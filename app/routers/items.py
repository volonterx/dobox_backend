from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth import current_active_user
from app.models.user import User
from app.models.item import Item
from app.schemas.item import ItemRead, ItemCreate, ItemUpdate

from app.utils import utcnow


router = APIRouter(prefix="/items", tags=["items"])

async def get_owned_item(
  item_id: int,
  current_user: User = Depends(current_active_user),
  db: AsyncSession = Depends(get_db),
) -> Item:
  result = await db.execute(current_user.items.select().where(Item.id == item_id))
  item = result.scalar_one_or_none()
  if item is None:
      raise HTTPException(status_code=404, detail="Item not found")
  return item


@router.get("/", response_model=list[ItemRead])
async def get_items(
  current_user: User = Depends(current_active_user),
  db: AsyncSession = Depends(get_db),
):
  result = await db.execute(
    current_user.items.select().order_by(
      Item.completed_at.is_(None).desc(),
      Item.updated_at.desc(),
    )
  )
  return result.scalars().all()


@router.post("/", response_model=ItemRead)
async def create_item(
  data: ItemCreate,
  current_user: User = Depends(current_active_user),
  db: AsyncSession = Depends(get_db),
):
  item = Item(**data.model_dump())
  current_user.items.add(item)
  await db.commit()
  await db.refresh(item)
  return item


@router.get("/{item_id}", response_model=ItemRead)
async def get_item(item: Item = Depends(get_owned_item)):
  return item


@router.put("/{item_id}", response_model=ItemRead)
async def update_item(
  data: ItemUpdate,
  item: Item = Depends(get_owned_item),
  db: AsyncSession = Depends(get_db),
):
  for field, value in data.model_dump(exclude_unset=True).items():
      setattr(item, field, value)
  if data.completed:
      item.completed_at = utcnow()
  if data.started:
      item.started_at = utcnow()
  await db.commit()
  await db.refresh(item)
  return item


@router.delete("/{item_id}", status_code=204)
async def delete_item(
  item: Item = Depends(get_owned_item),
  db: AsyncSession = Depends(get_db),
):
  await db.delete(item)
  await db.commit()
