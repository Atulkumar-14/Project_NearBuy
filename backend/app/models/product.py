from datetime import datetime
import uuid
from sqlalchemy import String, DateTime, ForeignKey, Numeric, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.db.types import GUID


class Product(Base):
    __tablename__ = "Products"

    product_id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    product_name: Mapped[str] = mapped_column(String(200))
    category_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("Product_Categories.category_id", ondelete="CASCADE"), index=True)
    brand: Mapped[str | None] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(String(1000))
    color: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    images: Mapped[list["ProductImage"]] = relationship(back_populates="product")
    reviews: Mapped[list["ProductReview"]] = relationship(back_populates="product")
    shop_products: Mapped[list["ShopProduct"]] = relationship(back_populates="product")
    from typing import Optional
    category: Mapped[Optional["ProductCategory"]] = relationship(back_populates="products")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Product {self.product_name}>"


class ProductImage(Base):
    __tablename__ = "Product_Images"

    image_id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("Products.product_id", ondelete="CASCADE"), index=True)
    image_url: Mapped[str] = mapped_column(String(500))

    product: Mapped["Product"] = relationship(back_populates="images")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ProductImage {self.image_id} for product {self.product_id}>"


class ShopProduct(Base):
    __tablename__ = "Shop_Product"

    shop_product_id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    shop_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("Shops.shop_id", ondelete="CASCADE"), index=True)
    product_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("Products.product_id", ondelete="CASCADE"), index=True)
    price: Mapped[float | None] = mapped_column(Numeric(precision=10, scale=2))
    stock: Mapped[int | None] = mapped_column(Integer)

    product: Mapped["Product"] = relationship(back_populates="shop_products")
    shop: Mapped["Shop"] = relationship(back_populates="products")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ShopProduct {self.shop_product_id}>"
