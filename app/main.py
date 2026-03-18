from fastapi import FastAPI,Depends
from app.api import user_api
from sqlalchemy.orm import Session
from sqlalchemy.orm import Session
from app.services.catalog_service import get_products
from app.database import get_db
from app.api import products
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
from app.api import auth_api,user_api,address_api,cart_api,catalog,category_api,orders_api,payment_api,webhook_api,coupon_api

app.include_router(user_api.router)
app.include_router(auth_api.router)
app.include_router(user_api.router)
app.include_router(address_api.router)
app.include_router(cart_api.router)
app.include_router(catalog.router)
app.include_router(products.router)
app.include_router(category_api.router)
app.include_router(orders_api.router)
app.include_router(payment_api.router)
app.include_router(webhook_api.router)
app.include_router(coupon_api.router)


@app.get("/")
def home():
    return {"message": "Ecommerce API running"}


