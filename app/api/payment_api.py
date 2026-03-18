import hmac
import hashlib
import razorpay
import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.utils.dependencies import get_current_user
from app.models.users import User
from app.models.orders import Order
from app.models.payments import Payment

from app.enums.order_status import OrderStatus
from app.enums.payment_status import PaymentStatus

from app.config import (
    RAZORPAY_KEY_ID,
    RAZORPAY_KEY_SECRET,
    RAZORPAY_WEBHOOK_SECRET
)
client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

router = APIRouter(prefix="/payments", tags=["Payments"])
def get_user_order(db: Session, order_id, user_id):

    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == user_id
    ).first()

    if not order:
        raise HTTPException(404, "Order not found")

    return order

@router.post("/create/{order_id}")
def create_payment(
    order_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    order = get_user_order(db, order_id, current_user.id)

    # Only unpaid orders allowed
    if order.order_status != OrderStatus.CREATED:
        raise HTTPException(
            status_code=400,
            detail="Payment already processed or invalid order state"
        )

    try:
        # Create Razorpay Order
        razorpay_order = client.order.create({
            "amount": int(order.final_amount * 100),  # paise
            "currency": "INR",
            "receipt": str(order.id),
            "payment_capture": 1
        })

        payment = Payment(
            id=uuid.uuid4(),
            order_id=order.id,
            provider="razorpay",
            payment_status=PaymentStatus.PENDING,
            transaction_id=razorpay_order["id"],
            amount=order.final_amount
        )

        db.add(payment)
        db.commit()

        return {
            "message": "Payment order created",
            "razorpay_order_id": razorpay_order["id"],
            "key": RAZORPAY_KEY_ID,
            "amount": razorpay_order["amount"],
            "currency": "INR"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Payment creation failed: {str(e)}"
        )
#  GET USER PAYMENTS (Authenticated)

@router.get("/")
def get_my_payments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    payments = (
        db.query(Payment)
        .join(Order, Order.id == Payment.order_id)
        .filter(Order.user_id == current_user.id)
        .all()
    )

    return [
        {
            "order_id": p.order_id,
            "provider": p.provider,
            "status": p.payment_status,
            "amount": float(p.amount),
            "transaction_id": p.transaction_id
        }
        for p in payments
    ]
