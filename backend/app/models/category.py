from datetime import datetime
from sqlalchemy import String, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class ProductCategory(Base):
    __tablename__ = "Product_Categories"

    # db.txt: INT IDENTITY PK, unique name, created_at default
    category_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category_key: Mapped[str | None] = mapped_column(String(100), unique=True, index=True)
    category_name: Mapped[str] = mapped_column(String(100), unique=True)
    category_description: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime | None] = mapped_column(DateTime, default=datetime.utcnow)

    products: Mapped[list["Product"]] = relationship(back_populates="category")
"""
ProductCategory model.
Relationships:
- ProductCategory 1:M Product
"""
