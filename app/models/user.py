from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship, WriteOnlyMapped
from app.database import Base
from app.models.oauth_account import OAuthAccount
from app.models.item import Item



class User(SQLAlchemyBaseUserTableUUID, Base):
  name: Mapped[str | None] = mapped_column(String(100), nullable=True)
  oauth_accounts: Mapped[list[OAuthAccount]] = relationship(lazy="joined")
  items: WriteOnlyMapped[Item] = relationship(lazy="write_only")
