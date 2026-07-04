from typing import Annotated

from fastapi import Depends,HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from blog import app,templates

from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException as StarletteHTTPException
# NOTE: it's `starlette.exceptions` (plural). `starlette.exception` (singular)
# does not exist and will crash the app on import.

import blog.models as models
from blog.database import Base, engine, get_db
from blog.schemas import PostCreate, PostResponse, UserCreate, UserResponse,PostUpdate,UserUpdate

# Base.metadata.create_all(bind=engine)
# -> Creates all tables defined in models.py if they don't already exist.
# -> Safe to call every startup; does nothing if tables already exist.
Base.metadata.create_all(bind=engine)

# ---------------------------------------------------------------------------
# HTML routes
# ---------------------------------------------------------------------------
#
# include_in_schema=False
#   FastAPI auto-documents every route in /docs and /redoc by default.
#   HTML pages don't belong in API docs — this hides them.
#   Flask has no equivalent because it has no built-in API docs.
#
# name="home"
#   Gives the route a stable identifier, independent of the function name.
#   You can rename the function freely without breaking anything.
#   Used in templates as: {{ request.url_for('home') }} → "/"
#   Also prevents name collisions when using APIRouter across multiple files.
#
# request: Request  (dependency injection)
#   FastAPI explicitly injects the HTTP request object into the function.
#   Gives access to: request.headers, request.cookies,
#                    request.query_params, request.url, request.url.path
#   Flask uses a global proxy (from flask import request) — invisible, magical.
#   FastAPI makes it explicit — visible, testable, and mockable.
#
# templates.TemplateResponse()
#   FastAPI's equivalent of Flask's render_template().
#   Flask:   return render_template("home.html", posts=posts)  ← no request needed
#   FastAPI: must pass "request" explicitly — no global app context like Flask.
#
# "request": request  (required in every TemplateResponse)
#   Jinja2 needs it to run url_for() inside templates.
#   Used in HTML as:
#     {{ request.url_for('static', path='style.css') }} → /static/style.css
#     {{ request.url_for('home') }}                     → /
#   Forgetting this raises an error immediately (better than silent failure).

@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
def home(request: Request, db: Annotated[Session, Depends(get_db)]):
    # db: Annotated[Session, Depends(get_db)]
    #   Session         -> type hint only, tells Python db will be a SQLAlchemy Session
    #   Depends(get_db) -> FastAPI dependency injection; calls get_db(), injects
    #                      the yielded session into `db`, closes it after the request.
    #   IMPORTANT: it's Depends(get_db) with parentheses (calling it),
    #   NOT Depends[get_db] with brackets - that raises a TypeError.

    # select(models.Post)  -> builds SQL: SELECT * FROM posts;  (not executed yet)
    # db.execute(...)      -> actually sends the query to the database
    # result               -> a SQLAlchemy Result object, NOT a list of Post objects
    result = db.execute(select(models.Post))

    # .scalars()  -> extracts ORM Post objects out of each result row
    # .all()      -> returns every matching row as a Python list
    posts = result.scalars().all()

    # request: Request must be passed into TemplateResponse - Jinja2 needs it
    # to support url_for() inside templates. FastAPI has no global request
    # context like Flask does, so it's always explicit here.
    return templates.TemplateResponse(
        request,
        "home.html",
        # NOTE: this must be the variable `posts`, not the string "posts" -
        # using "posts" (quoted) sends literal text to the template instead
        # of the actual list of Post objects.
        {"posts": posts, "title": "Home"},
    )


@app.get("/posts/{post_id}", include_in_schema=False, name="post_page")
def post_page(request: Request, post_id: int, db: Annotated[Session, Depends(get_db)]):
    # select(...).where(...) adds a SQL condition:
    #   SELECT * FROM posts WHERE id = <post_id>;
    result = db.execute(select(models.Post).where(models.Post.id == post_id))

    # .first() -> returns the single matching object, or None if no match.
    # Use .first() (not .all()) when you only expect/need one row.
    post = result.scalars().first()
    if post:
        title = post.title[:50]
        return templates.TemplateResponse(
            request,
            "post.html",
            {"post": post, "title": title},
        )
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


