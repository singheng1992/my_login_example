from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.auth import (
    LoginRequest, EmailLoginRequest, SmsLoginRequest,
    SendCodeRequest, TokenResponse, RegisterRequest
)
from app.schemas.common import ApiResponse
from app.services.auth_service import auth_service
from app.services.email_service import email_service
from app.services.sms_service import sms_service
from app.services.oauth_service import oauth_service
from app.models.user import User
from typing import Dict

router = APIRouter()


@router.post("/register", response_model=ApiResponse[Dict])
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        user = await auth_service.register(
            username=request.username,
            email=request.email,
            phone=request.phone,
            password=request.password,
            nickname=request.nickname,
            db=db
        )
        token = auth_service.create_token(str(user.id))

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
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        user = await auth_service.login_password(request.username, request.password, db)
        token = auth_service.create_token(str(user.id))

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
    request: EmailLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        user = await auth_service.login_email(request.email, request.code, db)
        token = auth_service.create_token(str(user.id))

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
    request: SmsLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        user = await auth_service.login_sms(request.phone, request.code, db)
        token = auth_service.create_token(str(user.id))

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
    request: SendCodeRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        await email_service.send_verification_code(request.identifier, db)
        return ApiResponse(message="验证码已发送到您的邮箱")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/send-sms", response_model=ApiResponse[Dict])
async def send_sms_code(
    request: SendCodeRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        await sms_service.send_verification_code(request.identifier, db)
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
        token = auth_service.create_token(str(user.id))

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
async def logout():
    return ApiResponse(message="登出成功")
