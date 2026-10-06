from uuid import UUID

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.db.session import get_db
from backend.app.services.user import get_user_by_id


def get_current_user(
    x_dev_user_id: str | None = Header(default=None),
    db: Session = Depends(get_db),
):

    # TEMPORARY DEVELOPMENT-ONLY IDENTITY.
    # Replace this dependency with real authentication in Phase 7.
    # NEVER deploy this development identity mechanism.
    if settings.environment != "development":
        raise HTTPException(status_code=500, detail="Development identity is disabled")

    if not x_dev_user_id:
        raise HTTPException(status_code=401, detail="Missing X-Dev-User-Id header")

    try:
        user_id = UUID(x_dev_user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid X-Dev-User-Id header")

    user = get_user_by_id(db, user_id)

    if user is None:
        raise HTTPException(status_code=401, detail="Invalid X-Dev-User-Id header")

    return user
