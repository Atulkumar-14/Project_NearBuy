from datetime import datetime, time
import uuid
from typing import Optional

import pytz
from sqlalchemy import String, DateTime, ForeignKey, Numeric, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.db.types import GUID


class Shop(Base):
    __tablename__ = "Shops"

    shop_id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    shop_name: Mapped[str] = mapped_column(String(200))
    # GSTIN (India GST Identification Number) used as unique business identifier
    gstin: Mapped[str | None] = mapped_column(String(15), unique=True)
    owner_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("Shop_Owners.owner_id", ondelete="CASCADE"), index=True)
    shop_image: Mapped[Optional[str]] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

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

    address_id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    shop_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("Shops.shop_id", ondelete="CASCADE"), index=True)
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

    timing_id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    shop_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("Shops.shop_id", ondelete="CASCADE"), index=True)
    day: Mapped[str] = mapped_column(String(20))
    open_time: Mapped[time | None] = mapped_column(Time)
    close_time: Mapped[time | None] = mapped_column(Time)

    shop: Mapped["Shop"] = relationship(back_populates="timings")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ShopTiming {self.day}: {self.open_time}-{self.close_time}>"