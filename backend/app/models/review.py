from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Numeric, CheckConstraint, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from pydantic import BaseModel, ConfigDict


class ProductReview(Base):
    __tablename__ = "Product_Reviews"

    review_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("Users.user_id", ondelete="CASCADE"), index=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("Products.product_id", ondelete="CASCADE"), index=True)
    rating: Mapped[float] = mapped_column(Numeric(2, 1))
    review_text: Mapped[str | None] = mapped_column(String(1000))
    created_at: Mapped[datetime | None] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("rating >= 1.0 AND rating <= 5.0", name="ck_rating_range"),
    )

    user: Mapped["User"] = relationship(back_populates="reviews")
    product: Mapped["Product"] = relationship(back_populates="reviews")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ProductReview {self.review_id} by user {self.user_id}>"


"""
DTOs for ProductReview
- ReviewCreate: input for creating a review
- ReviewRead: output model for responses
IDs are `int` to match SQLAlchemy models.
"""


class ReviewCreate(BaseModel):
    product_id: int
    rating: float
    review_text: str | None = None


class ReviewRead(BaseModel):
    review_id: int
    product_id: int
    user_id: int
    rating: float
    review_text: str | None

    model_config = ConfigDict(from_attributes=True)
"""
ProductReview model.
Relationships:
- Review M:1 User
- Review M:1 Product
"""
