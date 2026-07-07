from fastapi import FastAPI

from .frontend import (
    register_exception_handlers as register_frontend_exception_handlers,
    router as frontend_router,
)
from .posts import router as posts_router
from .users import router as users_router


def register_routers(app: FastAPI) -> None:
    app.include_router(frontend_router)
    app.include_router(users_router, prefix="/api/users", tags=["Users"])
    app.include_router(posts_router, prefix="/api/posts", tags=["Posts"])


def register_exception_handlers(app: FastAPI) -> None:
    register_frontend_exception_handlers(app)