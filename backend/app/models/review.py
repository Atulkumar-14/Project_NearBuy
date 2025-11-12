from datetime import datetime
import uuid
from sqlalchemy import String, DateTime, ForeignKey, Float, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.db.types import GUID


class ProductReview(Base):
    __tablename__ = "Product_Reviews"

    review_id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("Users.user_id", ondelete="CASCADE"), index=True)
    product_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("Products.product_id", ondelete="CASCADE"), index=True)
    rating: Mapped[float] = mapped_column(Float)
    review_text: Mapped[str | None] = mapped_column(String(1000))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("rating BETWEEN 1.0 AND 5.0", name="ck_rating_range"),
    )

    user: Mapped["User"] = relationship(back_populates="reviews")
    product: Mapped["Product"] = relationship(back_populates="reviews")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ProductReview {self.review_id} by user {self.user_id}>"