from pydantic import BaseModel, EmailStr
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
