from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.orm import Session
from app.models.users import User

from app.database import get_db
from app.schemas.address_schema import AddressCreate,AddressUpdate,AddressResponse
from app.crud.address_crud import create_address, get_user_addresses,delete_address,set_default_address,update_user_address
from app.utils.dependencies import get_current_user
from uuid import UUID
router = APIRouter(prefix="/addresses", tags=["Addresses"])

#to add the addresses
@router.post("/")
def add_address(
    address: AddressCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return create_address(db, user.id, address.dict())

#to show list of addresses
@router.get("/")
def list_addresses(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return get_user_addresses(db, user.id)
#to delete a address
@router.delete("/{address_id}", response_model=AddressResponse)
def remove_address(
    address_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return delete_address(db, address_id, user.id)

#to set previous address as default address

@router.post("/{address_id}/set-default")
def change_default_address(
    address_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):

    address = set_default_address(db, user.id, address_id)

    if not address:
        raise HTTPException(status_code=404, detail="Address not found")

    return {
        "message": "Default address updated successfully",
        "address": address
    }
#to update any address related to user but not changing default param
@router.post("/{address_id}/update")
def update_address(
    address_id: UUID,
    address: AddressUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):

    updated_address = update_user_address(
        db,
        user.id,
        address_id,
        address
    )

    if not updated_address:
        raise HTTPException(status_code=404, detail="Address not found")

    return updated_address