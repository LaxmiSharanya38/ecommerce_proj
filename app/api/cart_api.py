from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.product import Product
from app.models.inventory import Inventory
from app.schemas.cart import AddMultipleToCartRequest,UpdateCartItemRequest
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.post("/add-items")
def add_multiple_items_to_cart(
    data: AddMultipleToCartRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.add(cart)
        db.flush()

    validated_items = []

    for item in data.items:

        product = db.query(Product).filter(Product.id == item.product_id,Product.is_active == True).first()

        if not product:
            raise HTTPException(status_code=404,detail=f"Product {item.product_id} not available")

        inventory = db.query(Inventory).filter(Inventory.product_id == product.id).first()

        if not inventory:
            raise HTTPException(status_code=400,detail=f"Inventory missing for product {product.id}")

        sellable_stock = (inventory.quantity_available -inventory.reserved_quantity)

        if sellable_stock < item.quantity:
            raise HTTPException(status_code=400,detail=f"Insufficient stock for {product.name}")

        validated_items.append((item, product, inventory))

    for item, product, inventory in validated_items:

        cart_item = db.query(CartItem).filter(CartItem.cart_id == cart.id,CartItem.product_id == product.id).first()

        if cart_item:
            cart_item.quantity += item.quantity
        else:
            cart_item = CartItem(cart_id=cart.id,product_id=product.id,quantity=item.quantity,price_at_time=product.price)
            db.add(cart_item)

        inventory.reserved_quantity += item.quantity

        remaining_stock = (inventory.quantity_available -inventory.reserved_quantity)

        if remaining_stock <= 0:
            product.is_active = False

    db.commit()

    return {
        "message": "Items added to cart successfully"
    }


@router.post("/update-quantity")
def update_cart_item_quantity(
    data: UpdateCartItemRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()

    if not cart:
        raise HTTPException(404, "Cart not found")

    product = db.query(Product).filter(Product.id == data.product_id).first()

    if not product:
        raise HTTPException(404, "Product not found")

    cart_item = db.query(CartItem).filter(CartItem.cart_id == cart.id,CartItem.product_id == product.id).first()

    if not cart_item:
        raise HTTPException(404, "Item not present in cart")

    inventory = db.query(Inventory).filter(Inventory.product_id == product.id).first()

    if not inventory:
        raise HTTPException(400, "Inventory missing")

    old_quantity = cart_item.quantity
    new_quantity = data.quantity
    quantity_difference = new_quantity - old_quantity

    if quantity_difference > 0:
        sellable_stock = (inventory.quantity_available -inventory.reserved_quantity)

        if sellable_stock < quantity_difference:
            raise HTTPException(400, "Insufficient stock")

        inventory.reserved_quantity += quantity_difference

    elif quantity_difference < 0:
        inventory.reserved_quantity += quantity_difference  

    cart_item.quantity = new_quantity

    remaining_stock = (inventory.quantity_available -inventory.reserved_quantity)

    product.is_active = remaining_stock > 0

    db.commit()
    db.refresh(cart_item)

    return {
        "message": "Cart item quantity updated successfully",
        "product_id": str(product.id),
        "new_quantity": cart_item.quantity
    }
@router.delete("/delete-item/{product_id}")
def delete_cart_item(
    product_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()

    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    cart_item = db.query(CartItem).filter(CartItem.cart_id == cart.id,CartItem.product_id == product.id).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not found in cart")

    inventory = db.query(Inventory).filter(
        Inventory.product_id == product.id
    ).first()

    if not inventory:
        raise HTTPException(status_code=400, detail="Inventory missing")

    inventory.reserved_quantity -= cart_item.quantity

    if inventory.reserved_quantity < 0:
        inventory.reserved_quantity = 0

    db.delete(cart_item)

    remaining_stock = (inventory.quantity_available -inventory.reserved_quantity)

    product.is_active = remaining_stock > 0

    db.commit()

    return {
        "message": "Item removed from cart successfully",
        "product_id": str(product.id)
    }

@router.get("/my-cart")
def get_cart_items(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    cart = db.query(Cart).filter(
        Cart.user_id == current_user.id
    ).first()

    if not cart:
        return {
            "cart_items": [],
            "total_amount": 0
        }

    cart_items = db.query(CartItem).filter(CartItem.cart_id == cart.id).all()

    response_items = []
    total_amount = 0

    for item in cart_items:

        product = db.query(Product).filter(
            Product.id == item.product_id
        ).first()

        item_total = item.quantity * item.price_at_time
        total_amount += item_total

        response_items.append({
            "product_id": str(product.id),
            "product_name": product.name,
            "quantity": item.quantity,
            "price_at_time": float(item.price_at_time),
            "item_total": float(item_total)
        })

    return {
        "cart_id": str(cart.id),
        "cart_items": response_items,
        "total_amount": float(total_amount)
    }