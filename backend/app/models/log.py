from datetime import datetime
from sqlalchemy import String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class Log(Base):
    __tablename__ = "Log"

    # db.txt: [log_id] INT IDENTITY PK, [user_id] INT FK (CASCADE), [action_type], [description], [timestamp] DEFAULT getdate(), [ip_address], [status_code] DEFAULT 200
    log_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("Users.user_id", ondelete="CASCADE"))
    action_type: Mapped[str | None] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(String(500))
    timestamp: Mapped[datetime | None] = mapped_column(DateTime, default=datetime.utcnow)
    ip_address: Mapped[str | None] = mapped_column(String(50))
    status_code: Mapped[int | None] = mapped_column(Integer, default=200)