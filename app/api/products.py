from fastapi import APIRouter, Depends, HTTPException,UploadFile,File
from sqlalchemy.orm import Session
from uuid import UUID   

from app.database import get_db
from app.schemas.product import ProductCreate, ProductResponse,BulkProductUpdate
from app.services.product_service import create_product,bulk_update_products,delete_product,upload_products_service
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

@router.post("/products/bulk-update")
def update_products(
    data: BulkProductUpdate,
    db: Session = Depends(get_db)
):
    return bulk_update_products(db, data)
#along with product inventory also get deleted
@router.delete("/delete/{product_id}")
def delete_product_api(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return delete_product(db, product_id)

#Adding the products through csv file
@router.post("/upload-products")
def upload_products(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return upload_products_service(file, db)
