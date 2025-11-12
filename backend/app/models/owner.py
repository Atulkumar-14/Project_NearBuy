from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from pydantic import BaseModel, EmailStr, ConfigDict, field_validator


class ShopOwner(Base):
    __tablename__ = "Shop_Owners"

    # db.txt: INT IDENTITY PK, unique email and phone
    owner_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_name: Mapped[str | None] = mapped_column(String(150))
    phone: Mapped[str | None] = mapped_column(String(15), unique=True, index=True)
    email: Mapped[str | None] = mapped_column(String(200), unique=True, index=True)
    password_hash: Mapped[str | None] = mapped_column(String(255))

    shops: Mapped[list["Shop"]] = relationship(back_populates="owner")
    security: Mapped["OwnerSecurity"] = relationship(back_populates="owner", uselist=False)


"""
DTOs for ShopOwner
- OwnerLogin: email-only login payload
- OwnerRead: output model for owner info
"""


class OwnerLogin(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def _normalize_email(cls, v: str) -> str:
        return str(v).strip().lower()


class OwnerRead(BaseModel):
    owner_id: int
    owner_name: str | None
    email: str | None
    phone: str | None

    model_config = ConfigDict(from_attributes=True)
