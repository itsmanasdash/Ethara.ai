from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import OrderCreate, OrderResponse
from app.crud import orders as crud

router = APIRouter()


@router.post("/", response_model=OrderResponse, status_code=201)
def create_order(data: OrderCreate, db: Session = Depends(get_db)):
    """
    Create a new order.
    - Validates customer and all products exist.
    - Rejects order if any product has insufficient stock.
    - Automatically deducts stock and calculates total amount.
    """
    return crud.create_order(db, data)


@router.get("/", response_model=List[OrderResponse])
def list_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Retrieve all orders with customer and item details."""
    return crud.get_orders(db, skip=skip, limit=limit)


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """Retrieve a single order with full details."""
    return crud.get_order(db, order_id)


@router.delete("/{order_id}")
def cancel_order(order_id: int, db: Session = Depends(get_db)):
    """
    Cancel/delete an order.
    - Restores inventory for all items in the order.
    """
    return crud.delete_order(db, order_id)