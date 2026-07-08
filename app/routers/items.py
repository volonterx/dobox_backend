from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.item import Item
from app.schemas.item import ItemRead, ItemCreate, ItemUpdate

router = APIRouter(prefix="/items", tags=["items"])

@router.get("/", response_model=list[ItemRead])
async def get_items(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Item))
    return result.scalars().all()

@router.get("/{item_id}", response_model=ItemRead)
async def get_item(item_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Item).where(Item.id == item_id))
    item = result.scalars().first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.post("/", response_model=ItemRead)
async def create_item(item: ItemCreate, db: AsyncSession = Depends(get_db)):
    item = Item(**item.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item

@router.put("/{item_id}", response_model=ItemRead)
async def update_item(item_id: int, item: ItemUpdate, db: AsyncSession = Depends(get_db)):
    data = item.model_dump(exclude_unset=True)
    result = await db.execute(update(Item).where(Item.id == item_id).values(**data).returning(Item))
    updated_item = result.scalars().first()
    if updated_item:
        await db.commit()
        return updated_item
    else:
        raise HTTPException(status_code=404, detail="Item not found")

@router.delete("/{item_id}")
async def delete_item(item_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(delete(Item).where(Item.id == item_id).returning(Item))
    deleted_id = result.scalar_one_or_none()
    if deleted_id:
        await db.commit()
    else:
        raise HTTPException(status_code=404, detail="Item not found")
