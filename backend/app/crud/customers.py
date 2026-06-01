from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models import Customer
from app.schemas import CustomerCreate


def get_customer(db: Session, customer_id: int) -> Customer:
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with id {customer_id} not found."
        )
    return customer


def get_customer_by_email(db: Session, email: str) -> Customer | None:
    return db.query(Customer).filter(Customer.email == email.lower()).first()


def get_customers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Customer).offset(skip).limit(limit).all()


def create_customer(db: Session, data: CustomerCreate) -> Customer:
    if get_customer_by_email(db, data.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Customer with email '{data.email}' already exists."
        )
    customer = Customer(**data.dict())
    db.add(customer)
    try:
        db.commit()
        db.refresh(customer)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email must be unique."
        )
    return customer


def delete_customer(db: Session, customer_id: int) -> dict:
    customer = get_customer(db, customer_id)
    db.delete(customer)
    db.commit()
    return {"detail": f"Customer '{customer.full_name}' deleted successfully."}