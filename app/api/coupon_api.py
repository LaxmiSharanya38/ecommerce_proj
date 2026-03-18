from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.utils.dependencies import get_current_user
from app.services.coupon_service import (
    create_coupon,
    list_coupons,
    get_coupon,
    update_coupon,
    disable_coupon,apply_coupon_to_cart
)
from app.schemas.coupon_schema import (
    CouponCreate,
    CouponUpdate,
    CouponResponse
)

router = APIRouter(prefix="/coupons", tags=["Coupons"])
@router.post("", response_model=CouponResponse)
def create_coupon_api(
    data: CouponCreate,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    return create_coupon(db, data)

@router.get("", response_model=List[CouponResponse])
def list_coupons_api(
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    return list_coupons(db)

@router.get("/{coupon_id}", response_model=CouponResponse)
def get_coupon_api(
    coupon_id: UUID,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    return get_coupon(db, coupon_id)

@router.delete("/{coupon_id}", response_model=CouponResponse)
def disable_coupon_api(
    coupon_id: UUID,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    return disable_coupon(db, coupon_id)
@router.post("/apply")
def apply_coupon(
    coupon_code: str,
    cart_total: float,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):

    return apply_coupon_to_cart(
        db=db,
        coupon_code=coupon_code,
        user_id=user.id,
        cart_total=cart_total
    )