# routers/item_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, case

from database import get_db
from models.item import Item
from models.stock_movement import StockMovement
from schemas.item import ItemCreate, ItemOut

router = APIRouter(prefix="/items", tags=["items"])


def _balance_expr():
    """
    Expressão SQL: soma entradas menos saídas.
    SUM(CASE WHEN type='IN' THEN quantity ELSE -quantity END)
    """
    return func.coalesce(
        func.sum(
            case(
                (StockMovement.type == "IN", StockMovement.quantity),
                else_=-StockMovement.quantity,
            )
        ),
        0,
    )


@router.post("", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemCreate, db: Session = Depends(get_db)) -> ItemOut:
    # Evita duplicidade pelo nome
    exists = db.query(Item).filter(Item.name == payload.name).first()
    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Item já cadastrado com esse nome.",
        )

    item = Item(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("", response_model=list[ItemOut])
def list_items(db: Session = Depends(get_db)) -> list[ItemOut]:
    return db.query(Item).order_by(Item.name.asc()).all()


@router.get("/{item_id}", response_model=ItemOut)
def get_item(item_id: int, db: Session = Depends(get_db)) -> ItemOut:
    item = db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado.")
    return item


@router.get("/{item_id}/balance")
def get_item_balance(item_id: int, db: Session = Depends(get_db)) -> dict:
    # Confirma existência do item
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
