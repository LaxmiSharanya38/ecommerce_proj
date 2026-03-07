from fastapi import Depends
from app.utils.dependencies import get_current_user
from fastapi import APIRouter

router = APIRouter()

@router.get("/users/me")
def get_profile(current_user = Depends(get_current_user)):

    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email
    }