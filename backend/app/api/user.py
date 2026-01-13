from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.deps import get_current_user_id
from app.schemas.user import UserUpdate
from app.schemas.common import ApiResponse
from app.models.user import User
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
