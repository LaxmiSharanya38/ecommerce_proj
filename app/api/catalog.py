from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.database import get_db
from app.services.catalog_service import get_products,get_product_details

router = APIRouter(
    prefix="/catalog",
    tags=["Product Catalog"]
)

#product with pagination  and specific category id or search or sort or all products
@router.get("/products")
def list_products(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    category_id: Optional[UUID] = None,
    search: Optional[str] = None,
    sort: Optional[str] = Query(
        None,
        description="price_asc | price_desc | newest"
    ),
    db: Session = Depends(get_db)
):
    return get_products(
        db=db,
        page=page,
        limit=limit,
        category_id=category_id,
        search=search,
        sort=sort
    )

@router.get("/products/{product_id}")
def product_details(
    product_id: UUID,
    db: Session = Depends(get_db)
):
    return get_product_details(db, product_id)