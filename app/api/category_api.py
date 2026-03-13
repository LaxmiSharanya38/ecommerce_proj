from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID, uuid4
from typing import Optional, List
from pydantic import BaseModel
from app.schemas.category import CategoryResponse,CategoryCreate,CategoryUpdate
from app.services.category_service import create_category,update_category,delete_category,get_category_catalog

from app.database import get_db
from app.models.category import Category
from app.utils.dependencies import get_current_user
from app.models.users import User

router = APIRouter(prefix="/categories", tags=["Categories"])
@router.post("/create", response_model=CategoryResponse)
def create_category_api(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if not current_user:
        raise HTTPException(401, "Unauthorized")

    return create_category(db, category)
@router.post("/update/{category_id}", response_model=CategoryResponse)
def update_category_api(
    category_id: UUID,
    category: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if not current_user:
        raise HTTPException(401, "Unauthorized")

    return update_category(db, category_id, category)
@router.delete("/delete/{category_id}")
def delete_category_api(
    category_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if not current_user:
        raise HTTPException(401, "Unauthorized")

    return delete_category(db, category_id)
@router.get("/catalog")
def get_category_catalog_api(
    db: Session = Depends(get_db)
):

    return get_category_catalog(db)
