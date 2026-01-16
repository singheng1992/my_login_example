import random
import string
from datetime import datetime, timedelta
from typing import Dict, Optional
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security.http import HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from user_agents import parse as parse_user_agent

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.session import Session as SessionModel
from app.models.user import User
from app.schemas.auth import (
    EmailLoginRequest,
    LoginRequest,
    RegisterRequest,
    SendCodeRequest,
    SmsLoginRequest,
    TokenResponse,
)
from app.schemas.common import ApiResponse
from app.services.auth_service import auth_service
from app.services.email_service import email_service
from app.services.oauth.oauth_service import oauth_service
from app.services.redis_service import redis_service
from app.services.sms_service import sms_service

router = APIRouter()
security = HTTPBearer()
settings = get_settings()


def generate_state(length: int = 32) -> str:
    """生成随机 state 字符串"""
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


async def create_user_session(
    user: User, token: str, jti: str, request: Request, db: AsyncSession
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
        expires_at=expires_at,
    )
    db.add(session)
    await db.commit()


@router.post("/register", response_model=ApiResponse[Dict])
async def register(
    request_obj: RegisterRequest, request: Request, db: AsyncSession = Depends(get_db)
):
    try:
        user = await auth_service.register(
            username=request_obj.username,
            email=request_obj.email,
            phone=request_obj.phone,
            password=request_obj.password,
            nickname=request_obj.nickname,
            db=db,
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
                },
            ).dict()
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login/password", response_model=ApiResponse[Dict])
async def login_password(
    request_obj: LoginRequest, request: Request, db: AsyncSession = Depends(get_db)
):
    try:
        user = await auth_service.login_password(
            request_obj.username, request_obj.password, db
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
                    "avatar_url": user.avatar_url,
                },
            ).dict()
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/login/email", response_model=ApiResponse[Dict])
async def login_email(
    request_obj: EmailLoginRequest, request: Request, db: AsyncSession = Depends(get_db)
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
                    "avatar_url": user.avatar_url,
                },
            ).dict()
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/login/sms", response_model=ApiResponse[Dict])
async def login_sms(
    request_obj: SmsLoginRequest, request: Request, db: AsyncSession = Depends(get_db)
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
                    "avatar_url": user.avatar_url,
                },
            ).dict()
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/send-email", response_model=ApiResponse[Dict])
async def send_email_code(
    request_obj: SendCodeRequest, db: AsyncSession = Depends(get_db)
):
    try:
        await email_service.send_verification_code(request_obj.identifier, db)
        return ApiResponse(message="验证码已发送到您的邮箱")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/send-sms", response_model=ApiResponse[Dict])
async def send_sms_code(
    request_obj: SendCodeRequest, db: AsyncSession = Depends(get_db)
):
    try:
        await sms_service.send_verification_code(request_obj.identifier, db)
        return ApiResponse(message="验证码已发送到您的手机")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/oauth/{provider}")
async def oauth_login(provider: str):
    """获取 OAuth 授权 URL"""
    try:
        # 生成随机 state（防止 CSRF 攻击）
        state = generate_state()

        # 存储 state 到 Redis（10分钟过期）
        state_key = f"oauth_state:{provider}:{state}"
        await redis_service.set(state_key, "1", expire=600)

        # 使用配置的基础 URL 构建 redirect_uri
        redirect_uri = f"{settings.SERVER_BASE_URL}/api/auth/oauth/{provider}/callback"
        auth_url = oauth_service.get_authorization_url(provider, redirect_uri, state)

        print(f"OAuth 授权: provider={provider}, state={state[:8]}...")

        return ApiResponse(data={"auth_url": auth_url, "state": state})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/oauth/{provider}/callback")
async def oauth_callback(
    provider: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    code: Optional[str] = Query(None, description="OAuth 授权码"),
    state: Optional[str] = Query(None, description="OAuth 状态参数"),
    error: Optional[str] = Query(None, description="OAuth 错误信息"),
    error_description: Optional[str] = Query(None, description="OAuth 错误描述"),
):
    """OAuth 回调处理

    处理 OAuth 回调，成功后重定向到前端并传递 token。
    """
    from fastapi.responses import RedirectResponse

    # 前端 URL（开发环境）
    frontend_url = settings.FRONTEND_URL

    # 检查是否有 OAuth 错误
    if error:
        error_msg = error_description or error
        print(f"OAuth 授权失败: provider={provider}, error={error_msg}")
        # 重定向到前端并传递错误信息
        error_param = urlencode({"error": error_msg})
        return RedirectResponse(url=f"{frontend_url}?{error_param}", status_code=302)

    # 检查是否有授权码
    if not code:
        error_param = urlencode({"error": "缺少授权码，请重新授权"})
        return RedirectResponse(url=f"{frontend_url}?{error_param}", status_code=302)

    # 验证 state 参数（防止 CSRF 攻击）
    if not state:
        error_param = urlencode({"error": "缺少state参数，请重新授权"})
        return RedirectResponse(url=f"{frontend_url}?{error_param}", status_code=302)

    state_key = f"oauth_state:{provider}:{state}"
    state_exists = await redis_service.exists(state_key)

    if not state_exists:
        print(f"OAuth state 验证失败: provider={provider}, state={state[:8]}...")
        error_param = urlencode({"error": "state参数无效或已过期"})
        return RedirectResponse(url=f"{frontend_url}?{error_param}", status_code=302)

    # 删除已使用的 state（一次性使用）
    await redis_service.delete(state_key)

    try:
        # 使用配置的基础 URL 构建 redirect_uri
        redirect_uri = f"{settings.SERVER_BASE_URL}/api/auth/oauth/{provider}/callback"

        # 记录调试信息
        print(
            f"OAuth 回调: provider={provider}, code={code[:10]}..., state={state[:8]}..."
        )
        # 获取用户信息
        user_info = await oauth_service.get_user_info(provider, code, redirect_uri)
        print(f"OAuth 用户信息: {user_info}")
        # 查找或创建用户
        user = await oauth_service.find_or_create_user(
            provider, user_info["provider_user_id"], user_info, db
        )
        token, jti = auth_service.create_token(str(user.id))

        # 保存 session
        await create_user_session(user, token, jti, request, db)

        print(f"OAuth 登录成功: provider={provider}, user={user.nickname}")

        # 重定向到前端并传递 token
        return RedirectResponse(url=f"{frontend_url}#token={token}", status_code=302)

    except ValueError as e:
        print(f"OAuth 登录失败: provider={provider}, error={str(e)}")
        # 重定向到前端并传递错误信息
        error_param = urlencode({"error": str(e)})
        return RedirectResponse(url=f"{frontend_url}?{error_param}", status_code=302)
    except Exception as e:
        print(f"OAuth 登录异常: provider={provider}, error={str(e)}")
        # 重定向到前端并传递错误信息
        error_param = urlencode({"error": "登录失败，请重试"})
        return RedirectResponse(url=f"{frontend_url}?{error_param}", status_code=302)


@router.post("/logout", response_model=ApiResponse[Dict])
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
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
                    SessionModel.token_jti == jti, SessionModel.is_revoked == False
                )
            )
            session = result.scalar_one_or_none()
            if session:
                session.is_revoked = True
                session.revoked_at = datetime.utcnow()
                await db.commit()

    return ApiResponse(message="登出成功")
