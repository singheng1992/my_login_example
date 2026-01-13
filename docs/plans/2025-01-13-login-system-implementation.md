# 登录系统实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**目标:** 构建一个可用的前后端分离登录演示系统，支持账号密码、邮箱验证码、手机验证码和第三方登录

**架构:** 后端使用FastAPI + SQLAlchemy + PostgreSQL + Redis，前端使用原生HTML/CSS/JS，采用JWT认证

**技术栈:** Python 3.11+, FastAPI, PostgreSQL, Redis, SQLAlchemy, HTML5, CSS3, JavaScript

---

## 第一阶段：后端基础架构

### Task 1: 创建后端项目结构

**Files:**
- Create: `backend/app/__init__.py`
- Create: `backend/app/main.py`
- Create: `backend/app/core/__init__.py`
- Create: `backend/app/core/config.py`
- Create: `backend/app/core/security.py`
- Create: `backend/app/core/deps.py`
- Create: `backend/requirements.txt`
- Create: `backend/.env.example`

**Step 1: 创建核心配置文件**

创建 `backend/app/core/config.py`:

```python
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "Login Demo API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # 数据库配置
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/login_demo"

    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT配置
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7天

    # SMTP配置
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = ""

    # 短信配置 (阿里云)
    SMS_ACCESS_KEY: str = ""
    SMS_ACCESS_SECRET: str = ""
    SMS_SIGN_NAME: str = ""
    SMS_TEMPLATE_CODE: str = ""

    # OAuth配置
    OAUTH_GITHUB_CLIENT_ID: str = ""
    OAUTH_GITHUB_CLIENT_SECRET: str = ""
    OAUTH_GOOGLE_CLIENT_ID: str = ""
    OAUTH_GOOGLE_CLIENT_SECRET: str = ""
    OAUTH_WECHAT_APP_ID: str = ""
    OAUTH_WECHAT_APP_SECRET: str = ""
    OAUTH_DINGTALK_APP_ID: str = ""
    OAUTH_DINGTALK_APP_SECRET: str = ""
    OAUTH_FEISHU_APP_ID: str = ""
    OAUTH_FEISHU_APP_SECRET: str = ""

    # CORS配置
    CORS_ORIGINS: list[str] = ["http://localhost:8080", "http://127.0.0.1:8080"]

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

**Step 2: 创建JWT安全模块**

创建 `backend/app/core/security.py`:

```python
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from .config import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None
```

**Step 3: 创建依赖注入模块**

创建 `backend/app/core/deps.py`:

```python
from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from .security import decode_access_token
from .database import get_db

security = HTTPBearer()


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return user_id
```

**Step 4: 创建数据库连接模块**

创建 `backend/app/core/database.py`:

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()


async def get_db() -> AsyncGenerator:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

**Step 5: 创建主应用文件**

创建 `backend/app/main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.api import auth, user

settings = get_settings()

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(user.router, prefix="/api/user", tags=["user"])


@app.get("/")
async def root():
    return {"message": "Login Demo API", "version": settings.APP_VERSION}


@app.get("/health")
async def health():
    return {"status": "healthy"}
```

**Step 6: 创建依赖文件**

创建 `backend/requirements.txt`:

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
asyncpg==0.29.0
alembic==1.12.1
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
aiofiles==23.2.1
redis==5.0.1
aiosmtplib==3.0.1
httpx==0.25.2
```

**Step 7: 创建环境变量模板**

创建 `backend/.env.example`:

```ini
# 应用配置
APP_NAME=Login Demo API
DEBUG=true

# 数据库
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/login_demo

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production

# SMTP (邮箱验证码)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=your-email@gmail.com

# 短信 (阿里云)
SMS_ACCESS_KEY=your-access-key
SMS_ACCESS_SECRET=your-access-secret
SMS_SIGN_NAME=your-sign-name
SMS_TEMPLATE_CODE=your-template-code

# OAuth - GitHub
OAUTH_GITHUB_CLIENT_ID=your-github-client-id
OAUTH_GITHUB_CLIENT_SECRET=your-github-client-secret

# OAuth - Google
OAUTH_GOOGLE_CLIENT_ID=your-google-client-id
OAUTH_GOOGLE_CLIENT_SECRET=your-google-client-secret

# OAuth - 微信
OAUTH_WECHAT_APP_ID=your-wechat-app-id
OAUTH_WECHAT_APP_SECRET=your-wechat-app-secret

# OAuth - 钉钉
OAUTH_DINGTALK_APP_ID=your-dingtalk-app-id
OAUTH_DINGTALK_APP_SECRET=your-dingtalk-app-secret

# OAuth - 飞书
OAUTH_FEISHU_APP_ID=your-feishu-app-id
OAUTH_FEISHU_APP_SECRET=your-feishu-app-secret
```

**Step 8: 提交基础架构**

```bash
cd backend
git add app/ requirements.txt .env.example
git commit -m "feat: 添加后端基础架构

- 创建FastAPI应用结构
- 添加配置管理、JWT安全模块
- 添加数据库连接和依赖注入"
```

---

### Task 2: 创建数据库模型

