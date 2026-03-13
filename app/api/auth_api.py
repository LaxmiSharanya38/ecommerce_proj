from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user_schema import UserCreate,UserLogin,RefreshTokenRequest

from app.crud.user_crud import create_user, get_user_by_email
from app.utils.security import hash_password, create_access_token,verify_password,decode_refresh_token,create_refresh_token


from fastapi import APIRouter

router = APIRouter()

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):

    existing_user = get_user_by_email(db, user.email)

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    user_data = user.dict()

    user_data["password_hash"] = hash_password(user_data.pop("password"))

    new_user = create_user(db, user_data)

    return {"message": "User created successfully"}
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):

    db_user = get_user_by_email(db, user.email)

    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid email")

    if not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid password")

    access_token = create_access_token(
        {"sub": str(db_user.id)}
    )

   
    refresh_token = create_refresh_token({
        "sub": str(db_user.id)
    })

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
@router.post("/refresh")
def refresh_token(data: RefreshTokenRequest):

    user_id = decode_refresh_token(data.refresh_token)

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

    new_access_token = create_access_token({
        "sub": user_id
    })

    return {
        "access_token": new_access_token
    }