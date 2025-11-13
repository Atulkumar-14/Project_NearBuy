from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, Numeric, Integer, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from pydantic import BaseModel, ConfigDict, field_validator


class Product(Base):
    __tablename__ = "Products"

    # db.txt: INT IDENTITY PK, FK to Product_Categories, created_at default
    product_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_name: Mapped[str] = mapped_column(String(200))
    category_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("Product_Categories.category_id", ondelete="CASCADE"), index=True)
    category_key: Mapped[str | None] = mapped_column(String(100), index=True)
    brand: Mapped[str | None] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(String(1000))
    color: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[datetime | None] = mapped_column(DateTime, default=datetime.utcnow)

    images: Mapped[list["ProductImage"]] = relationship(back_populates="product")
    reviews: Mapped[list["ProductReview"]] = relationship(back_populates="product")
    shop_products: Mapped[list["ShopProduct"]] = relationship(back_populates="product")
    category: Mapped[Optional["ProductCategory"]] = relationship(back_populates="products")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Product {self.product_name}>"


class ProductImage(Base):
    __tablename__ = "Product_Images"

    # db.txt: INT IDENTITY PK, product_id FK, image_url
    image_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[bytes] = mapped_column(LargeBinary, ForeignKey("Products.product_id", ondelete="CASCADE"), index=True)
    image_url: Mapped[str] = mapped_column(String(500))

    product: Mapped["Product"] = relationship(back_populates="images")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ProductImage {self.image_id} for product {self.product_id}>"


class ShopProduct(Base):
    __tablename__ = "Shop_Product"

    # db.txt: INT IDENTITY PK, shop_id FK, product_id FK, price, stock
    shop_product_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    shop_id: Mapped[int] = mapped_column(Integer, ForeignKey("Shops.shop_id", ondelete="CASCADE"), index=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("Products.product_id", ondelete="CASCADE"), index=True)
    price: Mapped[float | None] = mapped_column(Numeric(precision=10, scale=2))
    stock: Mapped[int | None] = mapped_column(Integer)

    product: Mapped["Product"] = relationship(back_populates="shop_products")
    shop: Mapped["Shop"] = relationship(back_populates="products")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ShopProduct {self.shop_product_id}>"





class ProductCreate(BaseModel):
    product_name: str
    category_id: str | None = None
    brand: str | None = None
    description: str | None = None
    color: str | None = None

    @field_validator("product_name")
    @classmethod
    def _trim_name(cls, v: str) -> str:
        return v.strip()

    @field_validator("brand")
    @classmethod
    def _trim_brand(cls, v: str | None) -> str | None:
        return v.strip() if isinstance(v, str) else v

    @field_validator("description")
    @classmethod
    def _trim_desc(cls, v: str | None) -> str | None:
        return v.strip() if isinstance(v, str) else v

    @field_validator("color")
    @classmethod
    def _trim_color(cls, v: str | None) -> str | None:
        return v.strip() if isinstance(v, str) else v


class ProductRead(BaseModel):
    product_id: int | str
    product_name: str
    brand: str | None
    description: str | None
    color: str | None
    category_id: str | None = None

    model_config = ConfigDict(from_attributes=True)
