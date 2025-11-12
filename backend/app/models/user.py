from datetime import datetime
import uuid
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from app.db.base import Base
from app.db.types import GUID


class User(Base):
    __tablename__ = "Users"

    user_id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    name: Mapped[str | None] = mapped_column(String(150))
    email: Mapped[str | None] = mapped_column(String(200), unique=True, index=True)
    password: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(15), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime)

    # Relationships
    reviews: Mapped[list["ProductReview"]] = relationship(back_populates="user")
    search_history: Mapped[list["SearchHistory"]] = relationship(back_populates="user")
    purchases: Mapped[list["PurchaseHistory"]] = relationship(back_populates="user")
    verification: Mapped[Optional["UserVerification"]] = relationship(back_populates="user", uselist=False)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User {self.name}>"