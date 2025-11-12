from datetime import datetime
import uuid
from sqlalchemy import String, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.db.types import GUID


class SearchHistory(Base):
    __tablename__ = "Search_History"

    history_id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("Users.user_id", ondelete="CASCADE"), index=True)
    search_item: Mapped[str] = mapped_column(String(255))
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="search_history")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<SearchHistory {self.search_item}>"


class PurchaseHistory(Base):
    __tablename__ = "Purchase_History"

    purchase_id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("Users.user_id", ondelete="CASCADE"), index=True)
    shop_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("Shops.shop_id", ondelete="CASCADE"), index=True)
    product_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("Products.product_id", ondelete="CASCADE"), index=True)
    quantity: Mapped[int] = mapped_column(Integer)
    total_price: Mapped[float] = mapped_column()
    purchased_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="purchases")