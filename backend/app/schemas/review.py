from pydantic import BaseModel
from uuid import UUID


class ReviewCreate(BaseModel):
    product_id: UUID
    rating: float
    review_text: str | None = None


class ReviewRead(BaseModel):
    review_id: UUID
    product_id: UUID
    user_id: UUID
    rating: float
    review_text: str | None

    class Config:
        from_attributes = True