**Files:**
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/models/user.py`
- Create: `backend/app/models/oauth_account.py`
- Create: `backend/app/models/verification_code.py`

**Step 1: 创建用户模型**

创建 `backend/app/models/user.py`:

```python
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=True, index=True)
    email = Column(String(255), unique=True, nullable=True, index=True)
    phone = Column(String(20), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=True)
    nickname = Column(String(100), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    is_deleted = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<User {self.nickname}>"
```

**Step 2: 创建OAuth账号模型**

创建 `backend/app/models/oauth_account.py`:

```python
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class OAuthAccount(Base):
    __tablename__ = "oauth_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    provider = Column(String(50), nullable=False, index=True)  # github, google, wechat, dingtalk, feishu
    provider_user_id = Column(String(255), nullable=False)
    access_token = Column(String(500), nullable=True)
    refresh_token = Column(String(500), nullable=True)
    is_deleted = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", backref="oauth_accounts")

    def __repr__(self):
        return f"<OAuthAccount {self.provider}:{self.provider_user_id}>"
```

**Step 3: 创建验证码模型**

创建 `backend/app/models/verification_code.py`:

```python
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class VerificationCode(Base):
    __tablename__ = "verification_codes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    identifier = Column(String(255), nullable=False, index=True)  # email or phone
    code = Column(String(10), nullable=False)
    code_type = Column(String(20), nullable=False)  # email, sms
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<VerificationCode {self.identifier}:{self.code}>"
```

**Step 4: 更新models初始化文件**

创建 `backend/app/models/__init__.py`:

```python
from app.models.user import User
from app.models.oauth_account import OAuthAccount
from app.models.verification_code import VerificationCode

__all__ = ["User", "OAuthAccount", "VerificationCode"]
```

**Step 5: 提交模型**

```bash
cd backend
git add app/models/
git commit -m "feat: 添加数据库模型

- User模型支持用户名/邮箱/手机登录
- OAuthAccount模型支持第三方登录绑定
- VerificationCode模型支持验证码存储
- 所有模型支持软删除"
```

---

### Task 3: 配置Alembic数据库迁移

**Files:**
- Create: `backend/alembic.ini`
- Create: `backend/alembic/env.py`
- Create: `backend/alembic/script.py.mako`

**Step 1: 初始化Alembic**

```bash
cd backend
alembic init alembic
```

**Step 2: 修改alembic配置**

编辑 `backend/alembic.ini`，修改sqlalchemy.url:

```ini
sqlalchemy.url = postgresql+asyncpg://postgres:postgres@localhost:5432/login_demo
```

**Step 3: 修改env.py支持异步**

编辑 `backend/alembic/env.py`:

```python
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

import sys
sys.path.insert(0, '/path/to/backend')

from app.core.config import get_settings
from app.models import Base

settings = get_settings()
config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

**Step 4: 修复env.py导入路径**

编辑 `backend/alembic/env.py` 开头:

```python
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.config import get_settings
from app.models import Base

# ... 其余代码保持不变
```

**Step 5: 创建初始迁移**

```bash
cd backend
alembic revision --autogenerate -m "Initial migration"
```

**Step 6: 提交迁移配置**

```bash
cd backend
git add alembic/
git commit -m "feat: 配置Alembic数据库迁移

- 初始化Alembic配置
- 支持异步迁移"
```

---

### Task 4: 创建Pydantic模式

**Files:**
- Create: `backend/app/schemas/__init__.py`
- Create: `backend/app/schemas/user.py`
- Create: `backend/app/schemas/auth.py`

**Step 1: 创建用户Schema**

创建 `backend/app/schemas/user.py`:

```python
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
```

**Step 2: 创建认证Schema**

创建 `backend/app/schemas/auth.py`:

```python
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
```

**Step 3: 创建通用响应Schema**

创建 `backend/app/schemas/common.py`:

```python
from pydantic import BaseModel, Generic, TypeVar
from typing import Optional, Any

T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    code: int = 0
    message: str = "success"
    data: Optional[T] = None


class ErrorResponse(BaseModel):
    code: int
    message: str
    detail: Optional[str] = None
```

**Step 4: 更新schemas初始化文件**

创建 `backend/app/schemas/__init__.py`:

```python
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas.auth import (
    LoginRequest, EmailLoginRequest, SmsLoginRequest,
    SendCodeRequest, TokenResponse, RegisterRequest
)
from app.schemas.common import ApiResponse, ErrorResponse

__all__ = [
    "UserCreate", "UserUpdate", "UserResponse",
    "LoginRequest", "EmailLoginRequest", "SmsLoginRequest",
    "SendCodeRequest", "TokenResponse", "RegisterRequest",
    "ApiResponse", "ErrorResponse"
]
```

**Step 5: 提交Schema**

```bash
cd backend
git add app/schemas/
git commit -m "feat: 添加Pydantic验证模式

- 用户创建、更新、响应Schema
- 认证请求Schema（密码/邮箱/短信登录）
- 通用API响应格式"
```

---

## 第二阶段：核心服务层

### Task 5: 创建Redis缓存服务

**Files:**
- Create: `backend/app/services/__init__.py`
- Create: `backend/app/services/redis_service.py`

**Step 1: 创建Redis服务**

创建 `backend/app/services/redis_service.py`:

```python
import json
from typing import Optional, Any
from redis import asyncio as aioredis
from app.core.config import get_settings

settings = get_settings()


class RedisService:
    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None

    async def connect(self):
        self.redis = await aioredis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)

    async def disconnect(self):
        if self.redis:
            await self.redis.close()

    async def set(self, key: str, value: Any, expire: int = 300):
        if not self.redis:
            await self.connect()
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        await self.redis.set(key, value, ex=expire)

    async def get(self, key: str) -> Optional[str]:
        if not self.redis:
            await self.connect()
        return await self.redis.get(key)

    async def delete(self, key: str):
        if not self.redis:
            await self.connect()
        await self.redis.delete(key)

    async def exists(self, key: str) -> bool:
        if not self.redis:
            await self.connect()
        return await self.redis.exists(key) > 0


redis_service = RedisService()
```

**Step 2: 提交Redis服务**

```bash
cd backend
git add app/services/redis_service.py
git commit -m "feat: 添加Redis缓存服务"
```

---

### Task 6: 创建邮箱验证码服务

**Files:**
- Create: `backend/app/services/email_service.py`

**Step 1: 创建邮箱服务**

创建 `backend/app/services/email_service.py`:

```python
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.verification_code import VerificationCode
from app.core.config import get_settings
from app.services.redis_service import redis_service

settings = get_settings()


class EmailService:
    async def send_verification_code(self, email: str, db: AsyncSession) -> bool:
        # 检查发送频率限制 (60秒)
        cache_key = f"email_code_limit:{email}"
        if await redis_service.exists(cache_key):
            raise ValueError("验证码发送过于频繁，请60秒后再试")

        # 生成6位验证码
        code = str(random.randint(100000, 999999))
        expires_at = datetime.utcnow() + timedelta(minutes=5)

        # 保存到数据库
        verification_code = VerificationCode(
            identifier=email,
            code=code,
            code_type="email",
            expires_at=expires_at
        )
        db.add(verification_code)
        await db.commit()

        # 发送邮件
        try:
            await self._send_email(email, code)
            # 设置发送限制
            await redis_service.set(cache_key, "1", expire=60)
            return True
        except Exception as e:
            await db.rollback()
            raise e

    async def _send_email(self, to_email: str, code: str):
        message = MIMEMultipart()
        message["From"] = settings.SMTP_FROM
        message["To"] = to_email
        message["Subject"] = "登录验证码"

        body = f"""
        <html>
        <body>
            <h2>您的登录验证码是：</h2>
            <h1 style="color: #4CAF50;">{code}</h1>
            <p>验证码有效期为5分钟，请尽快使用。</p>
            <p>如果这不是您的操作，请忽略此邮件。</p>
        </body>
        </html>
        """

        message.attach(MIMEText(body, "html"))

        async with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            await server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            await server.send_message(message)

    async def verify_code(self, email: str, code: str, db: AsyncSession) -> bool:
        result = await db.execute(
            select(VerificationCode).where(
                VerificationCode.identifier == email,
                VerificationCode.code == code,
                VerificationCode.code_type == "email",
                VerificationCode.used == False,
                VerificationCode.is_deleted == False
            )
        )
        verification_code = result.scalar_one_or_none()

        if not verification_code:
            return False

        if verification_code.expires_at < datetime.utcnow():
            return False

        # 标记为已使用
        verification_code.used = True
        await db.commit()

        return True


email_service = EmailService()
```

**Step 2: 提交邮箱服务**

```bash
cd backend
git add app/services/email_service.py
git commit -m "feat: 添加邮箱验证码服务

- 支持发送6位数字验证码
- 验证码5分钟有效期
- 60秒发送频率限制"
```

---

### Task 7: 创建短信验证码服务

**Files:**
- Create: `backend/app/services/sms_service.py`

**Step 1: 创建短信服务**

创建 `backend/app/services/sms_service.py`:

```python
import random
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.verification_code import VerificationCode
from app.services.redis_service import redis_service
from alibabacloud_dysmsapi20170525.client import Client as DysmsClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_dysmsapi20170525 import models as dysms_models
from app.core.config import get_settings

settings = get_settings()


class SmsService:
    def __init__(self):
        self.client = None

    def _get_client(self) -> DysmsClient:
        if self.client:
            return self.client

        config = open_api_models.Config(
            access_key_id=settings.SMS_ACCESS_KEY,
            access_key_secret=settings.SMS_ACCESS_SECRET
        )
        config.endpoint = f'dysmsapi.aliyuncs.com'
        self.client = DysmsClient(config)
        return self.client

    async def send_verification_code(self, phone: str, db: AsyncSession) -> bool:
        # 检查发送频率限制
        cache_key = f"sms_code_limit:{phone}"
        if await redis_service.exists(cache_key):
            raise ValueError("验证码发送过于频繁，请60秒后再试")

        # 生成验证码
        code = str(random.randint(100000, 999999))
        expires_at = datetime.utcnow() + timedelta(minutes=5)

        # 保存到数据库
        verification_code = VerificationCode(
            identifier=phone,
            code=code,
            code_type="sms",
            expires_at=expires_at
        )
        db.add(verification_code)
        await db.commit()

        # 发送短信
        try:
            await self._send_sms(phone, code)
            await redis_service.set(cache_key, "1", expire=60)
            return True
        except Exception as e:
            await db.rollback()
            raise e

    async def _send_sms(self, phone: str, code: str):
        client = self._get_client()

        request = dysms_models.SendSmsRequest(
            sign_name=settings.SMS_SIGN_NAME,
            template_code=settings.SMS_TEMPLATE_CODE,
            phone_numbers=phone,
            template_param=f'{{"code":"{code}"}}'
        )

        await client.send_sms(request)

    async def verify_code(self, phone: str, code: str, db: AsyncSession) -> bool:
        result = await db.execute(
            select(VerificationCode).where(
                VerificationCode.identifier == phone,
                VerificationCode.code == code,
                VerificationCode.code_type == "sms",
                VerificationCode.used == False,
                VerificationCode.is_deleted == False
            )
        )
        verification_code = result.scalar_one_or_none()

        if not verification_code:
            return False

        if verification_code.expires_at < datetime.utcnow():
            return False

        verification_code.used = True
        await db.commit()

        return True


sms_service = SmsService()
```

**Step 2: 更新requirements.txt添加阿里云SDK**

编辑 `backend/requirements.txt`，添加:

```txt
alibabacloud-dysmsapi20170525==3.0.0
alibabacloud-tea-openapi==0.3.9
```

**Step 3: 提交短信服务**

```bash
cd backend
git add app/services/sms_service.py requirements.txt
git commit -m "feat: 添加短信验证码服务

- 集成阿里云短信服务
- 支持6位数字验证码发送
- 60秒发送频率限制"
```

---

### Task 8: 创建OAuth服务

**Files:**
- Create: `backend/app/services/oauth_service.py`

**Step 1: 创建OAuth服务**

创建 `backend/app/services/oauth_service.py`:

```python
import httpx
from typing import Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.models.oauth_account import OAuthAccount
from app.core.config import get_settings

settings = get_settings()


class OAuthProvider:
    GITHUB = "github"
    GOOGLE = "google"
    WECHAT = "wechat"
    DINGTALK = "dingtalk"
    FEISHU = "feishu"


class OAuthService:
    def __init__(self):
        self.providers = {
            OAuthProvider.GITHUB: {
                "auth_url": "https://github.com/login/oauth/authorize",
                "token_url": "https://github.com/login/oauth/access_token",
                "user_url": "https://api.github.com/user",
                "client_id": settings.OAUTH_GITHUB_CLIENT_ID,
                "client_secret": settings.OAUTH_GITHUB_CLIENT_SECRET,
                "scope": "user:email"
            },
            OAuthProvider.GOOGLE: {
                "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
                "token_url": "https://oauth2.googleapis.com/token",
                "user_url": "https://www.googleapis.com/oauth2/v2/userinfo",
                "client_id": settings.OAUTH_GOOGLE_CLIENT_ID,
                "client_secret": settings.OAUTH_GOOGLE_CLIENT_SECRET,
                "scope": "openid email profile"
            }
        }

    def get_authorization_url(self, provider: str, redirect_uri: str, state: str) -> str:
        config = self.providers.get(provider)
        if not config:
            raise ValueError(f"Unsupported provider: {provider}")

        if provider == OAuthProvider.GITHUB:
            return f"{config['auth_url']}?client_id={config['client_id']}&redirect_uri={redirect_uri}&scope={config['scope']}&state={state}"
        elif provider == OAuthProvider.GOOGLE:
            return f"{config['auth_url']}?client_id={config['client_id']}&redirect_uri={redirect_uri}&scope={config['scope']}&response_type=code&state={state}"

        raise ValueError(f"Unsupported provider: {provider}")

    async def get_user_info(self, provider: str, code: str, redirect_uri: str) -> Dict:
        config = self.providers.get(provider)
        if not config:
            raise ValueError(f"Unsupported provider: {provider}")

        # 获取access_token
        async with httpx.AsyncClient() as client:
            if provider == OAuthProvider.GITHUB:
                token_response = await client.post(
                    config["token_url"],
                    data={
                        "client_id": config["client_id"],
                        "client_secret": config["client_secret"],
                        "code": code
                    },
                    headers={"Accept": "application/json"}
                )
                token_data = token_response.json()

                if "error" in token_data:
                    raise ValueError(token_data.get("error_description", "Failed to get access token"))

                access_token = token_data["access_token"]

                # 获取用户信息
                user_response = await client.get(
                    config["user_url"],
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                user_data = user_response.json()

                return {
                    "provider_user_id": str(user_data["id"]),
                    "email": user_data.get("email"),
                    "name": user_data.get("name") or user_data.get("login"),
                    "avatar_url": user_data.get("avatar_url")
                }

            elif provider == OAuthProvider.GOOGLE:
                token_response = await client.post(
                    config["token_url"],
                    data={
                        "client_id": config["client_id"],
                        "client_secret": config["client_secret"],
                        "code": code,
                        "grant_type": "authorization_code",
                        "redirect_uri": redirect_uri
                    }
                )
                token_data = token_response.json()

                if "error" in token_data:
                    raise ValueError(token_data.get("error_description", "Failed to get access token"))

                access_token = token_data["access_token"]

                # 获取用户信息
                user_response = await client.get(
                    config["user_url"],
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                user_data = user_response.json()

                return {
                    "provider_user_id": user_data["id"],
                    "email": user_data.get("email"),
                    "name": user_data.get("name"),
                    "avatar_url": user_data.get("picture")
                }

        raise ValueError(f"Unsupported provider: {provider}")

    async def find_or_create_user(self, provider: str, provider_user_id: str, user_info: Dict, db: AsyncSession) -> User:
        # 查找已存在的OAuth账号
        result = await db.execute(
            select(OAuthAccount).where(
                OAuthAccount.provider == provider,
                OAuthAccount.provider_user_id == provider_user_id,
                OAuthAccount.is_deleted == False
            )
        )
        oauth_account = result.scalar_one_or_none()

        if oauth_account:
            # 返回关联的用户
            user_result = await db.execute(
                select(User).where(User.id == oauth_account.user_id, User.is_deleted == False)
            )
            return user_result.scalar_one()

        # 创建新用户
        user = User(
            nickname=user_info.get("name", "Unknown"),
            email=user_info.get("email"),
            avatar_url=user_info.get("avatar_url")
        )
        db.add(user)
        await db.flush()

        # 创建OAuth账号关联
        oauth_account = OAuthAccount(
            user_id=user.id,
            provider=provider,
            provider_user_id=provider_user_id
        )
        db.add(oauth_account)
        await db.commit()

        return user


oauth_service = OAuthService()
```

**Step 2: 提交OAuth服务**

```bash
cd backend
git add app/services/oauth_service.py
git commit -m "feat: 添加OAuth第三方登录服务

- 支持GitHub和Google登录
- 自动创建用户账号
- OAuth账号绑定"
```

---

### Task 9: 创建认证服务

**Files:**
- Create: `backend/app/services/auth_service.py`

**Step 1: 创建认证服务**

创建 `backend/app/services/auth_service.py`:

```python
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import get_settings

settings = get_settings()


class AuthService:
    async def register(
        self,
        username: Optional[str],
        email: Optional[str],
        phone: Optional[str],
        password: str,
        nickname: str,
        db: AsyncSession
    ) -> User:
        # 检查用户名是否已存在
        if username:
            result = await db.execute(
                select(User).where(User.username == username, User.is_deleted == False)
            )
            if result.scalar_one_or_none():
                raise ValueError("用户名已存在")

        # 检查邮箱是否已存在
        if email:
            result = await db.execute(
                select(User).where(User.email == email, User.is_deleted == False)
            )
            if result.scalar_one_or_none():
                raise ValueError("邮箱已被注册")

        # 检查手机号是否已存在
        if phone:
            result = await db.execute(
                select(User).where(User.phone == phone, User.is_deleted == False)
            )
            if result.scalar_one_or_none():
                raise ValueError("手机号已被注册")

        # 创建用户
        user = User(
            username=username,
            email=email,
            phone=phone,
            password_hash=get_password_hash(password),
            nickname=nickname
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        return user

    async def login_password(self, username: str, password: str, db: AsyncSession) -> User:
        # 支持用户名或邮箱登录
        result = await db.execute(
            select(User).where(
                (User.username == username) | (User.email == username),
                User.is_deleted == False
            )
        )
        user = result.scalar_one_or_none()

        if not user or not user.password_hash:
            raise ValueError("用户名或密码错误")

        if not verify_password(password, user.password_hash):
            raise ValueError("用户名或密码错误")

        return user

    async def login_email(self, email: str, code: str, db: AsyncSession) -> User:
        from app.services.email_service import email_service

        # 验证验证码
        if not await email_service.verify_code(email, code, db):
            raise ValueError("验证码错误或已过期")

        # 查找或创建用户
        result = await db.execute(
            select(User).where(User.email == email, User.is_deleted == False)
        )
        user = result.scalar_one_or_none()

        if not user:
            # 自动创建用户
            user = User(
                email=email,
                nickname=email.split("@")[0]
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)

        return user

    async def login_sms(self, phone: str, code: str, db: AsyncSession) -> User:
        from app.services.sms_service import sms_service

        # 验证验证码
        if not await sms_service.verify_code(phone, code, db):
            raise ValueError("验证码错误或已过期")

        # 查找或创建用户
        result = await db.execute(
            select(User).where(User.phone == phone, User.is_deleted == False)
        )
        user = result.scalar_one_or_none()

        if not user:
            # 自动创建用户
            user = User(
                phone=phone,
                nickname=phone
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)

        return user

    def create_token(self, user_id: str) -> str:
        return create_access_token(data={"sub": user_id})


auth_service = AuthService()
```

**Step 2: 提交认证服务**

```bash
cd backend
git add app/services/auth_service.py
git commit -m "feat: 添加认证服务

- 支持用户注册
- 支持账号密码登录
- 支持邮箱验证码登录
- 支持手机验证码登录
- 自动创建用户（邮箱/手机登录时）"
```

---

## 第三阶段：API接口

### Task 10: 创建认证API路由

**Files:**
- Create: `backend/app/api/__init__.py`
- Create: `backend/app/api/auth.py`

**Step 1: 创建认证API**

创建 `backend/app/api/auth.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_user_id
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
        state = "random_state_string"  # 实际应用中应生成随机state并验证
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
```

**Step 2: 提交认证API**

```bash
cd backend
git add app/api/auth.py
git commit -m "feat: 添加认证API路由

- POST /api/auth/register - 用户注册
- POST /api/auth/login/password - 账号密码登录
- POST /api/auth/login/email - 邮箱验证码登录
- POST /api/auth/login/sms - 手机验证码登录
- POST /api/auth/send-email - 发送邮箱验证码
- POST /api/auth/send-sms - 发送短信验证码
- GET /api/auth/oauth/{provider} - OAuth登录
- GET /api/auth/oauth/{provider}/callback - OAuth回调
- POST /api/auth/logout - 登出"
```

---

### Task 11: 创建用户API路由

**Files:**
- Create: `backend/app/api/user.py`

**Step 1: 创建用户API**

创建 `backend/app/api/user.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.deps import get_current_user_id
from app.schemas.user import UserResponse, UserUpdate
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
    # 验证文件类型
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="只支持上传图片")

    # 保存文件
    upload_dir = "backend/static/uploads/avatars"
    os.makedirs(upload_dir, exist_ok=True)

    filename = f"{user_id}_{int(datetime.utcnow().timestamp())}_{file.filename}"
    file_path = os.path.join(upload_dir, filename)

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    avatar_url = f"/static/uploads/avatars/{filename}"

    # 更新用户头像
    result = await db.execute(
        select(User).where(User.id == user_id, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()

    if user:
        user.avatar_url = avatar_url
        user.updated_at = datetime.utcnow()
        await db.commit()

    return ApiResponse(data={"avatar_url": avatar_url}, message="头像上传成功")
```

**Step 2: 提交用户API**

```bash
cd backend
git add app/api/user.py
git commit -m "feat: 添加用户API路由

- GET /api/user/profile - 获取个人信息
- PUT /api/user/profile - 更新个人信息
- POST /api/user/avatar - 上传头像"
```

---

### Task 12: 修复导入问题

**Files:**
- Modify: `backend/app/core/database.py`
- Modify: `backend/app/models/oauth_account.py`
- Modify: `backend/app/services/email_service.py`

**Step 1: 修复database.py导入**

编辑 `backend/app/core/database.py`，确保正确导入:

```python
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()


async def get_db() -> AsyncGenerator:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

**Step 2: 修复oauth_account.py**

编辑 `backend/app/models/oauth_account.py`:

```python
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class OAuthAccount(Base):
    __tablename__ = "oauth_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    provider = Column(String(50), nullable=False, index=True)
    provider_user_id = Column(String(255), nullable=False)
    access_token = Column(String(500), nullable=True)
    refresh_token = Column(String(500), nullable=True)
    is_deleted = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", backref="oauth_accounts")

    def __repr__(self):
        return f"<OAuthAccount {self.provider}:{self.provider_user_id}>"
```

**Step 3: 修复email_service.py使用同步SMTP**

编辑 `backend/app/services/email_service.py`:

```python
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.verification_code import VerificationCode
from app.core.config import get_settings
from app.services.redis_service import redis_service

settings = get_settings()


class EmailService:
    async def send_verification_code(self, email: str, db: AsyncSession) -> bool:
        # 检查发送频率限制 (60秒)
        cache_key = f"email_code_limit:{email}"
        if await redis_service.exists(cache_key):
            raise ValueError("验证码发送过于频繁，请60秒后再试")

        # 生成6位验证码
        code = str(random.randint(100000, 999999))
        expires_at = datetime.utcnow() + timedelta(minutes=5)

        # 保存到数据库
        verification_code = VerificationCode(
            identifier=email,
            code=code,
            code_type="email",
            expires_at=expires_at
        )
        db.add(verification_code)
        await db.commit()

        # 发送邮件
        try:
            self._send_email(email, code)
            # 设置发送限制
            await redis_service.set(cache_key, "1", expire=60)
            return True
        except Exception as e:
            await db.rollback()
            raise e

    def _send_email(self, to_email: str, code: str):
        message = MIMEMultipart()
        message["From"] = settings.SMTP_FROM
        message["To"] = to_email
        message["Subject"] = "登录验证码"

        body = f"""
        <html>
        <body>
            <h2>您的登录验证码是：</h2>
            <h1 style="color: #4CAF50;">{code}</h1>
            <p>验证码有效期为5分钟，请尽快使用。</p>
            <p>如果这不是您的操作，请忽略此邮件。</p>
        </body>
        </html>
        """

        message.attach(MIMEText(body, "html"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(message)

    async def verify_code(self, email: str, code: str, db: AsyncSession) -> bool:
        result = await db.execute(
            select(VerificationCode).where(
                VerificationCode.identifier == email,
                VerificationCode.code == code,
                VerificationCode.code_type == "email",
                VerificationCode.used == False,
                VerificationCode.is_deleted == False
            )
        )
        verification_code = result.scalar_one_or_none()

        if not verification_code:
            return False

        if verification_code.expires_at < datetime.utcnow():
            return False

        # 标记为已使用
        verification_code.used = True
        await db.commit()

        return True


email_service = EmailService()
```

**Step 4: 提交修复**

```bash
cd backend
git add app/core/database.py app/models/oauth_account.py app/services/email_service.py
git commit -m "fix: 修复导入问题和同步SMTP调用"
```

---

## 第四阶段：前端实现

### Task 13: 创建前端基础结构

**Files:**
- Create: `frontend/static/css/style.css`
- Create: `frontend/static/js/config.js`
- Create: `frontend/static/js/utils.js`
- Create: `frontend/templates/login.html`
- Create: `frontend/templates/register.html`
- Create: `frontend/templates/profile.html`

**Step 1: 创建CSS样式**

创建 `frontend/static/css/style.css`:

```css
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
}

.container {
    width: 100%;
    max-width: 420px;
    background: white;
    border-radius: 12px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
    padding: 40px;
    margin: 20px;
}

.logo {
    text-align: center;
    margin-bottom: 30px;
}

.logo h1 {
    color: #333;
    font-size: 28px;
    margin-bottom: 8px;
}

.logo p {
    color: #666;
    font-size: 14px;
}

.tabs {
    display: flex;
    border-bottom: 1px solid #e5e7eb;
    margin-bottom: 30px;
}

.tab {
    flex: 1;
    padding: 12px;
    text-align: center;
    cursor: pointer;
    color: #666;
    border-bottom: 2px solid transparent;
    transition: all 0.3s;
}

.tab:hover {
    color: #667eea;
}

.tab.active {
    color: #667eea;
    border-bottom-color: #667eea;
}

.tab-content {
    display: none;
}

.tab-content.active {
    display: block;
}

.form-group {
    margin-bottom: 20px;
}

.form-group label {
    display: block;
    margin-bottom: 8px;
    color: #333;
    font-weight: 500;
}

.form-group input {
    width: 100%;
    padding: 12px 16px;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    font-size: 14px;
    transition: border-color 0.3s;
}

.form-group input:focus {
    outline: none;
    border-color: #667eea;
}

.btn {
    width: 100%;
    padding: 14px;
    border: none;
    border-radius: 8px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s;
}

.btn-primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}

.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
    background: #f3f4f6;
    color: #666;
}