@app.get("/users/{user_id}/posts", include_in_schema=False, name="user_posts")
def user_posts_page(
    request: Request,
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    # Check the USER exists first - this is a 404 about the user, not the posts.
    # (Bug to avoid: don't check `if posts:` and say "User not found" when it's
    # really just an empty post list for a valid user - those are different things.)
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Separate query for this user's posts. Empty list here is fine -
    # a user with zero posts is not an error.
    result = db.execute(select(models.Post).where(models.Post.user_id == user_id))
    posts = result.scalars().all()
    return templates.TemplateResponse(
        request,
        "user_posts.html",
        {"posts": posts, "user": user, "title": f"{user.username}'s Posts"},
    )


# =============================================================================
# API ROUTES
# -----------------------------------------------------------------------------
# Purpose: provide JSON data for clients (browser JS, mobile apps, Postman, etc).
# Returns: JSON, validated/shaped by response_model schemas.
#
# response_model=UserResponse / PostResponse
#   FastAPI filters and validates the returned object against this schema
#   before sending it out. Hides any fields not declared in the schema,
#   auto-documents the response shape in /docs.
#
# status_code=status.HTTP_201_CREATED
#   200 = generic success. 201 = a new resource was created.
#   Since these POST routes create a new User/Post row, 201 is correct here.
# =============================================================================

@app.post(
    "/api/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
    # user: UserCreate -> request body schema, validates incoming JSON
    # (e.g. {"username": "rahul", "email": "rahul@gmail.com"})

    # Check username uniqueness:
    # SELECT * FROM users WHERE username = '<user.username>';
    result = db.execute(
        select(models.User).where(models.User.username == user.username),
    )
    # NOTE: must be result.scalars().first() - both parens required.
    # result.scalars.first() (missing parens on scalars) calls .first() on
    # the method object itself, not on its result - this is a bug to avoid.
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    # Check email uniqueness the same way.
    result = db.execute(
        select(models.User).where(models.User.email == user.email),
    )
    existing_email = result.scalars().first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Build the ORM object - not saved to the DB yet.
    new_user = models.User(
        username=user.username,
        email=user.email,
    )
    db.add(new_user)      # marks it for insertion (still not saved)
    db.commit()            # actually runs INSERT INTO users ...
    db.refresh(new_user)   # reloads new_user from the DB so it picks up
                            # DB-generated values like the new `id`
    return new_user


@app.get("/api/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(models.User).where(models.User.id == user_id),
    )
    user = result.scalars().first()
    if user:
        return user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


@app.get("/api/users/{user_id}/posts", response_model=list[PostResponse])
def get_user_posts(user_id: int, db: Annotated[Session, Depends(get_db)]):
    # Same pattern as user_posts_page above: validate the user exists first,
    # THEN fetch their posts (which may legitimately be an empty list).
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    result = db.execute(select(models.Post).where(models.Post.user_id == user_id))
    posts = result.scalars().all()
    return posts
@app.patch("/api/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Annotated[Session, Depends(get_db)],
):
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user_update.username is not None and user_update.username != user.username:
        result = db.execute(
            select(models.User).where(models.User.username == user_update.username),
        )
        existing_user = result.scalars().first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists",
            )

    if user_update.email is not None and user_update.email != user.email:
        result = db.execute(
            select(models.User).where(models.User.email == user_update.email),
        )
        existing_email = result.scalars().first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)


    db.commit()
    db.refresh(user)
    return user


@app.delete("/api/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    db.delete(user)
    db.commit()

@app.get("/api/posts", response_model=list[PostResponse])
def get_posts(db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Post))
    posts = result.scalars().all()
    return posts


