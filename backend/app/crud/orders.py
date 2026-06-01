from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from app.models import Order, OrderItem, Product, Customer
from app.schemas import OrderCreate


def get_order(db: Session, order_id: int) -> Order:
    order = (
        db.query(Order)
        .options(
            joinedload(Order.customer),
            joinedload(Order.items).joinedload(OrderItem.product),
        )
        .filter(Order.id == order_id)
        .first()
    )
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {order_id} not found."
        )
    return order


def get_orders(db: Session, skip: int = 0, limit: int = 100):
    return (
        db.query(Order)
        .options(
            joinedload(Order.customer),
            joinedload(Order.items).joinedload(OrderItem.product),
        )
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_order(db: Session, data: OrderCreate) -> Order:
    # 1. Validate customer exists
    customer = db.query(Customer).filter(Customer.id == data.customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with id {data.customer_id} not found."
        )

    # 2. Validate all products and stock in a single pass
    resolved_items = []
    for item in data.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {item.product_id} not found."
            )
        if product.quantity < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    f"Insufficient stock for '{product.name}' (SKU: {product.sku}). "
                    f"Requested: {item.quantity}, Available: {product.quantity}."
                )
            )
        resolved_items.append((product, item.quantity))

    # 3. Create order
    order = Order(
        customer_id=data.customer_id,
        notes=data.notes,
        status="pending",
        total_amount=0.0,
    )
    db.add(order)
    db.flush()  # Get order.id without committing

    # 4. Create order items, deduct stock, and calculate total
    total = 0.0
    for product, qty in resolved_items:
        unit_price = product.price
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=qty,
            unit_price=unit_price,
        )
        db.add(order_item)
        product.quantity -= qty          # Deduct stock atomically
        total += unit_price * qty

    order.total_amount = round(total, 2)

    db.commit()
    db.refresh(order)

    # Return fully loaded order
    return get_order(db, order.id)


def delete_order(db: Session, order_id: int) -> dict:
    """Cancel an order and restore inventory."""
    order = get_order(db, order_id)

    # Restore stock for each item
    for item in order.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:
            product.quantity += item.quantity

    db.delete(order)
    db.commit()
    return {"detail": f"Order #{order_id} cancelled and inventory restored."}