.btn-secondary:hover {
    background: #e5e7eb;
}

.btn-code {
    display: flex;
    gap: 10px;
}

.btn-code input {
    flex: 1;
}

.btn-code button {
    width: auto;
    padding: 12px 20px;
    white-space: nowrap;
}

.btn-code button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.oauth-buttons {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-top: 20px;
}

.oauth-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    padding: 12px;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    background: white;
    cursor: pointer;
    transition: all 0.3s;
}

.oauth-btn:hover {
    background: #f9fafb;
    border-color: #667eea;
}

.oauth-btn img {
    width: 20px;
    height: 20px;
}

.divider {
    display: flex;
    align-items: center;
    margin: 24px 0;
}

.divider::before,
.divider::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #e5e7eb;
}

.divider span {
    padding: 0 16px;
    color: #999;
    font-size: 14px;
}

.alert {
    padding: 12px;
    border-radius: 8px;
    margin-bottom: 20px;
    font-size: 14px;
}

.alert-error {
    background: #fee;
    color: #c33;
    border: 1px solid #fcc;
}

.alert-success {
    background: #efe;
    color: #3c3;
    border: 1px solid #cfc;
}

.alert.hidden {
    display: none;
}

.profile-header {
    text-align: center;
    margin-bottom: 30px;
}

