
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from uuid import UUID
from app.models.coupon_usage import CouponUsage
from app.models.coupon import Coupon
from app.schemas.coupon_schema import CouponCreate, CouponUpdate
from datetime import date
from decimal import Decimal
from app.enums.discount_enum import DiscountType

def create_coupon(db: Session, data: CouponCreate) -> Coupon:
    existing = (
        db.query(Coupon)
        .filter(Coupon.code == data.code)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Coupon code already exists",
        )

    coupon = Coupon(**data.model_dump())

    db.add(coupon)
    db.commit()
    db.refresh(coupon)

    return coupon
def list_coupons(db: Session):
    coupons = (
        db.query(Coupon)
        .order_by(Coupon.created_at.desc())
        .all()
    )

    return coupons


def get_coupon(db: Session, coupon_id: UUID) -> Coupon:

    coupon = (
        db.query(Coupon)
        .filter(Coupon.id == coupon_id)
        .first()
    )

    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coupon not found",
        )

    return coupon


def update_coupon(db: Session, data: CouponUpdate):

    coupon = (
        db.query(Coupon)
        .filter(Coupon.code == data.code)
        .first()
    )

    if not coupon:
        raise HTTPException(status_code=404, detail="Coupon not found")

    update_data = data.model_dump(exclude_unset=True)

    update_data.pop("code", None)

    for field, value in update_data.items():
        setattr(coupon, field, value)

    db.commit()
    db.refresh(coupon)

    return coupon
def disable_coupon(db: Session, coupon_id: UUID) -> Coupon:

    coupon = get_coupon(db, coupon_id)

    coupon.is_active = False

    db.commit()
    db.refresh(coupon)

    return coupon
def validate_coupon(
    db: Session,
    coupon_code: str,
    user_id,
    cart_total
):

    coupon = (
        db.query(Coupon)
        .filter(Coupon.code == coupon_code)
        .first()
    )

    if not coupon:
        raise HTTPException(404, "Invalid coupon")

    if not coupon.is_active:
        raise HTTPException(400, "Coupon is inactive")

    if coupon.expiry_date < date.today():
        raise HTTPException(400, "Coupon expired")

    if cart_total < coupon.min_order_amount:
        raise HTTPException(
            400,
            f"Minimum order amount is {coupon.min_order_amount}"
        )

    if coupon.usage_limit is not None:
        total_usage = (
            db.query(CouponUsage)
            .filter(CouponUsage.coupon_id == coupon.id)
            .count()
        )

        if total_usage >= coupon.usage_limit:
            raise HTTPException(400, "Coupon usage limit reached")

    user_usage = (
        db.query(CouponUsage)
        .filter(
            CouponUsage.coupon_id == coupon.id,
            CouponUsage.user_id == user_id
        )
        .count()
    )

    if user_usage > 0:
        raise HTTPException(400, "Coupon already used")

    return coupon


def calculate_discount(coupon, cart_total: Decimal):

    if coupon.discount_type == DiscountType.PERCENTAGE:
        discount = (cart_total * coupon.discount_value) / Decimal(100)

    elif coupon.discount_type == DiscountType.FLAT:
        discount = coupon.discount_value

    else:
        discount = Decimal(0)

    # Prevent negative totals
    discount = min(discount, cart_total)

    final_total = Decimal(cart_total) - Decimal(discount)

    return {
        "discount": discount,
        "final_total": final_total
    }



def apply_coupon_to_cart(
    db,
    coupon_code,
    user_id,
    cart_total
):

    coupon = validate_coupon(
        db,
        coupon_code,
        user_id,
        cart_total
    )

    pricing = calculate_discount(coupon, cart_total)

    return {
        "coupon_code": coupon.code,
        "discount": pricing["discount"],
        "final_total": pricing["final_total"]
    }