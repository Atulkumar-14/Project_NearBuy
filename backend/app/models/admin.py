from datetime import datetime
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from pydantic import BaseModel


class Admin(Base):
    __tablename__ = "admin"

    # db.txt: [userId] NVARCHAR(50) PRIMARY KEY, [password] NVARCHAR(255), [created_at] DATETIME DEFAULT getdate()
    userId: Mapped[str] = mapped_column(String(50), primary_key=True)
    password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime | None] = mapped_column(DateTime, default=datetime.utcnow)


class AdminLogin(BaseModel):
    userId: str
    password: str
