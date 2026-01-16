import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class OAuthAccount(Base):
    __tablename__ = "oauth_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    provider = Column(String(50), nullable=False, index=True)  # github, google, wechat, dingtalk, feishu
    provider_user_id = Column(String(255), nullable=False)
    access_token = Column(String(500), nullable=True)
    refresh_token = Column(String(500), nullable=True)
    is_deleted = Column(Boolean, default=False, server_default=text('FALSE'), index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint('provider', 'provider_user_id', name='uq_oauth_provider_user_id'),
    )

    def __repr__(self):
        return f"<OAuthAccount {self.provider}:{self.provider_user_id}>"
