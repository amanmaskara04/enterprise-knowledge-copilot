from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user
from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.schemas.user import UserCreate, UserRead
from backend.app.services.user import create_user

router = APIRouter()


@router.post(
    "/users",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
def create_user_endpoint(
    data: UserCreate,
    db: Session = Depends(get_db),
) -> User:
    try:
        return create_user(db, data)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists",
        )


@router.get("/users/me", response_model=UserRead)
def get_current_user_endpoint(
    current_user: User = Depends(get_current_user),
) -> User:
    return current_user
