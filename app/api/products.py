from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID   

from app.database import get_db
from app.schemas.product import ProductCreate, ProductResponse,ProductUpdate
from app.services.product_service import create_product,update_product
from app.utils.dependencies import get_current_user
from app.models.users import User

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


@router.post("/", response_model=ProductResponse)
def add_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return create_product(db, product)

@router.post("/update/{product_id}", response_model=ProductResponse)
def update_product_api(
    product_id: UUID,
    product: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # authentication required
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return update_product(db, product_id, product)


