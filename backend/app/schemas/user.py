from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from uuid import UUID


class UserBase(BaseModel):
    nickname: str


class UserCreate(UserBase):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str


class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None


class UpdateEmailRequest(BaseModel):
    """更新邮箱请求"""
    email: EmailStr = Field(..., description="新邮箱地址")
    code: str = Field(..., min_length=6, max_length=6, description="邮箱验证码")


class UserResponse(BaseModel):
    id: UUID
    username: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    nickname: str
    avatar_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
