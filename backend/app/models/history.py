from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class SearchHistory(Base):
    __tablename__ = "Search_History"

    history_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("Users.user_id", ondelete="CASCADE"), index=True)
    search_item: Mapped[str] = mapped_column(String(255))
    timestamp: Mapped[datetime | None] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="search_history")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<SearchHistory {self.search_item}>"