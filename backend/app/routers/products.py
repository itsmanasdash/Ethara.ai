from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import ProductCreate, ProductUpdate, ProductResponse
from app.crud import products as crud

router = APIRouter()


@router.post("/", response_model=ProductResponse, status_code=201)
def create_product(data: ProductCreate, db: Session = Depends(get_db)):
    """Create a new product. SKU must be unique."""
    return crud.create_product(db, data)


@router.get("/", response_model=List[ProductResponse])
def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Retrieve all products with optional pagination."""
    return crud.get_products(db, skip=skip, limit=limit)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Retrieve a single product by ID."""
    return crud.get_product(db, product_id)


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int, data: ProductUpdate, db: Session = Depends(get_db)
):
    """Update product details. Only provided fields are updated."""
    return crud.update_product(db, product_id, data)


@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Delete a product by ID."""
    return crud.delete_product(db, product_id)