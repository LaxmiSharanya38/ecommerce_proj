from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services.order_service import create_order_from_cart
from app.database import get_db
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.product import Product
from app.models.inventory import Inventory
from app.utils.dependencies import get_current_user
from app.schemas.order_schema import CreateOrderFromCartService
from uuid import UUID
from app.services.order_service import get_order_details,get_user_orders,cancel_order

router = APIRouter(prefix="/cart", tags=["Cart"])

@router.post("/create-order")
def create_cart(
    data: CreateOrderFromCartService,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return create_order_from_cart(db,current_user.id,data.address_id)





@router.get("/myorders")
def get_my_orders(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return get_user_orders(
        db,
        current_user.id,
        page,
        limit
    )
@router.get("/{order_id}")
def view_order_details(
    order_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return get_order_details(
        db,
        order_id,
        current_user.id
    )
@router.post("/{order_id}/cancel")
def cancel_user_order(
    order_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return cancel_order(
        db,
        current_user.id,
        order_id
    )