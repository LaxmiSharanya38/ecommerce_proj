from sqlalchemy.orm import Session
from fastapi import HTTPException
from uuid import UUID
from decimal import Decimal

from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.services.coupon_service import validate_coupon, calculate_discount

def apply_coupon_to_cart(db: Session, user_id: UUID, coupon_code: str):

    cart = db.query(Cart).filter(Cart.user_id == user_id).first()

    if not cart:
        raise HTTPException(404, "Cart not found")

    cart_items = db.query(CartItem).filter(
        CartItem.cart_id == cart.id
    ).all()

    if not cart_items:
        raise HTTPException(400, "Cart is empty")

    cart_total = sum(
        Decimal(item.price_at_time) * item.quantity
        for item in cart_items
    )

    coupon = validate_coupon(
        db,
        coupon_code,
        user_id,
        cart_total
    )

    result = calculate_discount(coupon, cart_total)

    cart.coupon_id = coupon.id
    cart.discount_amount = result["discount"]
    cart.final_amount = result["final_total"]

    db.commit()
    db.refresh(cart)

    return {
        "message": "Coupon applied successfully",
        "discount": float(cart.discount_amount),
        "final_amount": float(cart.final_amount)
    }
def remove_coupon_from_cart(db: Session, user_id: UUID):

    cart = db.query(Cart).filter(Cart.user_id == user_id).first()

    if not cart:
        raise HTTPException(404, "Cart not found")

    cart.coupon_id = None
    cart.discount_amount = 0
    cart.final_amount = cart.total_amount

    db.commit()

    return {"message": "Coupon removed successfully"}