.avatar {
    width: 100px;
    height: 100px;
    border-radius: 50%;
    margin: 0 auto 16px;
    overflow: hidden;
}

.avatar img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.info-item {
    display: flex;
    padding: 16px 0;
    border-bottom: 1px solid #e5e7eb;
}

.info-item label {
    flex: 0 0 100px;
    color: #666;
    font-size: 14px;
}

.info-item span {
    flex: 1;
    color: #333;
}

.logout-btn {
    margin-top: 24px;
    background: #ef4444;
}

.logout-btn:hover {
    background: #dc2626;
}

.links {
    text-align: center;
    margin-top: 20px;
}

.links a {
    color: #667eea;
    text-decoration: none;
    font-size: 14px;
}

.links a:hover {
    text-decoration: underline;
}
```

**Step 2: 创建配置文件**

创建 `frontend/static/js/config.js`:

```javascript
const API_BASE_URL = 'http://localhost:8000';

const config = {
    apiBaseUrl: API_BASE_URL,
    oauthProviders: {
        github: `${API_BASE_URL}/api/auth/oauth/github`,
        google: `${API_BASE_URL}/api/auth/oauth/google`,
        wechat: `${API_BASE_URL}/api/auth/oauth/wechat`,
        dingtalk: `${API_BASE_URL}/api/auth/oauth/dingtalk`,
        feishu: `${API_BASE_URL}/api/auth/oauth/feishu`
    }
};
```

**Step 3: 创建工具函数**

创建 `frontend/static/js/utils.js`:

```javascript
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

