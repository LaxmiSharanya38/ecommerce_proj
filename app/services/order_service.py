# services/order_service.py
from app.models.inventory import Inventory
from app.models.address import Address
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.product import Product
from app.models.orders import Order
from app.models.orderitem import OrderItem
from app.models.payments import Payment
from app.models.shipment import Shipment
from app.models.invoice import Invoice
from uuid import UUID
from app.enums.order_status import OrderStatus
import uuid
from sqlalchemy.orm import Session,joinedload
from fastapi import HTTPException
from datetime import datetime
from sqlalchemy import func

def create_order_from_cart(db: Session, user_id, address_id):

    try:

        # Validate address
        address = db.query(Address).filter(
            Address.id == address_id,
            Address.user_id == user_id
        ).first()

        if not address:
            raise HTTPException(
                status_code=404,
                detail="Address not found"
            )

        # Get cart
        cart = db.query(Cart).filter(
            Cart.user_id == user_id
        ).first()

        if not cart:
            raise HTTPException(
                status_code=400,
                detail="Cart not found"
            )

        cart_items = db.query(CartItem).filter(
            CartItem.cart_id == cart.id
        ).all()

        if not cart_items:
            raise HTTPException(
                status_code=400,
                detail="Cart is empty"
            )

        #  Calculate totals
        total_amount = 0
        order_items_data = []

        for item in cart_items:

            product = db.query(Product).filter(
                Product.id == item.product_id
            ).first()

            inventory = db.query(Inventory).filter(
                Inventory.product_id == product.id
            ).first()

            if not inventory:
                raise HTTPException(
                    status_code=400,
                    detail=f"Inventory missing for product {product.id}"
                )

            # verify reserved stock
            if inventory.reserved_quantity < item.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Stock reservation mismatch for {product.name}"
                )

            subtotal = item.price_at_time * item.quantity
            total_amount += subtotal

            order_items_data.append({
                "product": product,
                "quantity": item.quantity,
                "price": item.price_at_time,
                "subtotal": subtotal,
                "inventory": inventory
            })

        # Create order
        order = Order(
            id=uuid.uuid4(),
            user_id=user_id,
            address_id=address_id,
            order_status=OrderStatus.CREATED,
            total_amount=total_amount,
            discount_amount=0,
            final_amount=total_amount,
            created_at=datetime.utcnow()
        )

        db.add(order)
        db.flush()

        # Create order items
        for data in order_items_data:
            order_item = OrderItem(
                id=uuid.uuid4(),
                order_id=order.id,
                product_id=data["product"].id,
                quantity=data["quantity"],
                price=data["price"],
                subtotal=data["subtotal"]
            )

            db.add(order_item)

            inventory = data["inventory"]

            inventory.reserved_quantity -= data["quantity"]
            inventory.quantity_available -= data["quantity"]

            remaining_stock = (
                inventory.quantity_available - inventory.reserved_quantity
            )

            if remaining_stock <= 0:
                data["product"].is_active = False

        #Clear cart
        db.query(CartItem).filter(
            CartItem.cart_id == cart.id
        ).delete()

        # Commit transaction
        db.commit()
        db.refresh(order)

        return {
            "message": "Order created successfully",
            "order_id": order.id,
            "final_amount": float(order.final_amount)
        }

    except Exception as e:
        db.rollback()
        raise e



def get_order_details(
    db: Session,
    order_id: UUID,
    user_id: UUID
):

    # fetch order with relationships
    order = (
        db.query(Order)
        .options(
            joinedload(Order.items)
            .joinedload(OrderItem.product),

            joinedload(Order.payments),
            joinedload(Order.shipment),
            joinedload(Order.invoice)
        )
        .filter(
            Order.id == order_id,
            Order.user_id == user_id 
        )
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    # ---------- order items ----------
    items = []

    for item in order.items:
        items.append({
            "product_id": item.product_id,
            "product_name": item.product.name,
            "quantity": item.quantity,
            "price": float(item.price),
            "subtotal": float(item.subtotal)
        })

    # ---------- payment ----------
    payment_data = None
    if order.payments:
        payment_data = {
            "provider": order.payments.provider,
            "status": order.payments.payment_status,
            "transaction_id": order.payments.transaction_id,
            "amount": float(order.payments.amount)
        }

    # ---------- shipment ----------
    shipment_data = None
    if order.shipment:
        shipment_data = {
            "courier_name": order.shipment.courier_name,
            "tracking_number": order.shipment.tracking_number,
            "shipment_status": order.shipment.shipment_status
        }

    # ---------- invoice ----------
    invoice_data = None
    if order.invoice:
        invoice_data = {
            "invoice_number": order.invoice.invoice_number,
            "invoice_url": order.invoice.invoice_url,
            "generated_at": order.invoice.generated_at
        }

    # ---------- final response ----------
    return {
        "order_id": order.id,
        "order_status": order.order_status,
        "total_amount": float(order.total_amount),
        "discount_amount": float(order.discount_amount),
        "final_amount": float(order.final_amount),
        "created_at": order.created_at,
        "items": items,
        "payment": payment_data,
        "shipment": shipment_data,
        "invoice": invoice_data
    }
def update_order_status(db: Session, order_id: int, new_status: OrderStatus):

    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(404, "Order not found")
    order.order_status = new_status
    db.commit()
    db.refresh(order)
    return order


def get_user_orders(
    db: Session,
    user_id,
    page: int = 1,
    limit: int = 10
):
    offset = (page - 1) * limit

    orders = (
        db.query(
            Order.id,
            Order.order_status,
            Order.final_amount,
            Order.created_at,
            func.sum(OrderItem.quantity).label("total_items")
        )
        .join(OrderItem, OrderItem.order_id == Order.id)
        .filter(Order.user_id == user_id)
        .group_by(Order.id)
        .order_by(Order.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return [
        {
            "order_id": o.id,
            "order_status": o.order_status,
            "final_amount": float(o.final_amount),
            "total_items": o.total_items,
            "created_at": o.created_at,
        }
        for o in orders
    ]
def cancel_order(db: Session, user_id, order_id):

    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == user_id
    ).first()

    if not order:
        raise HTTPException(404, "Order not found")

    if order.order_status not in [
    OrderStatus.CREATED,
    OrderStatus.PAYMENT_PENDING
]:        raise HTTPException(
            400,
            "Order cannot be cancelled"
        )

    # restore inventory
    order_items = db.query(OrderItem).filter(
        OrderItem.order_id == order.id
    ).all()

    for item in order_items:

        inventory = db.query(Inventory).filter(
            Inventory.product_id == item.product_id
        ).first()

        product = db.query(Product).filter(
            Product.id == item.product_id
        ).first()

        inventory.quantity_available += item.quantity

        if inventory.quantity_available > 0:
            product.is_active = True

    # update order status
    order.order_status = "CANCELLED"
    order.cancelled_at = datetime.utcnow()

    db.commit()

    return {"message": "Order cancelled successfully"}

