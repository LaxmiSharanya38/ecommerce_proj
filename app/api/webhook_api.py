# app/api/webhook_api.py

import hmac
import hashlib
import json

from fastapi import APIRouter, Request, HTTPException,Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.payments import Payment
from app.models.orders import Order
from app.enums.order_status import OrderStatus
from app.enums.payment_status import PaymentStatus
from app.config import RAZORPAY_WEBHOOK_SECRET
from app.database import get_db

router = APIRouter()

@router.post("/webhook")
async def razorpay_webhook(
    request: Request,
    db: Session = Depends(get_db)
):

    body = await request.body()
    signature = request.headers.get("X-Razorpay-Signature")

    # Verify Webhook Signature (SECURITY)
    generated_signature = hmac.new(
        bytes(RAZORPAY_WEBHOOK_SECRET, "utf-8"),
        body,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(generated_signature, signature):
        raise HTTPException(400, "Invalid webhook signature")

    payload = await request.json()
    event = payload.get("event")

    # PAYMENT SUCCESS EVENT
    if event == "payment.captured":

        payment_entity = payload["payload"]["payment"]["entity"]
        razorpay_order_id = payment_entity["order_id"]

        payment = db.query(Payment).filter(
            Payment.transaction_id == razorpay_order_id
        ).first()

        if payment:

            payment.payment_status = PaymentStatus.SUCCESS

            order = db.query(Order).filter(
                Order.id == payment.order_id
            ).first()

            if order:
                order.order_status = OrderStatus.PAID

            db.commit()

    # PAYMENT FAILED EVENT
    elif event == "payment.failed":

        payment_entity = payload["payload"]["payment"]["entity"]
        razorpay_order_id = payment_entity["order_id"]

        payment = db.query(Payment).filter(
            Payment.transaction_id == razorpay_order_id
        ).first()

        if payment:
            payment.payment_status = PaymentStatus.FAILED
            db.commit()

    return {"status": "webhook processed"}