function setCookie(name, value, days) {
    const date = new Date();
    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
    document.cookie = `${name}=${value};expires=${date.toUTCString()};path=/`;
}

function deleteCookie(name) {
    document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/`;
}

function showAlert(message, type = 'error') {
    const alertDiv = document.getElementById('alert');
    if (alertDiv) {
        alertDiv.textContent = message;
        alertDiv.className = `alert alert-${type}`;
        alertDiv.classList.remove('hidden');
        setTimeout(() => {
            alertDiv.classList.add('hidden');
        }, 5000);
    }
}

function getHeaders() {
    const token = localStorage.getItem('access_token');
    return {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` })
    };
}

function handleResponse(response) {
    if (!response.ok) {
        return response.json().then(data => {
            throw new Error(data.detail || data.message || '请求失败');
        });
    }
    return response.json();
}

function saveToken(token) {
    localStorage.setItem('access_token', token);
}

function clearToken() {
    localStorage.removeItem('access_token');
}

function isLoggedIn() {
    return !!localStorage.getItem('access_token');
}

function redirectTo(path) {
    window.location.href = path;
}
```

**Step 4: 提交前端基础结构**

```bash
cd frontend
git add static/css/ static/js/
git commit -m "feat: 添加前端基础结构

- 创建响应式CSS样式
- 添加API配置和工具函数
- 支持JWT Token管理"
```

---

### Task 14: 创建登录页面

**Files:**
- Create: `frontend/templates/login.html`
- Create: `frontend/static/js/login.js`

**Step 1: 创建登录HTML**

创建 `frontend/templates/login.html`:

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>登录 - Login Demo</title>
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <div class="container">
        <div class="logo">
            <h1>欢迎回来</h1>
            <p>登录您的账户</p>
        </div>

        <div id="alert" class="alert hidden"></div>

        <div class="tabs">
            <div class="tab active" data-tab="password">密码登录</div>
            <div class="tab" data-tab="email">邮箱登录</div>
            <div class="tab" data-tab="sms">短信登录</div>
        </div>

        <!-- 密码登录 -->
        <div class="tab-content active" id="password-content">
            <form id="password-form">
                <div class="form-group">
                    <label>用户名/邮箱</label>
                    <input type="text" id="password-username" required>
                </div>
                <div class="form-group">
                    <label>密码</label>
                    <input type="password" id="password-password" required>
                </div>
                <button type="submit" class="btn btn-primary">登录</button>
            </form>
        </div>

        <!-- 邮箱登录 -->
        <div class="tab-content" id="email-content">
            <form id="email-form">
                <div class="form-group">
                    <label>邮箱</label>
                    <input type="email" id="email-email" required>
                </div>
                <div class="form-group btn-code">
                    <input type="text" id="email-code" placeholder="6位验证码" maxlength="6" required>
                    <button type="button" id="send-email-btn" class="btn btn-secondary">发送验证码</button>
                </div>
                <button type="submit" class="btn btn-primary">登录</button>
            </form>
        </div>

        <!-- 短信登录 -->
        <div class="tab-content" id="sms-content">
            <form id="sms-form">
                <div class="form-group">
                    <label>手机号</label>
                    <input type="tel" id="sms-phone" placeholder="11位手机号" maxlength="11" required>
                </div>
                <div class="form-group btn-code">
                    <input type="text" id="sms-code" placeholder="6位验证码" maxlength="6" required>
                    <button type="button" id="send-sms-btn" class="btn btn-secondary">发送验证码</button>
                </div>
                <button type="submit" class="btn btn-primary">登录</button>
            </form>
        </div>

        <div class="divider">
            <span>或</span>
        </div>

        <div class="oauth-buttons">
            <button class="oauth-btn" data-provider="github">
                <span>GitHub 登录</span>
            </button>
            <button class="oauth-btn" data-provider="google">
                <span>Google 登录</span>
            </button>
            <button class="oauth-btn" data-provider="wechat">
                <span>微信登录</span>
            </button>
            <button class="oauth-btn" data-provider="dingtalk">
                <span>钉钉登录</span>
            </button>
            <button class="oauth-btn" data-provider="feishu">
                <span>飞书登录</span>
            </button>
        </div>

        <div class="links">
            <p>还没有账户？ <a href="/register.html">立即注册</a></p>
        </div>
    </div>

    <script src="/static/js/config.js"></script>
    <script src="/static/js/utils.js"></script>
    <script src="/static/js/login.js"></script>
</body>
</html>
```

