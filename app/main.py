from fastapi import FastAPI
from app.api import auth_api,user_api
app=FastAPI()
app.include_router(auth_api.router)
app.include_router(user_api.router)
@app.get("/")
def home():
    return {"message": "Ecommerce API running"}