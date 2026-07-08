from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at:  Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
    completed: Mapped[bool] = mapped_column(default=False)
#     user_id: Mapped[int] = mapped_column(default=None)
