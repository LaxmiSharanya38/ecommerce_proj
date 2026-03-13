from app.models.category import Category
from sqlalchemy.orm import Session
from app.schemas.category import CategoryCreate,CategoryUpdate
from fastapi import HTTPException
from uuid import UUID   
import uuid

def create_category(db: Session, data: CategoryCreate):

    existing = db.query(Category).filter(
        Category.name.ilike(data.name)
    ).first()

    if existing:
        raise HTTPException(400, "Category already exists")

    if data.parent_id:
        parent = db.query(Category).filter(
            Category.id == data.parent_id
        ).first()

        if not parent:
            raise HTTPException(404, "Parent category not found")

    category = Category(
        id=uuid.uuid4(),
        name=data.name,
        parent_id=data.parent_id
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    return category
def update_category(db: Session, category_id: UUID, data: CategoryUpdate):

    category = db.query(Category).filter(
        Category.id == category_id
    ).first()

    if not category:
        raise HTTPException(404, "Category not found")

    if data.name:
        category.name = data.name

    if data.parent_id:

        parent = db.query(Category).filter(
            Category.id == data.parent_id
        ).first()

        if not parent:
            raise HTTPException(404, "Parent category not found")

        category.parent_id = data.parent_id

    db.commit()
    db.refresh(category)

    return category
def delete_category(db: Session, category_id: UUID):

    category = db.query(Category).filter(
        Category.id == category_id
    ).first()

    if not category:
        raise HTTPException(404, "Category not found")

    children = db.query(Category).filter(
        Category.parent_id == category_id
    ).first()

    if children:
        raise HTTPException(
            400,
            "Cannot delete category with subcategories"
        )

    db.delete(category)
    db.commit()

    return {"message": "Category deleted successfully"}

def build_category_tree(categories, parent_id=None):

    tree = []

    for cat in categories:
        if cat.parent_id == parent_id:

            children = build_category_tree(categories, cat.id)

            tree.append({
                "id": cat.id,
                "name": cat.name,
                "children": children
            })

    return tree


def get_category_catalog(db: Session):

    categories = db.query(Category).all()

    catalog = build_category_tree(categories)

    return catalog
