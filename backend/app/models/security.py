from datetime import datetime
import uuid
from sqlalchemy import String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.db.types import GUID


class UserVerification(Base):
    __tablename__ = "User_Verification"

    ver_id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("Users.user_id", ondelete="CASCADE"), index=True)
    registration_started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    registration_completed_at: Mapped[datetime | None] = mapped_column(DateTime)
    email_verified_at: Mapped[datetime | None] = mapped_column(DateTime)
    phone_verified_at: Mapped[datetime | None] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending|verified|blocked

    user: Mapped["User"] = relationship(back_populates="verification")


class OwnerSecurity(Base):
    __tablename__ = "Owner_Security"

    sec_id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("Shop_Owners.owner_id", ondelete="CASCADE"), index=True)
    email_verified_at: Mapped[datetime | None] = mapped_column(DateTime)
    phone_verified_at: Mapped[datetime | None] = mapped_column(DateTime)
    two_factor_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    two_factor_secret: Mapped[str | None] = mapped_column(String(64))
    last_2fa_verified_at: Mapped[datetime | None] = mapped_column(DateTime)

    owner: Mapped["ShopOwner"] = relationship(back_populates="security")


class AuthLog(Base):
    __tablename__ = "Auth_Log"

    log_id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    principal_type: Mapped[str] = mapped_column(String(10))  # user|owner|admin
    principal_id: Mapped[str | None] = mapped_column(String(64))
    event_type: Mapped[str] = mapped_column(String(30))  # register|login|logout|refresh|verify
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    reason: Mapped[str | None] = mapped_column(String(255))
    ip: Mapped[str | None] = mapped_column(String(64))
    user_agent: Mapped[str | None] = mapped_column(String(255))
    occurred_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)