@app.post(
    "/api/posts",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_post(post: PostCreate, db: Annotated[Session, Depends(get_db)]):
    # Validate the referenced user_id actually exists before creating
    # a post that points to it (foreign key sanity check at the app level).
    result = db.execute(select(models.User).where(models.User.id == post.user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    new_post = models.Post(
        title=post.title,
        content=post.content,
        user_id=post.user_id,
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@app.get("/api/posts/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if post:
        return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

@app.put("/api/posts/{post_id}",response_model=PostResponse)
def update_post_full(post_id:int,post_data:PostCreate,db:Annotated[Session,Depends(get_db)]):
    result=db.execute(select(models.Post).where(models.Post.id == post_id))
    post=result.scalars().first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    if post_data.user_id != post.user_id:
        result=db.execute(select(models.User).where(models.User.id == post_data.user_id))
        user=result.scalars().first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
    post.title=post_data.title
    post.content=post_data.content
    post.user_id=post_data.user_id

    db.commit()
    db.refresh(post)
    return post

@app.patch("/api/posts/{post_id}", response_model=PostResponse)
def update_post_partial(
    post_id: int,
    post_data: PostUpdate,
    db: Annotated[Session, Depends(get_db)]
):
    result = db.execute(
        select(models.Post).where(models.Post.id == post_id)
    )
    post = result.scalars().first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    # model_dump(exclude_unset=True) returns ONLY the fields that the client
    # actually sent in the request body.
    #
    # Example Request:
    # {
    #     "title": "New Title"
    # }
    #
    # update_data becomes:
    # {"title": "New Title"}
    #
    # "content" is NOT included because the client didn't send it.
    # This prevents existing database values from being overwritten with None.
    update_data = post_data.model_dump(exclude_unset=True)

    # Dynamically update only the provided fields.
    #
    # Example:
    # update_data = {
    #     "title": "New Title",
    #     "content": "Updated Content"
    # }
    #
    # Loop Iteration 1:
    # key = "title"
    # value = "New Title"
    # setattr(post, "title", "New Title")
    # -> Equivalent to:
    # post.title = "New Title"
    #
    # Loop Iteration 2:
    # key = "content"
    # value = "Updated Content"
    # setattr(post, "content", "Updated Content")
    # -> Equivalent to:
    # post.content = "Updated Content"
    #
    # setattr() is useful because we don't have to manually write:
    # if post_data.title is not None:
    #     post.title = post_data.title
    # if post_data.content is not None:
    #     post.content = post_data.content
    #
    # The same code works automatically for any number of fields.
    for key, value in update_data.items():
        setattr(post, key, value)

    # Save the modified object permanently to the database.
    db.commit()

    # Reload the object from the database.
    # This ensures the SQLAlchemy object contains the latest values stored
    # in the database, including any values automatically generated or
    # modified by the database (e.g., timestamps, defaults, triggers).
    db.refresh(post)

    # Return the updated SQLAlchemy model object.
    #
    # Although 'post' is NOT a JSON object (it's a SQLAlchemy model instance),
    # FastAPI sees response_model=PostResponse and automatically converts it.
    #
    # Because PostResponse has:
    # model_config = ConfigDict(from_attributes=True)
    #
    # Pydantic reads the object's attributes (post.id, post.title, post.content,
    # etc.), creates a PostResponse object, and FastAPI serializes that object
    # into JSON before sending the response to the client.
    #
    # Flow:
    # SQLAlchemy Model -> Pydantic(PostResponse) -> JSON Response
    return post

@app.delete("/api/posts/{post_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id:int,db:Annotated[Session,Depends(get_db)]):
    result=df.execute(select(models.Post).where(models.Post.id == post_id))
    post=result.scalars().First()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    db.delete(post)
    db.commit()
# =============================================================================
# EXCEPTION HANDLERS
# -----------------------------------------------------------------------------
# HTTPException        -> handles things you raise yourself (404, 400, etc.)
# RequestValidationError -> handles invalid request bodies (Pydantic validation)
#
# Both handlers branch on the URL path:
#   /api/*       -> return JSON (because API clients expect JSON)
#   everything else -> return error.html (because browsers expect a page)
# =============================================================================

@app.exception_handler(StarletteHTTPException)
def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
    message = (
        exception.detail
        if exception.detail
        else "An error occurred. Please check your request and try again."
    )
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exception.status_code,
            content={"detail": message},
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


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exception: RequestValidationError):
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": exception.errors()},
        )
    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Invalid request. Please check your input and try again.",
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )

# ---------------------------------------------------------------------------
# Full request lifecycle
# ---------------------------------------------------------------------------
#
#  Browser / API client
#       │
#       │  HTTP Request
#       ▼
#  ┌─────────────────────────────────────────────────────┐
#  │  FastAPI router                                     │
#  │  matches URL path + HTTP method to a route function │
#  └─────────────────────────────────────────────────────┘
#       │
#       ▼
#  ┌─────────────────────────────────────────────────────┐
#  │  Dependency injection  (automatic)                  │
#  │  request: Request — HTTP request object injected    │
#  │  post_id: int     — path param extracted + coerced  │
#  │  invalid type (e.g. "abc") → RequestValidationError │
#  └─────────────────────────────────────────────────────┘
#       │                              │
#       │ valid params                 │ invalid params
#       ▼                              ▼
#  Route function runs        validation_exception_handler
#       │                              │
#       │                           /api/* ?
#       │                          ┌────┴────┐
#       │                        JSON       HTML
#       │                     {"detail":…} error.html (422)
#       │
#       ├─ return dict / list
#       │    FastAPI serializes → JSON response automatically
#       │
#       ├─ return TemplateResponse
#       │    Jinja2 renders → HTML response sent to browser
#       │
#       └─ raise HTTPException(status_code=..., detail=...)
#                │
#                ▼
#         http_exception_handler
#         (StarletteHTTPException catches FastAPI's too)
#                │
#             /api/* ?
#            ┌────┴────┐
#          JSON       HTML
#       {"detail":…} error.html (status_code)
#
#
# ---------------------------------------------------------------------------
# Static file request lifecycle (separate flow — never hits route functions)
# ---------------------------------------------------------------------------
#
#  Browser requests /static/style.css
#       │
#       ▼
#  app.mount("/static", StaticFiles(directory="static"), name="static")
#       │
#       ▼
#  File read from disk and returned directly to browser
#  (no route function, no Jinja2, no exception handlers involved)
# why we use HttpException instead of returning a dict with status code and message?
# bc using hhtpexception give us more control over the response, and it allows us to raise
# an exception that can be caught by FastAPI's exception handlers. This way, we can customize the error response and ensure that it follows a consistent format across the application. Additionally, using HTTPException allows us to set specific status codes and messages, making it easier to handle errors in a standardized way.