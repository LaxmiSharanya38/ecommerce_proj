from fastapi import FastAPI
from app.api import auth_api,user_api,address_api
app=FastAPI()
from app.api import user_api

app.include_router(user_api.router)
app.include_router(auth_api.router)
app.include_router(user_api.router)
app.include_router(address_api.router)

@app.get("/")
def home():
    return {"message": "Ecommerce API running"}