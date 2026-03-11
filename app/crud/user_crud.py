from sqlalchemy.orm import Session
from app.models.users import User
from app.utils.security import verify_password, hash_password

def get_user_by_email(db: Session, email: str):

    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user_data):

    user = User(name=user_data["name"],email=user_data["email"],password_hash=user_data["password_hash"],phone=user_data["phone"],is_active=True)

    db.add(user)

    db.commit()

    db.refresh(user)

    return user

def change_user_password(
    db: Session,
    user_id,
    old_password,
    new_password
):

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise Exception("User not found")

    # verify old password
    if not verify_password(old_password, user.password_hash):
        raise Exception("Old password is incorrect")

    # optional safety check
    if verify_password(new_password, user.password_hash):
        raise Exception("New password cannot be same as old password")

    # update password (existing record)
    user.password_hash = hash_password(new_password)

    db.commit()
    db.refresh(user)

    return {"message": "Password changed successfully"}





def delete_user_account(db: Session, user_id, password: str):

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise Exception("User not found")

    # verify password 
    if not verify_password(password, user.password_hash):
        raise Exception("Incorrect password")

    db.delete(user)
    db.commit()

    return {"message": "User account deleted successfully"}




def delete_user_account(db: Session, user_id, password: str):

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise Exception("User not found")

    # ✅ verify password using password_hash column
    if not verify_password(password, user.password_hash):
        raise Exception("Incorrect password")

    db.delete(user)
    db.commit()

    return {"message": "User account deleted successfully"}