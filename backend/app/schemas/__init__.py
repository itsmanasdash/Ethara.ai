from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# ──────────────────────────────────────────
# Product Schemas
# ──────────────────────────────────────────

class ProductCreate(BaseModel):
    """User only provides name, price, quantity, description. SKU is auto-generated."""
    name: str = Field(..., min_length=1, max_length=255)
    price: float = Field(..., gt=0)
    quantity: int = Field(..., ge=0)
    description: Optional[str] = None


class ProductUpdate(BaseModel):
    """All fields optional for partial updates. SKU cannot be changed."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    price: Optional[float] = Field(None, gt=0)
    quantity: Optional[int] = Field(None, ge=0)
    description: Optional[str] = None


class ProductResponse(BaseModel):
    id: int
    name: str
    sku: str
    price: float
    quantity: int
    description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ──────────────────────────────────────────
# Customer Schemas
# ──────────────────────────────────────────

class CustomerCreate(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=50)


class CustomerResponse(CustomerCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ──────────────────────────────────────────
# Order Schemas
# ──────────────────────────────────────────

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: float
    product: Optional[ProductResponse] = None

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    customer_id: int
    items: List[OrderItemCreate] = Field(..., min_length=1)
    notes: Optional[str] = None


class OrderResponse(BaseModel):
    id: int
    customer_id: int
    status: str
    total_amount: float
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    customer: Optional[CustomerResponse] = None
    items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True


# ──────────────────────────────────────────
# Dashboard Schema
# ──────────────────────────────────────────

class DashboardResponse(BaseModel):
    total_products: int
    total_customers: int
    total_orders: int
    low_stock_products: List[ProductResponse]