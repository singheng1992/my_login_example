from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.core.database import Base


class Session(Base):
    """用户登录会话表"""
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    token_jti = Column(String(255), unique=True, nullable=False, index=True, comment="Token唯一标识(JWT ID)")
    device_info = Column(String(255), nullable=True, comment="设备信息")
    ip_address = Column(String(45), nullable=True, comment="IP地址")
    user_agent = Column(Text, nullable=True, comment="用户代理")
    is_revoked = Column(Boolean, default=False, nullable=False, index=True, comment="是否已撤销")
    revoked_at = Column(DateTime, nullable=True, comment="撤销时间")
    last_used_at = Column(DateTime, default=datetime.utcnow, comment="最后使用时间")
    expires_at = Column(DateTime, nullable=False, index=True, comment="过期时间")
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
