import hashlib
import random
import urllib.parse
from datetime import datetime, timedelta

import aiohttp
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.verification_code import VerificationCode
from app.services.redis_service import redis_service

settings = get_settings()


class SmsService:
    """短信服务（短信宝）"""

    # 状态码对应说明
    STATUS_MAP = {
        "0": "短信发送成功",
        "-1": "参数不全",
        "-2": "服务器空间不支持,请确认支持curl或者fsocket,联系您的空间商解决或者更换空间",
        "30": "密码错误",
        "40": "账号不存在",
        "41": "余额不足",
        "42": "账户已过期",
        "43": "IP地址限制",
        "50": "内容含有敏感词",
    }

    def _md5(self, text: str) -> str:
        """MD5 加密"""
        m = hashlib.md5()
        m.update(text.encode("utf8"))
        return m.hexdigest()

    async def send_verification_code(self, phone: str, db: AsyncSession) -> bool:
        """发送短信验证码"""
        cache_key = f"sms_code_limit:{phone}"
        if await redis_service.exists(cache_key):
            raise ValueError("验证码发送过于频繁，请60秒后再试")

        code = str(random.randint(100000, 999999))
        expires_at = datetime.utcnow() + timedelta(
            minutes=settings.SMSBAO_CODE_EXPIRE_MINUTES
        )

        verification_code = VerificationCode(
            identifier=phone, code=code, code_type="sms", expires_at=expires_at
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
        """发送短信（短信宝）

        Args:
            phone: 手机号码
            code: 验证码

        Raises:
            ValueError: 发送失败时抛出异常
        """
        # 检查配置
        if not settings.SMSBAO_USERNAME or not settings.SMSBAO_PASSWORD:
            raise ValueError(
                "短信配置未完成，请在配置文件中设置 SMSBAO_USER 和 SMSBAO_PASSWORD"
            )

        # 构建短信内容
        content = settings.SMSBAO_TEMPLATE.format(code=code)

        # MD5 加密密码
        password = self._md5(settings.SMSBAO_PASSWORD)

        # 构建请求参数
        params = {
            "u": settings.SMSBAO_USERNAME,
            "p": password,
            "m": phone,
            "c": content,
        }

        # 构建完整 URL
        url = f"{settings.SMSBAO_URL}/sms?{urllib.parse.urlencode(params)}"
        print(f"发送短信请求 URL: {url}")
        # 发送 HTTP 请求
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    url, timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    result = await response.text()

                    # 检查发送结果
                    if result != "0":
                        error_msg = self.STATUS_MAP.get(result, f"未知错误: {result}")
                        raise ValueError(f"短信发送失败: {error_msg}")

            except aiohttp.ClientError as e:
                raise ValueError(f"短信发送网络错误: {str(e)}")
            except Exception as e:
                raise ValueError(f"短信发送失败: {str(e)}")

    async def verify_code(self, phone: str, code: str, db: AsyncSession) -> bool:
        """验证短信验证码"""
        result = await db.execute(
            select(VerificationCode).where(
                VerificationCode.identifier == phone,
                VerificationCode.code == code,
                VerificationCode.code_type == "sms",
                VerificationCode.used == False,
                VerificationCode.is_deleted == False,
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