**Step 2: 创建登录JS**

创建 `frontend/static/js/login.js`:

```javascript
// 检查是否已登录
if (isLoggedIn()) {
    redirectTo('/profile.html');
}

// 标签切换
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', function() {
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

        this.classList.add('active');
        const tabName = this.dataset.tab;
        document.getElementById(`${tabName}-content`).classList.add('active');
    });
});

// 密码登录
document.getElementById('password-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('password-username').value;
    const password = document.getElementById('password-password').value;

    try {
        const response = await fetch(`${config.apiBaseUrl}/api/auth/login/password`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const data = await handleResponse(response);
        saveToken(data.data.access_token);
        showAlert('登录成功！', 'success');
        setTimeout(() => redirectTo('/profile.html'), 1000);
    } catch (error) {
        showAlert(error.message);
    }
});

// 发送邮箱验证码
document.getElementById('send-email-btn').addEventListener('click', async function() {
    const email = document.getElementById('email-email').value;
    if (!email) {
        showAlert('请输入邮箱');
        return;
    }

    try {
        const response = await fetch(`${config.apiBaseUrl}/api/auth/send-email`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ identifier: email })
        });

        const data = await handleResponse(response);
        showAlert(data.message || '验证码已发送', 'success');

        // 倒计时
        let countdown = 60;
        this.disabled = true;
        const timer = setInterval(() => {
            this.textContent = `${countdown}s`;
            countdown--;
            if (countdown < 0) {
                clearInterval(timer);
                this.disabled = false;
                this.textContent = '发送验证码';
            }
        }, 1000);
    } catch (error) {
        showAlert(error.message);
    }
});

// 邮箱登录
document.getElementById('email-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('email-email').value;
    const code = document.getElementById('email-code').value;

    try {
        const response = await fetch(`${config.apiBaseUrl}/api/auth/login/email`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, code })
        });

        const data = await handleResponse(response);
        saveToken(data.data.access_token);
        showAlert('登录成功！', 'success');
        setTimeout(() => redirectTo('/profile.html'), 1000);
    } catch (error) {
        showAlert(error.message);
    }
});

// 发送短信验证码
document.getElementById('send-sms-btn').addEventListener('click', async function() {
    const phone = document.getElementById('sms-phone').value;
    if (!phone) {
        showAlert('请输入手机号');
        return;
    }

    try {
        const response = await fetch(`${config.apiBaseUrl}/api/auth/send-sms`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ identifier: phone })
        });

        const data = await handleResponse(response);
        showAlert(data.message || '验证码已发送', 'success');

        // 倒计时
        let countdown = 60;
        this.disabled = true;
        const timer = setInterval(() => {
            this.textContent = `${countdown}s`;
            countdown--;
            if (countdown < 0) {
                clearInterval(timer);
                this.disabled = false;
                this.textContent = '发送验证码';
            }
        }, 1000);
    } catch (error) {
        showAlert(error.message);
    }
});

// 短信登录
document.getElementById('sms-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const phone = document.getElementById('sms-phone').value;
    const code = document.getElementById('sms-code').value;

    try {
        const response = await fetch(`${config.apiBaseUrl}/api/auth/login/sms`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone, code })
        });

        const data = await handleResponse(response);
        saveToken(data.data.access_token);
        showAlert('登录成功！', 'success');
        setTimeout(() => redirectTo('/profile.html'), 1000);
    } catch (error) {
        showAlert(error.message);
    }
});

// OAuth登录
document.querySelectorAll('.oauth-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const provider = this.dataset.provider;
        const authUrl = config.oauthProviders[provider];
        if (authUrl) {
            window.location.href = authUrl;
        } else {
            showAlert('该登录方式暂未配置');
        }
    });
});
```

