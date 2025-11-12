from datetime import datetime
from sqlalchemy import String, DateTime, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class AdminCredential(Base):
    __tablename__ = "admin_credentials"

    username: Mapped[str] = mapped_column(String(255), primary_key=True)
    password_hash: Mapped[str] = mapped_column(Text)
    salt: Mapped[str] = mapped_column(Text)
    last_login: Mapped[datetime | None] = mapped_column(DateTime, default=None)
    failed_attempts: Mapped[int] = mapped_column(Integer, default=0)

