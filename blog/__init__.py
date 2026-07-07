from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from blog.database import Base, engine
from blog.routers import (
    register_exception_handlers,
    register_routers,
)

BASE_DIR = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(_app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()


app = FastAPI(
    title="FastAPI Blog",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
app.mount("/media", StaticFiles(directory=BASE_DIR / "media"), name="media")

register_routers(app)
register_exception_handlers(app)