from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class ShopCreate(BaseModel):
    shop_name: str
    gstin: str
    owner_id: UUID | None = None
    shop_image: str | None = None


class ShopRead(BaseModel):
    shop_id: UUID
    shop_name: str
    gstin: Optional[str]
    shop_image: str | None

    class Config:
        from_attributes = True


class ShopPrice(BaseModel):
    shop_id: UUID
    shop_name: str
    price: float | None
    stock: int | None


class ShopRegister(BaseModel):
    # Basic shop info
    shop_name: str
    gstin: str
    shop_image: str | None = None

    # Owner info (created or linked by email/phone)
    owner_name: Optional[str] = None
    owner_phone: Optional[str] = None
    owner_email: Optional[str] = None
    owner_password: Optional[str] = None

    # Address info (optional but recommended)
    city: Optional[str] = None
    country: Optional[str] = None
    pincode: Optional[str] = None
    landmark: Optional[str] = None
    area: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class ShopProductAdd(BaseModel):
    product_id: UUID
    price: float | None = None
    stock: int | None = None