**Step 3: 提交登录页面**

```bash
cd frontend
git add templates/login.html static/js/login.js
git commit -m "feat: 添加登录页面

- 支持密码、邮箱、短信三种登录方式
- 支持GitHub、Google、微信、钉钉、飞书第三方登录
- 验证码倒计时功能"
```

---

### Task 15: 创建注册页面

**Files:**
- Create: `frontend/templates/register.html`
- Create: `frontend/static/js/register.js`

**Step 1: 创建注册HTML**

创建 `frontend/templates/register.html`:

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>注册 - Login Demo</title>
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <div class="container">
        <div class="logo">
            <h1>创建账户</h1>
            <p>加入我们开始使用</p>
        </div>

        <div id="alert" class="alert hidden"></div>

        <form id="register-form">
            <div class="form-group">
                <label>用户名</label>
                <input type="text" id="username" required minlength="3" maxlength="50">
            </div>
            <div class="form-group">
                <label>密码</label>
                <input type="password" id="password" required minlength="6" maxlength="100">
            </div>
            <div class="form-group">
                <label>确认密码</label>
                <input type="password" id="confirm-password" required>
            </div>
            <div class="form-group">
                <label>昵称</label>
                <input type="text" id="nickname" required>
            </div>
            <div class="form-group">
                <label>邮箱（可选）</label>
                <input type="email" id="email">
            </div>
            <div class="form-group">
                <label>手机号（可选）</label>
                <input type="tel" id="phone" maxlength="11">
            </div>
            <button type="submit" class="btn btn-primary">注册</button>
        </form>

        <div class="links">
            <p>已有账户？ <a href="/login.html">立即登录</a></p>
        </div>
    </div>

    <script src="/static/js/config.js"></script>
    <script src="/static/js/utils.js"></script>
    <script src="/static/js/register.js"></script>
</body>
</html>
```

**Step 2: 创建注册JS**

创建 `frontend/static/js/register.js`:

```javascript
// 检查是否已登录
if (isLoggedIn()) {
    redirectTo('/profile.html');
}

// 注册表单提交
document.getElementById('register-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm-password').value;

    if (password !== confirmPassword) {
        showAlert('两次密码输入不一致');
        return;
    }

    const userData = {
        username: document.getElementById('username').value,
        password: password,
        nickname: document.getElementById('nickname').value,
        email: document.getElementById('email').value || null,
        phone: document.getElementById('phone').value || null
    };

    try {
        const response = await fetch(`${config.apiBaseUrl}/api/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData)
        });

        const data = await handleResponse(response);
        saveToken(data.data.access_token);
        showAlert('注册成功！', 'success');
        setTimeout(() => redirectTo('/profile.html'), 1000);
    } catch (error) {
        showAlert(error.message);
    }
});
```

**Step 3: 提交注册页面**

```bash
cd frontend
git add templates/register.html static/js/register.js
git commit -m "feat: 添加注册页面

- 支持用户名密码注册
- 可选邮箱和手机号
- 密码确认验证"
```

---

### Task 16: 创建个人中心页面

**Files:**
- Create: `frontend/templates/profile.html`
- Create: `frontend/static/js/profile.js`

**Step 1: 创建个人中心HTML**

创建 `frontend/templates/profile.html`:

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>个人中心 - Login Demo</title>
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <div class="container">
        <div class="profile-header">
            <h1>个人中心</h1>
        </div>

        <div id="alert" class="alert hidden"></div>

        <div class="avatar">
            <img id="avatar-img" src="/static/images/default-avatar.png" alt="头像">
        </div>

        <div class="info-item">
            <label>用户名</label>
            <span id="username">-</span>
        </div>
        <div class="info-item">
            <label>昵称</label>
            <span id="nickname">-</span>
        </div>
        <div class="info-item">
            <label>邮箱</label>
            <span id="email">-</span>
        </div>
        <div class="info-item">
            <label>手机号</label>
            <span id="phone">-</span>
        </div>

        <div class="form-group" style="margin-top: 20px;">
            <label>修改昵称</label>
            <input type="text" id="new-nickname" placeholder="输入新昵称">
        </div>

        <div class="form-group">
            <label>上传头像</label>
            <input type="file" id="avatar-file" accept="image/*">
        </div>

        <button id="update-btn" class="btn btn-primary">更新信息</button>
        <button id="logout-btn" class="btn btn-primary logout-btn">退出登录</button>
    </div>

    <script src="/static/js/config.js"></script>
    <script src="/static/js/utils.js"></script>
    <script src="/static/js/profile.js"></script>
</body>
</html>
```

**Step 2: 创建个人中心JS**

创建 `frontend/static/js/profile.js`:

```javascript
// 检查是否已登录
if (!isLoggedIn()) {
    redirectTo('/login.html');
}

// 加载用户信息
async function loadProfile() {
    try {
        const response = await fetch(`${config.apiBaseUrl}/api/user/profile`, {
            headers: getHeaders()
        });

        const data = await handleResponse(response);
        const user = data.data;

        document.getElementById('username').textContent = user.username || '-';
        document.getElementById('nickname').textContent = user.nickname;
        document.getElementById('email').textContent = user.email || '-';
        document.getElementById('phone').textContent = user.phone || '-';

        if (user.avatar_url) {
            document.getElementById('avatar-img').src = user.avatar_url.startsWith('http')
                ? user.avatar_url
                : `${config.apiBaseUrl}${user.avatar_url}`;
        }
    } catch (error) {
        showAlert(error.message);
        if (error.message.includes('401')) {
            clearToken();
            redirectTo('/login.html');
        }
    }
}

// 更新信息
document.getElementById('update-btn').addEventListener('click', async () => {
    const nickname = document.getElementById('new-nickname').value;
    if (!nickname) {
        showAlert('请输入新昵称');
        return;
    }

    try {
        const response = await fetch(`${config.apiBaseUrl}/api/user/profile`, {
            method: 'PUT',
            headers: getHeaders(),
            body: JSON.stringify({ nickname })
        });

        const data = await handleResponse(response);
        showAlert(data.message || '更新成功', 'success');
        document.getElementById('new-nickname').value = '';
        loadProfile();
    } catch (error) {
        showAlert(error.message);
    }
});

// 上传头像
document.getElementById('avatar-file').addEventListener('change', async function() {
    const file = this.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${config.apiBaseUrl}/api/user/avatar`, {
            method: 'POST',
            headers: {
                ...(localStorage.getItem('access_token') && { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` })
            },
            body: formData
        });

        const data = await handleResponse(response);
        showAlert(data.message || '头像上传成功', 'success');
        loadProfile();
    } catch (error) {
        showAlert(error.message);
    }
});

