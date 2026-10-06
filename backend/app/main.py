from fastapi import FastAPI

from backend.app.api.routes.documents import router as documents_router
from backend.app.api.routes.health import router as health_router
from backend.app.api.routes.users import router as users_router
from backend.app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)

app.include_router(health_router)
app.include_router(users_router)
app.include_router(documents_router)
