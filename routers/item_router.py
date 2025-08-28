# routers/item_router.py

from typing import Optional, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, case

from database import get_db
from models.item import Item
from models.stock_movement import StockMovement
from schemas.item import ItemCreate, ItemUpdate, ItemOut
from schemas.common import Page
from auth.auth_utils import get_current_user
from models.user import User

router = APIRouter(prefix="/items", tags=["items"])


def _balance_expr():
    return func.coalesce(
        func.sum(
            case(
                (StockMovement.type == "IN", StockMovement.quantity),
                else_=-StockMovement.quantity,
            )
        ),
        0,
    )


# ---------- CREATE ----------
@router.post("", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
def create_item(
    payload: ItemCreate,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> ItemOut:
    exists = db.query(Item).filter(func.lower(Item.name) == func.lower(payload.name)).first()
    if exists:
        raise HTTPException(status_code=409, detail="Item já cadastrado com esse nome.")
    item = Item(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


# ---------- LIST ----------
@router.get("", response_model=Page[ItemOut])
def list_items(
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
    q: Optional[str] = Query(None, description="Busca por nome/categoria (contém)"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    order: Literal["name_asc", "name_desc", "id_desc", "id_asc"] = "name_asc",
) -> Page[ItemOut]:
    query = db.query(Item)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter((Item.name.ilike(like)) | (Item.category.ilike(like)))

    total = query.count()

    if order == "name_asc":
        query = query.order_by(Item.name.asc())
    elif order == "name_desc":
        query = query.order_by(Item.name.desc())
    elif order == "id_desc":
        query = query.order_by(Item.id.desc())
    else:
        query = query.order_by(Item.id.asc())

    items = query.offset((page - 1) * size).limit(size).all()
    return Page[ItemOut](items=items, page=page, size=size, total=total)


# ---------- READ ----------
@router.get("/{item_id}", response_model=ItemOut)
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> ItemOut:
    item = db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado.")
    return item


# ---------- UPDATE ----------
@router.patch("/{item_id}", response_model=ItemOut)
def update_item(
    item_id: int,
    payload: ItemUpdate,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> ItemOut:
    item = db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado.")

    data = payload.model_dump(exclude_unset=True)

    if "name" in data:
        conflict = (
            db.query(Item)
            .filter(func.lower(Item.name) == func.lower(data["name"]), Item.id != item_id)
            .first()
        )
        if conflict:
            raise HTTPException(status_code=409, detail="Já existe outro item com esse nome.")

    for field, value in data.items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)
    return item


# ---------- DELETE ----------
@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    item = db.get(Item, item_id)
    if not item:
        return
    db.delete(item)
    db.commit()


# ---------- BALANCE ----------
@router.get("/{item_id}/balance")
def get_item_balance(
    item_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> dict:
    item = db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado.")

    balance = (
        db.query(_balance_expr())
        .filter(StockMovement.item_id == item_id)
        .scalar()
    ) or 0

    return {
        "item_id": item_id,
        "name": item.name,
        "balance": int(balance),
        "unit": item.unit,
        "min_stock": item.min_stock,
        "below_min_stock": balance < item.min_stock,
    }

