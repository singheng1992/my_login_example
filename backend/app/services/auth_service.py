from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.core.security import verify_password, get_password_hash, create_access_token

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
        if username:
            result = await db.execute(
                select(User).where(User.username == username, User.is_deleted == False)
            )
            if result.scalar_one_or_none():
                raise ValueError("用户名已存在")

        if email:
            result = await db.execute(
                select(User).where(User.email == email, User.is_deleted == False)
            )
            if result.scalar_one_or_none():
                raise ValueError("邮箱已被注册")

        if phone:
            result = await db.execute(
                select(User).where(User.phone == phone, User.is_deleted == False)
            )
            if result.scalar_one_or_none():
                raise ValueError("手机号已被注册")

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

        if not await email_service.verify_code(email, code, db):
            raise ValueError("验证码错误或已过期")

        result = await db.execute(
            select(User).where(User.email == email, User.is_deleted == False)
        )
        user = result.scalar_one_or_none()

        if not user:
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

        if not await sms_service.verify_code(phone, code, db):
            raise ValueError("验证码错误或已过期")

        result = await db.execute(
            select(User).where(User.phone == phone, User.is_deleted == False)
        )
        user = result.scalar_one_or_none()

        if not user:
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
