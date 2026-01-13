import random
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.verification_code import VerificationCode
from app.services.redis_service import redis_service
from app.core.config import get_settings

settings = get_settings()


class SmsService:
    async def send_verification_code(self, phone: str, db: AsyncSession) -> bool:
        cache_key = f"sms_code_limit:{phone}"
        if await redis_service.exists(cache_key):
            raise ValueError("验证码发送过于频繁，请60秒后再试")

        code = str(random.randint(100000, 999999))
        expires_at = datetime.utcnow() + timedelta(minutes=5)

        verification_code = VerificationCode(
            identifier=phone,
            code=code,
            code_type="sms",
            expires_at=expires_at
        )
        db.add(verification_code)
        await db.commit()

        try:
            await self._send_sms(phone, code)
            await redis_service.set(cache_key, "1", expire=60)
            return True
        except Exception as e:
            await db.rollback()
            raise e

    async def _send_sms(self, phone: str, code: str):
        # TODO: 实现实际的短信发送逻辑
        # 这里只是占位，实际需要调用阿里云短信API
        pass

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
