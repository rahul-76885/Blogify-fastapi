from typing import Annotated

from blog.template_env import templates
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from blog import models
from blog.database import get_db

from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

router = APIRouter()


@router.get("/", include_in_schema=False, name="home")
@router.get("/posts", include_in_schema=False, name="posts")
async def home(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(models.Post).options(
            selectinload(models.Post.author)
        )
    )

    posts = result.scalars().all()

    return templates.TemplateResponse(
        request,
        "home.html",
        {
            "posts": posts,
            "title": "Home",
        },
    )


@router.get(
    "/posts/{post_id}",
    include_in_schema=False,
    name="post_page",
)
async def post_page(
    request: Request,
    post_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author))
        .where(models.Post.id == post_id)
    )

    post = result.scalars().first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    return templates.TemplateResponse(
        request,
        "post.html",
        {
            "post": post,
            "title": post.title[:50],
        },
    )


@router.get(
    "/users/{user_id}/posts",
    include_in_schema=False,
    name="user_posts",
)
async def user_posts_page(
    request: Request,
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(models.User).where(
            models.User.id == user_id
        )
    )

    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    result = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author))
        .where(models.Post.user_id == user_id)
    )

    posts = result.scalars().all()

    return templates.TemplateResponse(
        request,
        "user_posts.html",
        {
            "posts": posts,
            "user": user,
            "title": f"{user.username}'s Posts",
        },
    )


async def general_http_exception_handler(
    request: Request,
    exception: StarletteHTTPException,
):
    if request.url.path.startswith("/api"):
        return await http_exception_handler(request, exception)

    message = (
        exception.detail
        if exception.detail
        else "An error occurred. Please check your request and try again."
    )

    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": exception.status_code,
            "title": exception.status_code,
            "message": message,
        },
        status_code=exception.status_code,
    )


async def validation_exception_handler(
    request: Request,
    exception: RequestValidationError,
):
    if request.url.path.startswith("/api"):
        return await request_validation_exception_handler(
            request,
            exception,
        )

    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "title": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "message": "Invalid request. Please check your input and try again.",
        },
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        StarletteHTTPException,
        general_http_exception_handler,
    )

    app.add_exception_handler(
        RequestValidationError,
        validation_exception_handler,
    )