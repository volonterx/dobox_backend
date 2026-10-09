from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, DateTime

from app.database import Base
from app.utils import utcnow

class Item(Base):
  __tablename__ = "items"

  id: Mapped[int] = mapped_column(primary_key=True)
  title: Mapped[str] = mapped_column()
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
  updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
  user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
  started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
  completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
  parent_id: Mapped[int] = mapped_column(ForeignKey("items.id"), nullable=True)

  parent: Mapped["Item | None"] = relationship(remote_side=[id], lazy="joined", join_depth=1)