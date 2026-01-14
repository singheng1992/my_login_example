from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security.http import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import decode_access_token
from app.schemas.auth import (
    LoginRequest, EmailLoginRequest, SmsLoginRequest,
    SendCodeRequest, TokenResponse, RegisterRequest
)
from app.schemas.common import ApiResponse
from app.services.auth_service import auth_service
from app.services.email_service import email_service
from app.services.sms_service import sms_service
from app.services.oauth_service import oauth_service
from app.services.redis_service import redis_service
from app.models.user import User
from app.models.session import Session as SessionModel
from typing import Dict
from datetime import datetime, timedelta
from user_agents import parse as parse_user_agent

router = APIRouter()
security = HTTPBearer()


async def create_user_session(
    user: User,
    token: str,
    jti: str,
    request: Request,
    db: AsyncSession
):
    """创建用户登录会话记录"""
    # 获取客户端信息
    user_agent_str = request.headers.get("user-agent", "")
    user_agent = parse_user_agent(user_agent_str)

    # 解析设备信息
    device_info = f"{user_agent.os.family} {user_agent.os.version_string} - {user_agent.browser.family} {user_agent.browser.version_string}"

    # 获取 IP 地址
    ip_address = request.client.host if request.client else None

    # 计算 token 过期时间
    expires_at = datetime.utcnow() + timedelta(minutes=10080)  # 7天

    # 创建 session 记录
    session = SessionModel(
        user_id=user.id,
        token_jti=jti,
        device_info=device_info,
        ip_address=ip_address,
        user_agent=user_agent_str,
        expires_at=expires_at
    )
    db.add(session)
    await db.commit()


@router.post("/register", response_model=ApiResponse[Dict])
async def register(
    request_obj: RegisterRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    try:
        user = await auth_service.register(
            username=request_obj.username,
            email=request_obj.email,
            phone=request_obj.phone,
            password=request_obj.password,
            nickname=request_obj.nickname,
            db=db
        )
        token, jti = auth_service.create_token(str(user.id))

        # 保存 session
        await create_user_session(user, token, jti, request, db)

        return ApiResponse(
            data=TokenResponse(
                access_token=token,
                user={
                    "id": str(user.id),
                    "nickname": user.nickname,
                    "email": user.email,
                    "phone": user.phone
                }
            ).dict()
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login/password", response_model=ApiResponse[Dict])
async def login_password(
    request_obj: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    try:
        user = await auth_service.login_password(request_obj.username, request_obj.password, db)
        token, jti = auth_service.create_token(str(user.id))

        # 保存 session
        await create_user_session(user, token, jti, request, db)

        return ApiResponse(
            data=TokenResponse(
                access_token=token,
                user={
                    "id": str(user.id),
                    "nickname": user.nickname,
                    "email": user.email,
                    "phone": user.phone,
                    "avatar_url": user.avatar_url
                }
            ).dict()
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/login/email", response_model=ApiResponse[Dict])
async def login_email(
    request_obj: EmailLoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    try:
        user = await auth_service.login_email(request_obj.email, request_obj.code, db)
        token, jti = auth_service.create_token(str(user.id))

        # 保存 session
        await create_user_session(user, token, jti, request, db)

        return ApiResponse(
            data=TokenResponse(
                access_token=token,
                user={
                    "id": str(user.id),
                    "nickname": user.nickname,
                    "email": user.email,
                    "phone": user.phone,
                    "avatar_url": user.avatar_url
                }
            ).dict()
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/login/sms", response_model=ApiResponse[Dict])
async def login_sms(
    request_obj: SmsLoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    try:
        user = await auth_service.login_sms(request_obj.phone, request_obj.code, db)
        token, jti = auth_service.create_token(str(user.id))

        # 保存 session
        await create_user_session(user, token, jti, request, db)

        return ApiResponse(
            data=TokenResponse(
                access_token=token,
                user={
                    "id": str(user.id),
                    "nickname": user.nickname,
                    "email": user.email,
                    "phone": user.phone,
                    "avatar_url": user.avatar_url
                }
            ).dict()
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/send-email", response_model=ApiResponse[Dict])
async def send_email_code(
    request_obj: SendCodeRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        await email_service.send_verification_code(request_obj.identifier, db)
        return ApiResponse(message="验证码已发送到您的邮箱")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/send-sms", response_model=ApiResponse[Dict])
async def send_sms_code(
    request_obj: SendCodeRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        await sms_service.send_verification_code(request_obj.identifier, db)
        return ApiResponse(message="验证码已发送到您的手机")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/oauth/{provider}")
async def oauth_login(provider: str):
    try:
        redirect_uri = "http://localhost:8000/api/auth/oauth/" + provider + "/callback"
        state = "random_state_string"
        auth_url = oauth_service.get_authorization_url(provider, redirect_uri, state)
        return ApiResponse(data={"auth_url": auth_url})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/oauth/{provider}/callback", response_model=ApiResponse[Dict])
async def oauth_callback(
    provider: str,
    code: str,
    state: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    try:
        redirect_uri = "http://localhost:8000/api/auth/oauth/" + provider + "/callback"
        user_info = await oauth_service.get_user_info(provider, code, redirect_uri)
        user = await oauth_service.find_or_create_user(
            provider,
            user_info["provider_user_id"],
            user_info,
            db
        )
        token, jti = auth_service.create_token(str(user.id))

        # 保存 session
        await create_user_session(user, token, jti, request, db)

        return ApiResponse(
            data=TokenResponse(
                access_token=token,
                user={
                    "id": str(user.id),
                    "nickname": user.nickname,
                    "email": user.email,
                    "phone": user.phone,
                    "avatar_url": user.avatar_url
                }
            ).dict()
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/logout", response_model=ApiResponse[Dict])
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """退出登录，标记 session 为已撤销"""
    token = credentials.credentials

    # 解析 token 获取 jti
    payload = decode_access_token(token)
    if payload:
        jti = payload.get("jti")
        if jti:
            # 标记数据库中的 session 为已撤销
            result = await db.execute(
                select(SessionModel).where(
                    SessionModel.token_jti == jti,
                    SessionModel.is_revoked == False
                )
            )
            session = result.scalar_one_or_none()
            if session:
                session.is_revoked = True
                session.revoked_at = datetime.utcnow()
                await db.commit()

    return ApiResponse(message="登出成功")
