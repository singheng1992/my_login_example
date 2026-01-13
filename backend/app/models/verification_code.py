import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class VerificationCode(Base):
    __tablename__ = "verification_codes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    identifier = Column(String(255), nullable=False, index=True)  # email or phone
    code = Column(String(10), nullable=False)
    code_type = Column(String(20), nullable=False)  # email, sms
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False, server_default=text('FALSE'))
    is_deleted = Column(Boolean, default=False, server_default=text('FALSE'), index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<VerificationCode {self.identifier}:{self.code}>"
