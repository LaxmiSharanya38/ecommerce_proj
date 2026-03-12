
import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException
from uuid import UUID   
from app.models.product import Product
from app.models.category import Category
from app.models.inventory import Inventory
from app.models.product_images import ProductImage
from app.schemas.product import ProductCreate
from app.schemas.product import ProductUpdate


def create_product(db: Session, data: ProductCreate):

    try:
        category = db.query(Category).filter(
            Category.id == data.category_id
        ).first()

        if not category:
            raise HTTPException(404, "Category not found")

        product = Product(
            id=uuid.uuid4(),
            name=data.name,
            description=data.description,
            category_id=data.category_id,
            price=data.price,
            sku=data.sku,
            is_active=True
        )

        db.add(product)
        db.flush() 

        inventory = Inventory(
            id=uuid.uuid4(),
            product_id=product.id,
            quantity_available=data.quantity_available,
            reserved_quantity=0
        )

        db.add(inventory)

        first_image = True
        for img in data.images:
            image = ProductImage(
                id=uuid.uuid4(),
                product_id=product.id,
                image_url=img,
                is_primary=first_image
            )
            db.add(image)
            first_image = False

        db.commit()
        db.refresh(product)

        return product

    except Exception as e:
        db.rollback()
        raise e


def update_product(db: Session, product_id: UUID, data: ProductUpdate):

    try:
        product = db.query(Product).filter(
            Product.id == product_id
        ).first()

        if not product:
            raise HTTPException(404, "Product not found")

        if data.name is not None:
            product.name = data.name

        if data.description is not None:
            product.description = data.description

        if data.price is not None:
            product.price = data.price

        if data.sku is not None:
            product.sku = data.sku

        if data.is_active is not None:
            product.is_active = data.is_active

        if data.category_id is not None:
            category = db.query(Category).filter(
                Category.id == data.category_id
            ).first()

            if not category:
                raise HTTPException(404, "Category not found")

            product.category_id = data.category_id

        if data.quantity_available is not None:
            inventory = db.query(Inventory).filter(
                Inventory.product_id == product.id
            ).first()

            if not inventory:
                raise HTTPException(404, "Inventory not found")

            inventory.quantity_available = data.quantity_available

        if data.images is not None:

            db.query(ProductImage).filter(
                ProductImage.product_id == product.id
            ).delete()

            first = True
            for img in data.images:
                new_img = ProductImage(
                    id=uuid.uuid4(),
                    product_id=product.id,
                    image_url=img,
                    is_primary=first
                )
                db.add(new_img)
                first = False

        db.commit()
        db.refresh(product)

        return product

    except Exception as e:
        db.rollback()
        raise e
