from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, DateTime

from app.database import Base
from app.utils import utcnow

class Item(Base):
  __tablename__ = "items"

  id: Mapped[int] = mapped_column(primary_key=True)
  title: Mapped[str] = mapped_column()
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
  updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
  completed: Mapped[bool] = mapped_column(default=False)
  user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
