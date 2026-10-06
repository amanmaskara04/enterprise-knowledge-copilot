from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.models.user import User
from backend.app.schemas.user import UserCreate


def create_user(db: Session, data: UserCreate) -> User:
    user = User(
        email=str(data.email).lower(),
        full_name=data.full_name,
        role=data.role,
    )
    db.add(user)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise

    db.refresh(user)
    return user


def get_user_by_id(db: Session, user_id):
    return db.scalar(select(User).where(User.id == user_id))


def get_user_by_email(db: Session, email: str):
    return db.scalar(select(User).where(User.email == email.lower()))
