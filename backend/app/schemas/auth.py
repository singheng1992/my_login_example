from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    username: str
    password: str


class EmailLoginRequest(BaseModel):
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6)


class SmsLoginRequest(BaseModel):
    phone: str = Field(..., pattern=r'^\d{11}$')
    code: str = Field(..., min_length=6, max_length=6)


class SendCodeRequest(BaseModel):
    identifier: str  # email or phone


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)
    nickname: str = Field(..., min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class OAuthCallbackRequest(BaseModel):
    code: str
    state: Optional[str] = None
