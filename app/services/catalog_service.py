from sqlalchemy.orm import Session
from sqlalchemy import asc, desc, or_, text
from app.models.product import Product
from app.models.category import Category
from app.models.inventory import Inventory
from app.models.product_images import ProductImage
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func

def get_products(
    db: Session,
    page: int = 1,
    limit: int = 10,
    category_id=None,
    search: str | None = None,
    sort: str | None = None
):

    offset = (page - 1) * limit

    query = (
        db.query(
            Product.id,
            Product.name,
            Product.description,
            Product.category_id,
            Category.name.label("category"),
            Product.price,
            Inventory.quantity_available,
            Inventory.reserved_quantity,
            ProductImage.image_url
        )
        .join(Category, Product.category_id == Category.id)
        .join(Inventory, Inventory.product_id == Product.id)
        .join(ProductImage, ProductImage.product_id == Product.id)
        .filter(Product.is_active == True)
        .filter(
            (Inventory.quantity_available -
             Inventory.reserved_quantity) > 0
        )
    )

    if category_id:
        query = query.filter(Product.category_id == category_id)

    if search:

        recursive_query = text("""
        WITH RECURSIVE category_tree AS (
            SELECT id, parent_id
            FROM categories
            WHERE name ILIKE :search

            UNION ALL

            SELECT c.id, c.parent_id
            FROM categories c
            JOIN category_tree ct
            ON c.parent_id = ct.id
        )
        SELECT id FROM category_tree
    """)

        result = db.execute(
            recursive_query,
            {"search": f"%{search}%"}
        ).fetchall()

        category_ids = [row[0] for row in result]

        similarity_score = func.similarity(
            Product.name,
            search
        )

        query = query.add_columns(
            similarity_score.label("score")
        ).filter(
            or_(
                Product.name.ilike(f"%{search}%"),
                Product.category_id.in_(category_ids),
                similarity_score > 0.3   
            )
        ).order_by(desc("score"))
    if sort == "price_asc":
        query = query.order_by(asc(Product.price))

    elif sort == "price_desc":
        query = query.order_by(desc(Product.price))

    elif sort == "newest":
        query = query.order_by(desc(Product.created_at))

    else:
        query = query.order_by(desc(Product.created_at))

    total_products = query.count()

    results = (
        query
        .offset(offset)
        .limit(limit)
        .all()
    )

    products = []

    for r in results:
        sellable_stock = (
            r.quantity_available - r.reserved_quantity
        )

        products.append({
            "id": r.id,
            "name": r.name,
            "description": r.description,
            "category_id": r.category_id,
            "category": r.category,
            "price": float(r.price),
            "stock": sellable_stock,
            "image_url": r.image_url
        })

    return {
        "page": page,
        "limit": limit,
        "total": total_products,
        "data": products
    }
    
#get specific product details
def get_product_details(db: Session, product_id):

    product_data = (
        db.query(
            Product.id,
            Product.name,
            Product.description,
            Product.price,
            Product.is_active,
            Category.name.label("category"),
            Inventory.quantity_available,
            Inventory.reserved_quantity
        )
        .join(Category, Product.category_id == Category.id)
        .join(Inventory, Inventory.product_id == Product.id)
        .filter(Product.id == product_id)
        .first()
    )

    if not product_data:
        raise HTTPException(404, "Product not found")

    sellable_stock = (
        product_data.quantity_available -
        product_data.reserved_quantity
    )

    if not product_data.is_active or sellable_stock <= 0:
        raise HTTPException(404, "Product not available")

    # fetch images separately
    images = (
        db.query(ProductImage.image_url)
        .filter(ProductImage.product_id == product_id)
        .all()
    )

    image_list = [img.image_url for img in images]

    return {
        "id": product_data.id,
        "name": product_data.name,
        "description": product_data.description,
        "category": product_data.category,
        "price": float(product_data.price),
        "stock": sellable_stock,
        "images": image_list
    }