// 退出登录
document.getElementById('logout-btn').addEventListener('click', async () => {
    try {
        await fetch(`${config.apiBaseUrl}/api/auth/logout`, {
            method: 'POST',
            headers: getHeaders()
        });
    } catch (error) {
        console.error('Logout error:', error);
    }

    clearToken();
    showAlert('已退出登录', 'success');
    setTimeout(() => redirectTo('/login.html'), 1000);
});

// 初始加载
loadProfile();
```

**Step 3: 创建默认头像**

创建目录和占位文件:

```bash
mkdir -p frontend/static/images
```

创建 `frontend/static/images/default-avatar.png` (可使用简单的SVG占位):

**Step 4: 提交个人中心**

```bash
cd frontend
git add templates/profile.html static/js/profile.js static/images/
git commit -m "feat: 添加个人中心页面

- 显示用户信息
- 支持修改昵称
- 支持上传头像
- 退出登录功能"
```

---

## 第五阶段：启动脚本和配置

### Task 17: 创建后端启动脚本

**Files:**
- Create: `backend/start.sh`
- Create: `backend/static/uploads/avatars/.gitkeep`

**Step 1: 创建后端启动脚本**

创建 `backend/start.sh`:

```bash
#!/bin/bash

echo "Starting Login Demo Backend..."

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "Installing dependencies..."
pip install -r requirements.txt

# 复制环境变量文件
if [ ! -f ".env" ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "Please edit .env file with your configuration!"
fi

# 创建上传目录
mkdir -p static/uploads/avatars

# 运行数据库迁移
echo "Running database migrations..."
alembic upgrade head

# 启动服务器
echo "Starting server on http://localhost:8000"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Step 2: 添加执行权限**

```bash
chmod +x backend/start.sh
```

**Step 3: 创建占位文件**

创建 `backend/static/uploads/avatars/.gitkeep`:

```bash
mkdir -p backend/static/uploads/avatars
touch backend/static/uploads/avatars/.gitkeep
```

**Step 4: 提交启动脚本**

```bash
git add backend/start.sh backend/static/
git commit -m "feat: 添加后端启动脚本

- 自动创建虚拟环境
- 自动安装依赖
- 自动运行数据库迁移
- 启动FastAPI服务器"
```

---

### Task 18: 创建前端启动脚本

**Files:**
- Create: `frontend/start.sh`

**Step 1: 创建前端启动脚本**

创建 `frontend/start.sh`:

```bash
#!/bin/bash

echo "Starting Login Demo Frontend..."

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "Python3 is not installed!"
    exit 1
fi

# 启动HTTP服务器
echo "Starting server on http://localhost:8080"
cd $(dirname "$0")
python3 -m http.server 8080
```

**Step 2: 添加执行权限**

```bash
chmod +x frontend/start.sh
```

**Step 3: 提交启动脚本**

```bash
git add frontend/start.sh
git commit -m "feat: 添加前端启动脚本

- 使用Python内置HTTP服务器
- 监听8080端口"
```

---

### Task 19: 创建Docker Compose配置

**Files:**
- Create: `docker-compose.yml`

**Step 1: 创建Docker Compose配置**

创建 `docker-compose.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: login_demo_db
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: login_demo
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: login_demo_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
  redis_data:
```

**Step 2: 提交Docker配置**

```bash
git add docker-compose.yml
git commit -m "feat: 添加Docker Compose配置

- PostgreSQL 15数据库
- Redis 7缓存
- 数据持久化"
```

---

### Task 20: 更新README文档

**Files:**
- Modify: `README.md`

**Step 1: 更新README**

编辑 `README.md`:

```markdown
# 登录演示系统

一个前后端分离的登录演示项目，支持多种登录方式。

## 功能特性

- 账号密码登录
- 邮箱验证码登录
- 手机验证码登录
- 第三方登录（GitHub、Google、微信、钉钉、飞书）
- 个人中心

## 技术栈

### 后端
- Python 3.11+
- FastAPI
- PostgreSQL 15
- Redis
- SQLAlchemy
- JWT

### 前端
- HTML5
- CSS3
- 原生JavaScript

## 快速开始

### 1. 启动数据库服务

```bash
docker-compose up -d
```

### 2. 启动后端服务

```bash
cd backend
./start.sh
```

后端将运行在 http://localhost:8000

### 3. 启动前端服务

```bash
cd frontend
./start.sh
```

前端将运行在 http://localhost:8080

### 4. 访问应用

打开浏览器访问 http://localhost:8080

## 配置说明

复制 `backend/.env.example` 到 `backend/.env` 并修改配置：

- SMTP配置（邮箱验证码）
- 短信API配置（阿里云）
- OAuth应用配置（第三方登录）

## API文档

启动后端后访问 http://localhost:8000/docs 查看完整API文档。

## 开发说明

### 数据库迁移

```bash
cd backend
alembic revision --autogenerate -m "描述"
alembic upgrade head
```

### 目录结构

```
my_login_example/
├── backend/           # 后端代码
├── frontend/          # 前端代码
├── docs/             # 文档
└── docker-compose.yml # 数据库服务
```

## License

MIT
```

**Step 2: 提交README**

```bash
git add README.md
git commit -m "docs: 更新README文档"
```

---

## 实现完成检查清单

在完成所有任务后，验证以下功能：

### 后端
- [ ] FastAPI服务器正常启动
- [ ] 数据库迁移成功执行
- [ ] 账号密码注册/登录正常
- [ ] 邮箱验证码发送和登录正常
- [ ] 短信验证码发送和登录正常
- [ ] OAuth第三方登录正常（至少配置GitHub或Google）
- [ ] 用户信息获取和更新正常
- [ ] 头像上传正常

### 前端
- [ ] 登录页面所有Tab切换正常
- [ ] 注册页面提交正常
- [ ] 个人中心加载正常
- [ ] Token管理正常（自动跳转）

### 整体
- [ ] Docker服务正常启动
- [ ] 跨域配置正常
- [ ] 错误提示友好

---

**实现计划完成！**
