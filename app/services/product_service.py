
import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException,UploadFile
from uuid import UUID   
from app.models.product import Product
from app.models.category import Category
from app.models.inventory import Inventory
from app.models.product_images import ProductImage
from app.schemas.product import ProductCreate
from app.schemas.product import BulkProductUpdate
import pandas as pd

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


def bulk_update_products(db: Session, data: BulkProductUpdate):

    try:

        updated_products = []

        for item in data.products:

            product = db.query(Product).filter(
                Product.sku == item.sku
            ).first()

            if not product:
                raise HTTPException(
                    status_code=404,
                    detail=f"Product with SKU {item.sku} not found"
                )

            if item.name is not None:
                product.name = item.name

            if item.description is not None:
                product.description = item.description

            if item.price is not None:
                product.price = item.price

            if item.is_active is not None:
                product.is_active = item.is_active

            if item.category_id is not None:

                category = db.query(Category).filter(
                    Category.id == item.category_id
                ).first()

                if not category:
                    raise HTTPException(
                        status_code=404,
                        detail="Category not found"
                    )

                product.category_id = item.category_id

            if item.quantity_available is not None:

                inventory = db.query(Inventory).filter(
                    Inventory.product_id == product.id
                ).first()

                if not inventory:
                    raise HTTPException(
                        status_code=404,
                        detail="Inventory not found"
                    )

                inventory.quantity_available = item.quantity_available

            if item.images is not None:

                db.query(ProductImage).filter(
                    ProductImage.product_id == product.id
                ).delete()

                first = True

                for img in item.images:

                    new_img = ProductImage(
                        id=uuid.uuid4(),
                        product_id=product.id,
                        image_url=img,
                        is_primary=first
                    )

                    db.add(new_img)

                    first = False

            updated_products.append(product.sku)

        db.commit()

        return {
            "message": "Products updated successfully",
            "updated_skus": updated_products
        }

    except Exception as e:
        db.rollback()
        raise e
def delete_product(db: Session, product_id: UUID):
    product=db.query(Product).filter(Product.id==product_id).first()
    if not product:
        raise HTTPException(404, "Product not found")
    db.query(Inventory).filter(
        Inventory.product_id == product_id
    ).delete()

    # delete images
    db.query(ProductImage).filter(
        ProductImage.product_id == product_id
    ).delete()

    # delete product
    db.delete(product)

    db.commit()

    return {"message": "Product deleted successfully"}
#adding multiple products through csv
def upload_products_service(file: UploadFile, db: Session):

    try:
        df = pd.read_csv(file.file)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid CSV file")

    inserted_products = 0
    errors = []

    for index, row in df.iterrows():

        try:

            category = db.query(Category).filter(
                Category.id == row["category_id"]
            ).first()

            if not category:
                errors.append(f"Row {index+1}: Category not found")
                continue

            product = Product(
                name=row["name"],
                description=row["description"],
                category_id=row["category_id"],
                price=row["price"],
                sku=row["sku"],
                is_active=True
            )

            db.add(product)
            db.flush()

            # inventory
            inventory = Inventory(
                product_id=product.id,
                quantity_available=row["quantity"],
                reserved_quantity=0
            )

            db.add(inventory)

            # images
            images = str(row["images"]).split("|")

            for i, img in enumerate(images):

                image = ProductImage(
                    product_id=product.id,
                    image_url=img,
                    is_primary=(i == 0)
                )

                db.add(image)

            inserted_products += 1

        except Exception as e:
            errors.append(f"Row {index+1}: {str(e)}")

    db.commit()

    return {
        "inserted": inserted_products,
        "failed_rows": errors
    }