from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user_schema import UserCreate,UserLogin

from app.crud.user_crud import create_user, get_user_by_email
from app.utils.security import hash_password, create_access_token,verify_password


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

    token = create_access_token(
        {"sub": str(db_user.id)}
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }
