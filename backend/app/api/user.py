from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.core.database import get_db
from app.core.deps import get_current_user_id
from app.schemas.user import UserUpdate, UpdateEmailRequest
from app.schemas.common import ApiResponse
from app.models.user import User
from app.models.oauth_account import OAuthAccount
from app.services.email_service import email_service
from typing import Dict
import os
from datetime import datetime

router = APIRouter()


@router.get("/profile", response_model=ApiResponse[Dict])
async def get_profile(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User).where(User.id == user_id, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    return ApiResponse(
        data={
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "phone": user.phone,
            "nickname": user.nickname,
            "avatar_url": user.avatar_url,
            "created_at": user.created_at.isoformat()
        }
    )


@router.put("/profile", response_model=ApiResponse[Dict])
async def update_profile(
    request: UserUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User).where(User.id == user_id, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if request.nickname is not None:
        user.nickname = request.nickname
    if request.avatar_url is not None:
        user.avatar_url = request.avatar_url

    user.updated_at = datetime.utcnow()
    await db.commit()

    return ApiResponse(
        data={
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "phone": user.phone,
            "nickname": user.nickname,
            "avatar_url": user.avatar_url
        },
        message="个人信息更新成功"
    )


@router.put("/email", response_model=ApiResponse[Dict])
async def update_email(
    request: UpdateEmailRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """更新邮箱

    需要提供新邮箱地址和邮箱验证码。

    流程：
    1. 先调用 /api/auth/send-email 发送验证码到新邮箱
    2. 调用此接口更新邮箱

    特殊处理：如果邮箱已被其他账号使用，则自动关联两个账号
    """
    # 获取当前用户
    result = await db.execute(
        select(User).where(User.id == user_id, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 如果新邮箱与当前邮箱相同，直接返回
    if user.email == request.email:
        return ApiResponse(
            data={
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "phone": user.phone,
                "nickname": user.nickname,
                "avatar_url": user.avatar_url
            },
            message="邮箱未发生变化"
        )

    # 验证邮箱验证码
    is_valid = await email_service.verify_code(request.email, request.code, db)
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail="验证码无效或已过期，请重新获取"
        )

    # 检查新邮箱是否已被其他用户使用
    existing_result = await db.execute(
        select(User).where(
            User.email == request.email,
            User.id != user_id,
            User.is_deleted == False
        )
    )
    existing_user = existing_result.scalar_one_or_none()

    if existing_user:
        # 邮箱已被占用，关联两个账号
        # 1. 将当前用户的 OAuth 账号转移到目标用户
        await db.execute(
            update(OAuthAccount)
            .where(OAuthAccount.user_id == user_id, OAuthAccount.is_deleted == False)
            .values(user_id=existing_user.id)
        )

        # 2. 标记当前用户为已删除
        user.is_deleted = True
        user.updated_at = datetime.utcnow()

        # 3. 更新目标用户的更新时间
        existing_user.updated_at = datetime.utcnow()

        await db.commit()

        # 返回目标账号信息
        return ApiResponse(
            data={
                "id": str(existing_user.id),
                "username": existing_user.username,
                "email": existing_user.email,
                "phone": existing_user.phone,
                "nickname": existing_user.nickname,
                "avatar_url": existing_user.avatar_url
            },
            message="邮箱已绑定，账号已关联"
        )

    # 更新邮箱
    user.email = request.email
    user.updated_at = datetime.utcnow()
    await db.commit()

    return ApiResponse(
        data={
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "phone": user.phone,
            "nickname": user.nickname,
            "avatar_url": user.avatar_url
        },
        message="邮箱更新成功"
    )


@router.post("/avatar", response_model=ApiResponse[Dict])
async def upload_avatar(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="只支持上传图片")

    upload_dir = "backend/static/uploads/avatars"
    os.makedirs(upload_dir, exist_ok=True)

    filename = f"{user_id}_{int(datetime.utcnow().timestamp())}_{file.filename}"
    file_path = os.path.join(upload_dir, filename)

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    avatar_url = f"/static/uploads/avatars/{filename}"

    result = await db.execute(
        select(User).where(User.id == user_id, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()

    if user:
        user.avatar_url = avatar_url
        user.updated_at = datetime.utcnow()
        await db.commit()

    return ApiResponse(data={"avatar_url": avatar_url}, message="头像上传成功")
