import uuid
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models import Product
from app.schemas import ProductCreate, ProductUpdate


def generate_sku(name: str) -> str:
    """
    Generate a SKU from the product name + 6 random hex chars.
    Example: "Laptop Pro" -> "LAP-PRO-a3f9c1"
    """
    prefix = "-".join(word[:3].upper() for word in name.split()[:2])
    suffix = uuid.uuid4().hex[:6].upper()
    return f"{prefix}-{suffix}"


def get_product(db: Session, product_id: int) -> Product:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found."
        )
    return product


def get_products(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Product).offset(skip).limit(limit).all()


def create_product(db: Session, data: ProductCreate) -> Product:
    # Generate a unique SKU (retry on collision, extremely unlikely)
    for _ in range(5):
        sku = generate_sku(data.name)
        if not db.query(Product).filter(Product.sku == sku).first():
            break

    product = Product(
        name=data.name,
        sku=sku,
        price=data.price,
        quantity=data.quantity,
        description=data.description,
    )
    db.add(product)
    try:
        db.commit()
        db.refresh(product)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Failed to generate a unique SKU, please try again."
        )
    return product


def update_product(db: Session, product_id: int, data: ProductUpdate) -> Product:
    product = get_product(db, product_id)
    update_data = data.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product_id: int) -> dict:
    product = get_product(db, product_id)
    db.delete(product)
    db.commit()
    return {"detail": f"Product '{product.name}' (SKU: {product.sku}) deleted successfully."}