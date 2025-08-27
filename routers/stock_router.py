# routers/stock_router.py

from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, case

from database import get_db
from models.item import Item
from models.stock_movement import StockMovement
from schemas.stock import MovementCreate, MovementOut

router = APIRouter(prefix="/stock", tags=["stock"])


# --- expressão SQL para saldo (IN - OUT) ---
def _balance_expr():
    return func.coalesce(
        func.sum(
            case((StockMovement.type == "IN", StockMovement.quantity), else_=-StockMovement.quantity)
        ),
        0,
    )


def get_balance(db: Session, item_id: int) -> int:
    return (
        db.query(_balance_expr())
        .filter(StockMovement.item_id == item_id)
        .scalar()
        or 0
    )


# ---------- Endpoints ----------

@router.post("/move", response_model=MovementOut, status_code=status.HTTP_201_CREATED)
def move_stock(payload: MovementCreate, db: Session = Depends(get_db)):
    """
    Registra movimentação de estoque:
    - type = "IN" (entrada) ou "OUT" (saída)
    - valida saldo para saídas
    """
    item = db.get(Item, payload.item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado.")

    if payload.type not in ("IN", "OUT"):
        raise HTTPException(status_code=400, detail="type deve ser 'IN' ou 'OUT'.")

    if payload.type == "OUT":
        balance = get_balance(db, payload.item_id)
        if payload.quantity > balance:
            raise HTTPException(
                status_code=400,
                detail=f"Sem saldo suficiente. Saldo atual: {balance}",
            )

    mov = StockMovement(**payload.model_dump())
    db.add(mov)
    db.commit()
    db.refresh(mov)
    return mov


@router.get("/movements", response_model=list[MovementOut])
def list_movements(
    db: Session = Depends(get_db),
    item_id: Optional[int] = None,
    type: Optional[str] = Query(None, pattern="^(IN|OUT)$"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """
    Lista movimentações com filtros opcionais:
    - item_id
    - type: IN ou OUT
    - paginação: limit/offset
    """
    q = db.query(StockMovement)
    if item_id is not None:
        q = q.filter(StockMovement.item_id == item_id)
    if type is not None:
        q = q.filter(StockMovement.type == type)
    return q.order_by(StockMovement.id.desc()).offset(offset).limit(limit).all()


@router.get("/alerts/low")
def low_stock_alerts(db: Session = Depends(get_db)):
    """
    Retorna itens com saldo abaixo do mínimo (min_stock).
    """
    alerts = []
    items = db.query(Item).all()
    for it in items:
        bal = get_balance(db, it.id)
        if bal < it.min_stock:
            alerts.append(
                {
                    "item_id": it.id,
                    "name": it.name,
                    "balance": int(bal),
                    "unit": it.unit,
                    "min_stock": it.min_stock,
                    "below_min_stock": True,
                }
            )
    return alerts


@router.get("/alerts/expiry")
def expiry_alerts(days: int = Query(30, ge=1, le=365), db: Session = Depends(get_db)):
    """
    Lotes vencidos ou a vencer em N dias.
    - Busca a menor data de validade por lote+item (se houver duplicatas).
    - Como é MVP, percorre movimentos com expiration_date.
    """
    today = date.today()
    limit_date = today + timedelta(days=days)

    q = db.query(StockMovement).filter(StockMovement.expiration_date.isnot(None))
    alerts = []
    for m in q:
        status = None
        if m.expiration_date < today:
            status = "expired"
        elif today <= m.expiration_date <= limit_date:
            status = "expiring_soon"

        if status:
            alerts.append(
                {
                    "item_id": m.item_id,
                    "lot": m.lot,
                    "expiration_date": m.expiration_date.isoformat(),
                    "status": status,
                }
            )
    return alerts


@router.get("/balance/{item_id}")
def quick_balance(item_id: int, db: Session = Depends(get_db)):
    """
    Atalho: retorna só o saldo atual de um item.
    """
    item = db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado.")
    bal = get_balance(db, item_id)
    return {"item_id": item_id, "name": item.name, "balance": int(bal), "unit": item.unit}
