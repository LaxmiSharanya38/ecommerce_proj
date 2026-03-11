from fastapi import Depends
from app.utils.dependencies import get_current_user
from fastapi import APIRouter,HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user_schema import ChangePasswordRequest,DeleteUserRequest
from app.crud.user_crud import change_user_password,delete_user_account
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])
#show user
@router.get("/me")
def get_profile(current_user = Depends(get_current_user)):

    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email
    }

#change password new and old passwords shouldn't match
@router.post("/changepassword")
def change_password(
    data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):

    try:
        return change_user_password(
            db,
            user.id,
            data.old_password,
            data.new_password
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
#delete the user from db
@router.delete("/delete-account")
def delete_account(
    data: DeleteUserRequest,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    try:
        return delete_user_account(db, user.id, data.password)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))