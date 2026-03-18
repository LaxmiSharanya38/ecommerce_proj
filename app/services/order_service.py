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
from app.enums.order_status import OrderStatus,RefundStatus
import uuid
from sqlalchemy.orm import Session,joinedload
from fastapi import HTTPException
from datetime import datetime
from sqlalchemy import func
from app.models.coupon import Coupon
from decimal import Decimal
from datetime import date
from app.services.coupon_service import validate_coupon
from app.models.coupon_usage import CouponUsage


def create_order_from_cart(db: Session, user_id, address_id):

    try:

        address = db.query(Address).filter(
            Address.id == address_id,
            Address.user_id == user_id
        ).first()

        if not address:
            raise HTTPException(404, "Address not found")

        cart = db.query(Cart).filter(
            Cart.user_id == user_id
        ).first()

        if not cart:
            raise HTTPException(400, "Cart not found")

        cart_items = db.query(CartItem).filter(
            CartItem.cart_id == cart.id
        ).all()

        if not cart_items:
            raise HTTPException(400, "Cart empty")

        coupon = cart.coupon

        if coupon:
            validate_coupon(
                db,
                coupon.code,
                user_id,
                cart.total_amount
            )

        total_amount = cart.total_amount
        discount_amount = cart.discount_amount or 0
        final_amount = cart.final_amount or total_amount

        order = Order(
            id=uuid.uuid4(),
            user_id=user_id,
            address_id=address_id,
            order_status=OrderStatus.CREATED,
            total_amount=total_amount,
            discount_amount=discount_amount,
            final_amount=final_amount,
            coupon_id=cart.coupon_id,
            coupon_code=coupon.code if coupon else None,
            created_at=datetime.utcnow()
        )

        db.add(order)
        db.flush()

        for item in cart_items:

            order_item = OrderItem(
                id=uuid.uuid4(),
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.price_at_time,
                subtotal=item.price_at_time * item.quantity
            )

            db.add(order_item)

        if coupon:
            usage = CouponUsage(
                user_id=user_id,
                coupon_id=coupon.id,
                order_id=order.id
            )
            db.add(usage)

        db.query(CartItem).filter(
            CartItem.cart_id == cart.id
        ).delete()

        cart.coupon_id = None
        cart.discount_amount = 0
        cart.final_amount = None

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
       payment_data = [
    {
        "provider": p.provider,
        "status": p.payment_status,
        "transaction_id": p.transaction_id,
        "amount": float(p.amount)
    }
    for p in order.payments
]

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
    "coupon_code": order.coupon_code,
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

    try:
        order = db.query(Order).filter(
            Order.id == order_id,
            Order.user_id == user_id
        ).first()

        if not order:
            raise HTTPException(404, "Order not found")

        if order.order_status == OrderStatus.CANCELLED:
            raise HTTPException(400, "Order already cancelled")

        if order.order_status in [
            OrderStatus.SHIPPED,
            OrderStatus.DELIVERED
        ]:
            raise HTTPException(
                400,
                "Order cannot be cancelled after shipping"
            )

        if order.refund_status == RefundStatus.PENDING:
            raise HTTPException(
                400,
                "Refund already in process for this order"
            )

        # ---------- RESTORE INVENTORY ----------
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

        # ---------- RESTORE COUPON USAGE ----------
        usage = db.query(CouponUsage).filter(
            CouponUsage.order_id == order.id
        ).first()

        if usage:
            db.delete(usage)
            # usage_limit auto restored because count reduces

        # ---------- UPDATE ORDER STATUS ----------
        original_status = order.order_status

        order.order_status = OrderStatus.CANCELLED
        order.cancelled_at = datetime.utcnow()

        if original_status == OrderStatus.PAID:
            order.refund_status = RefundStatus.PENDING

        db.commit()

        return {"message": "Order cancelled successfully"}

    except HTTPException as he:
        raise he

    except Exception as e:
        db.rollback()
        raise HTTPException(
            500,
            f"Failed to cancel order: {str(e)}"
        )