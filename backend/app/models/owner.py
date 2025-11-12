import uuid
from datetime import datetime
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from app.db.base import Base
from app.db.types import GUID


class ShopOwner(Base):
    __tablename__ = "Shop_Owners"

    owner_id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    owner_name: Mapped[str | None] = mapped_column(String(150))
    phone: Mapped[str | None] = mapped_column(String(15), unique=True, index=True)
    email: Mapped[str | None] = mapped_column(String(200), unique=True, index=True)
    password_hash: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime)

    shops: Mapped[list["Shop"]] = relationship(back_populates="owner")
    security: Mapped[Optional["OwnerSecurity"]] = relationship(back_populates="owner", uselist=False)