from datetime import datetime, time
from typing import Optional
import pytz

from sqlalchemy import String, DateTime, ForeignKey, Numeric, Time, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from pydantic import BaseModel, ConfigDict, field_validator


class Shop(Base):
    __tablename__ = "Shops"

    # db.txt: INT IDENTITY PK, owner_id FK, created_at default
    shop_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    shop_name: Mapped[str] = mapped_column(String(200))
    owner_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("Shop_Owners.owner_id", ondelete="CASCADE"), index=True)
    shop_image: Mapped[Optional[str]] = mapped_column(String(500))
    created_at: Mapped[datetime | None] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    address: Mapped[Optional["ShopAddress"]] = relationship(back_populates="shop", uselist=False)
    timings: Mapped[list["ShopTiming"]] = relationship(back_populates="shop")
    products: Mapped[list["ShopProduct"]] = relationship(back_populates="shop")
    owner: Mapped[Optional["ShopOwner"]] = relationship(back_populates="shops")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Shop {self.shop_name}>"

    def is_open(self) -> bool:
        if not self.timings:
            return False
        india_tz = pytz.timezone("Asia/Kolkata")
        now = datetime.now(india_tz)
        current_time = now.time()
        current_day = now.strftime("%A")
        current_timing = next((t for t in self.timings if t.day.lower() == current_day.lower()), None)
        if not current_timing:
            return False
        if isinstance(current_timing.open_time, str) and current_timing.open_time == "CLOSED":
            return False
        if current_timing.open_time is None or current_timing.close_time is None:
            return False
        return current_timing.open_time <= current_time <= current_timing.close_time


class ShopAddress(Base):
    __tablename__ = "Shop_Address"

    # db.txt: INT IDENTITY PK, FK to Shops, address fields
    address_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    shop_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("Shops.shop_id", ondelete="CASCADE"), index=True)
    city: Mapped[Optional[str]] = mapped_column(String(100))
    country: Mapped[Optional[str]] = mapped_column(String(100))
    pincode: Mapped[Optional[str]] = mapped_column(String(10))
    landmark: Mapped[Optional[str]] = mapped_column(String(200))
    area: Mapped[Optional[str]] = mapped_column(String(200))
    latitude: Mapped[Optional[float]] = mapped_column(Numeric(precision=10, scale=6))
    longitude: Mapped[Optional[float]] = mapped_column(Numeric(precision=10, scale=6))

    shop: Mapped["Shop"] = relationship(back_populates="address")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ShopAddress {self.area}, {self.city}>"


class ShopTiming(Base):
    __tablename__ = "Shop_Timings"

    # db.txt: INT IDENTITY PK, FK to Shops, day, open_time, close_time
    timing_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    shop_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("Shops.shop_id", ondelete="CASCADE"), index=True)
    day: Mapped[str] = mapped_column(String(20))
    open_time: Mapped[time | None] = mapped_column(Time)
    close_time: Mapped[time | None] = mapped_column(Time)

    shop: Mapped["Shop"] = relationship(back_populates="timings")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ShopTiming {self.day}: {self.open_time}-{self.close_time}>"


"""
DTOs for Shop
- ShopCreate, ShopRead: basic create/read
- ShopRegister: composite payload to create owner + shop + address
- ShopProductAdd: link product to shop with price/stock
- ShopInventoryUpdate: partial update for inventory
"""


class ShopCreate(BaseModel):
    shop_name: str
    owner_id: int | None = None
    shop_image: Optional[str] = None

    @field_validator("shop_name")
    @classmethod
    def _trim_name(cls, v: str) -> str:
        return v.strip()


class ShopRead(BaseModel):
    shop_id: int | str
    shop_name: str
    shop_image: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ShopRegister(BaseModel):
    shop_name: str
    gstin: Optional[str] = None
    shop_image: Optional[str] = None
    owner_name: Optional[str] = None
    owner_phone: Optional[str] = None
    owner_email: Optional[str] = None
    owner_password: Optional[str] = None
    owner_password_confirm: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    pincode: Optional[str] = None
    landmark: Optional[str] = None
    area: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    @field_validator("shop_name")
    @classmethod
    def _trim_shop(cls, v: str) -> str:
        return v.strip()

    @field_validator("city")
    @classmethod
    def _norm_city(cls, v: Optional[str]) -> Optional[str]:
        return (v or "").strip() or None

    @field_validator("pincode")
    @classmethod
    def _pincode_digits(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        d = "".join(ch for ch in v if ch.isdigit())
        if d and not (4 <= len(d) <= 10):
            raise ValueError("Invalid pincode format")
        return d if d else None

    @field_validator("gstin")
    @classmethod
    def _gstin_format(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return None
        s = v.strip().upper()
        # Allow common 15-char GSTIN format; relax if schema differs
        import re
        if not re.fullmatch(r"[0-9A-Z]{15}", s):
            raise ValueError("Invalid GSTIN format")
        return s

    @field_validator("latitude", "longitude")
    @classmethod
    def _latlon_range(cls, v: Optional[float]) -> Optional[float]:
        if v is None:
            return None
        try:
            x = float(v)
        except Exception:
            raise ValueError("Invalid coordinate")
        if not (-90.0 <= x <= 90.0) and not (-180.0 <= x <= 180.0):
            raise ValueError("Invalid coordinate range")
        return x


class ShopProductAdd(BaseModel):
    product_id: int
    price: float | None = None
    stock: int | None = None


class ShopInventoryUpdate(BaseModel):
    price: float | None = None
    stock: int | None = None
"""
Shop-related models.
Relationships:
- Shop 1:1 ShopAddress
- Shop 1:M ShopTiming
- Shop M:M Product via ShopProduct
- Shop M:1 ShopOwner
"""
