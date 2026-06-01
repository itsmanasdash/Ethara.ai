from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Product, Customer, Order
from app.schemas import DashboardResponse, ProductResponse

router = APIRouter()

LOW_STOCK_THRESHOLD = 10


@router.get("/", response_model=DashboardResponse)
def get_dashboard(db: Session = Depends(get_db)):
    """
    Return summary statistics:
    - Total products, customers, orders
    - Products with quantity <= 10 (low stock)
    """
    total_products = db.query(Product).count()
    total_customers = db.query(Customer).count()
    total_orders = db.query(Order).count()
    low_stock = (
        db.query(Product)
        .filter(Product.quantity <= LOW_STOCK_THRESHOLD)
        .order_by(Product.quantity.asc())
        .all()
    )

    return DashboardResponse(
        total_products=total_products,
        total_customers=total_customers,
        total_orders=total_orders,
        low_stock_products=[ProductResponse.from_orm(p) for p in low_stock],
    )