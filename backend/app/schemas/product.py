from pydantic import BaseModel
from uuid import UUID


class ProductCreate(BaseModel):
    product_name: str
    category_id: UUID | None = None
    brand: str | None = None
    description: str | None = None
    color: str | None = None


class ProductRead(BaseModel):
    product_id: UUID
    product_name: str
    brand: str | None
    description: str | None
    color: str | None

    class Config:
        from_attributes = True