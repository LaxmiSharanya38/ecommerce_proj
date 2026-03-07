from sqlalchemy.orm import Session
from app.models.address import Address


from app.models.address import Address

def create_address(db, user_id, address_data):

    # Check if user already has addresses
    existing_address = (
        db.query(Address)
        .filter(Address.user_id == user_id)
        .first()
    )

    if existing_address:
        # Change previous default address to False
        db.query(Address).filter(
            Address.user_id == user_id,
            Address.is_default == True
        ).update({"is_default": False})

    # New address will always be default
    address_data["is_default"] = True

    new_address = Address(
        user_id=user_id,
        **address_data
    )

    db.add(new_address)
    db.commit()
    db.refresh(new_address)

    return new_address

#to get all user addresses
def get_user_addresses(db: Session, user_id):

    return db.query(Address).filter(
        Address.user_id == user_id
    ).all()
#delete address except default address
def delete_address(db: Session, address_id, user_id):

    address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == user_id
    ).first()

    if not address:
        return None

    if address.is_default:
        raise Exception("Cannot delete default address")

    db.delete(address)
    db.commit()

    return address
#to set previous address as default address

def set_default_address(db: Session, user_id, address_id):

    # check if address belongs to the user
    address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == user_id
    ).first()

    if not address:
        return None

    # find current default address
    current_default = db.query(Address).filter(
        Address.user_id == user_id,
        Address.is_default == True
    ).first()

    # make current default false
    if current_default:
        current_default.is_default = False

    # set new default
    address.is_default = True

    db.commit()
    db.refresh(address)

    return address

#to update any user address
def update_user_address(db: Session, user_id, address_id, address_data):

    # find the address belonging to the user
    address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == user_id
    ).first()

    if not address:
        return None

    update_data = address_data.dict(exclude_unset=True)

    # update only provided fields
    for key, value in update_data.items():
        setattr(address, key, value)

    db.commit()
    db.refresh(address)

    return address
