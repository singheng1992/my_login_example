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
        cache_key = f"email_code_limit:{email}"
        if await redis_service.exists(cache_key):
            raise ValueError("验证码发送过于频繁，请60秒后再试")

        code = str(random.randint(100000, 999999))
        expires_at = datetime.utcnow() + timedelta(minutes=5)

        verification_code = VerificationCode(
            identifier=email,
            code=code,
            code_type="email",
            expires_at=expires_at
        )
        db.add(verification_code)
        await db.commit()

        try:
            self._send_email(email, code)
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

        verification_code.used = True
        await db.commit()

        return True


email_service = EmailService()
