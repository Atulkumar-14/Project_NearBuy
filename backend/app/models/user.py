from datetime import datetime
from sqlalchemy import String, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
import re


class User(Base):
    __tablename__ = "Users"

    # db.txt: [user_id] INT IDENTITY PK, unique email/phone, [created_at] DEFAULT getdate()
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str | None] = mapped_column(String(150))
    email: Mapped[str | None] = mapped_column(String(200), unique=True, index=True)
    password: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(15), unique=True, index=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships in db.txt
    reviews: Mapped[list["ProductReview"]] = relationship(back_populates="user")
    search_history: Mapped[list["SearchHistory"]] = relationship(back_populates="user")
    verification: Mapped["UserVerification"] = relationship(back_populates="user", uselist=False)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User {self.name}>"


"""
DTOs for User
- UserCreate: input for registration
- UserLogin: input for login
- UserRead: output model for responses
Includes validators for email normalization, name trimming, and password policy.
"""


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: str

    @field_validator("name")
    @classmethod
    def _trim_name(cls, v: str) -> str:
        return v.strip()

    @field_validator("email")
    @classmethod
    def _normalize_email(cls, v: EmailStr) -> str:
        s = str(v).strip().lower()
        return s

    @field_validator("phone")
    @classmethod
    def _sanitize_phone(cls, v: str) -> str:
        s = re.sub(r"[^0-9]", "", v or "")
        return s

    @field_validator("password")
    @classmethod
    def _password_policy(cls, v: str) -> str:
        pwd = v or ""
        if len(pwd) < 12:
            raise ValueError("Password must be at least 12 characters long")
        if not re.search(r"[A-Z]", pwd):
            raise ValueError("Password must include an uppercase letter")
        if not re.search(r"[a-z]", pwd):
            raise ValueError("Password must include a lowercase letter")
        if not re.search(r"[0-9]", pwd):
            raise ValueError("Password must include a digit")
        if not re.search(r"[^A-Za-z0-9]", pwd):
            raise ValueError("Password must include a symbol")
        common = {"password", "123456", "qwerty", "letmein", "admin", "welcome"}
        if pwd.lower() in common:
            raise ValueError("Password is too common")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def _normalize_email(cls, v: EmailStr) -> str:
        return str(v).strip().lower()


class UserRead(BaseModel):
    user_id: int | str
    name: str | None
    email: EmailStr | None
    phone: str | None
    created_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
    @field_validator("user_id", mode="before")
    @classmethod
    def _coerce_user_id(cls, v):
        if isinstance(v, (bytes, bytearray)):
            try:
                return v.hex()
            except Exception:
                return str(v)
        return v
"""
User model: represents application users.
Relationships:
- 1:M ProductReview via User.reviews
- 1:M SearchHistory via User.search_history
"""
