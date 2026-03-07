from sqlalchemy.orm import Session
from app.models.users import User


def get_user_by_email(db: Session, email: str):

    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user_data):

    user = User(name=user_data["name"],email=user_data["email"],password_hash=user_data["password_hash"],phone=user_data["phone"],is_active=True)

    db.add(user)

    db.commit()

    db.refresh(user)

    return user