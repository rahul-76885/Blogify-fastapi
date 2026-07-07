# Chapter 05 -- Routes (`routes.py`)

**Source File:** `blog/routes.py`

------------------------------------------------------------------------

# Purpose

The `routes.py` file is the bridge between the outside world and your
application.

It is responsible for:

-   Receiving HTTP requests
-   Matching the correct URL
-   Executing application logic
-   Returning HTML or JSON responses

Think of routes as the **entry points** of your application.

------------------------------------------------------------------------

# Learning Objectives

After reading this chapter you should understand:

-   What routes are
-   Why routing exists
-   How FastAPI matches routes
-   HTML routes vs API routes
-   Dependency Injection
-   CRUD operations
-   SQLAlchemy inside routes
-   Response models
-   Exception handling
-   Best practices

------------------------------------------------------------------------

# File Overview

``` text
routes.py
│
├── HTML Routes
│   ├── Home
│   ├── Post Page
│   └── User Posts
│
├── User API
│
├── Post API
│
└── Exception Handlers
```

------------------------------------------------------------------------

# What is a Route?

A route is a Python function executed when a matching URL and HTTP
method are requested.

Example:

``` python
@app.get("/")
```

means:

    GET /

    ↓

    home()

------------------------------------------------------------------------

# Why do Routes exist?

Routes map URLs to functions.

``` text
URL

↓

Python Function
```

Example:

    /

    ↓

    home()

    ----------------

    /posts

    ↓

    posts()

    ----------------

    /api/users

    ↓

    create_user()

Without routing, FastAPI would not know which code to execute.

------------------------------------------------------------------------

# Request Lifecycle

``` text
Client

↓

HTTP Request

↓

FastAPI

↓

Route Matching

↓

Dependency Injection

↓

Validation

↓

Route Function

↓

SQLAlchemy

↓

Database

↓

Response Model

↓

JSON / HTML

↓

Client
```

------------------------------------------------------------------------

# Route Matching

Example:

``` python
@app.get("/posts/{post_id}")
```

Request:

    /posts/10

FastAPI extracts:

``` python
post_id = 10
```

If conversion fails:

    /posts/abc

FastAPI automatically returns **422 Validation Error**.

------------------------------------------------------------------------

# HTML Routes vs API Routes

## HTML Routes

Return HTML using:

``` python
TemplateResponse(...)
```

Used by browsers.

## API Routes

Return JSON.

Used by:

-   React
-   Vue
-   Mobile Apps
-   Postman
-   Other APIs

------------------------------------------------------------------------

# Why Separate Them?

HTML pages should not appear in Swagger.

Use:

``` python
include_in_schema=False
```

for browser-only routes.

------------------------------------------------------------------------

# APIRouter

As projects grow, one large `routes.py` becomes difficult to maintain.

Instead split routes into:

``` text
routers/

frontend.py

users.py

posts.py
```

Benefits:

-   Better organization
-   Easier testing
-   Cleaner architecture
-   Modular development

------------------------------------------------------------------------

# Dependency Injection

Example:

``` python
db: Annotated[AsyncSession, Depends(get_db)]
```

FastAPI automatically creates and injects the database session.

Flow:

``` text
Request

↓

Depends(get_db)

↓

AsyncSession

↓

Route

↓

Session Closed
```

------------------------------------------------------------------------

# Request Object

``` python
request: Request
```

Provides:

-   URL
-   Headers
-   Cookies
-   Client Information

Required by Jinja templates.

------------------------------------------------------------------------

# TemplateResponse

HTML routes return:

``` python
templates.TemplateResponse(...)
```

Flow:

``` text
Browser

↓

GET /

↓

Template

↓

HTML

↓

Browser
```

------------------------------------------------------------------------

# SQLAlchemy Inside Routes

Typical pattern:

``` python
result = await db.execute(...)
```

↓

``` python
result.scalars()
```

↓

``` python
.all()

or

.first()
```

------------------------------------------------------------------------

# select()

Creates a SQL query.

``` python
select(models.Post)
```

Equivalent to:

``` sql
SELECT * FROM posts;
```

------------------------------------------------------------------------

# execute()

Executes the SQL query.

``` python
await db.execute(query)
```

------------------------------------------------------------------------

# scalars()

Extracts ORM objects from the result.

Instead of rows:

    Row
    Row

You get:

    Post(...)
    Post(...)

------------------------------------------------------------------------

# all()

Returns every matching object.

``` python
posts = result.scalars().all()
```

------------------------------------------------------------------------

# first()

Returns the first object or `None`.

``` python
post = result.scalars().first()
```

------------------------------------------------------------------------

# selectinload()

Loads related objects efficiently.

Without it:

    Posts

    ↓

    One query per author

    ↓

    N+1 Problem

With it:

    Posts

    ↓

    One optimized query

    ↓

    Authors

------------------------------------------------------------------------

# CRUD Operations

  Operation   HTTP        SQL
  ----------- ----------- --------
  Create      POST        INSERT
  Read        GET         SELECT
  Update      PUT/PATCH   UPDATE
  Delete      DELETE      DELETE

------------------------------------------------------------------------

# POST

Flow:

``` text
Client

↓

JSON

↓

Schema

↓

Validation

↓

Database

↓

Response
```

Always validate data before inserting.

------------------------------------------------------------------------

# GET

Reads data without modifying the database.

------------------------------------------------------------------------

# PUT vs PATCH

PUT replaces an entire resource.

PATCH updates only supplied fields.

------------------------------------------------------------------------

# model_dump(exclude_unset=True)

Used for PATCH requests.

Without it:

Missing fields become `None`.

With it:

Only supplied fields are updated.

------------------------------------------------------------------------

# setattr()

Dynamic updates.

``` python
setattr(post, key, value)
```

Equivalent to:

``` python
post.title = value
```

Useful for partial updates.

------------------------------------------------------------------------

# DELETE

Typical flow:

``` text
Find Object

↓

Delete

↓

Commit

↓

204 No Content
```

------------------------------------------------------------------------

# Response Models

Example:

``` python
response_model=UserResponse
```

Purpose:

-   Filters output
-   Hides sensitive fields
-   Converts ORM objects into JSON

Flow:

``` text
ORM Object

↓

Pydantic

↓

JSON
```

------------------------------------------------------------------------

# Exception Handling

Raise:

``` python
HTTPException(...)
```

Flow:

``` text
Route

↓

Raise Exception

↓

Handler

↓

JSON or HTML
```

------------------------------------------------------------------------

# Common Mistakes

-   Forgetting `commit()`
-   Forgetting `refresh()`
-   Returning ORM models without response schemas
-   Using PUT instead of PATCH
-   Forgetting `exclude_unset=True`
-   Forgetting existence checks
-   Creating N+1 queries

------------------------------------------------------------------------

# Best Practices

-   Keep routes thin.
-   Put business logic elsewhere.
-   Use response models.
-   Raise `HTTPException`.
-   Validate related resources.
-   Prefer PATCH for partial updates.

------------------------------------------------------------------------

# Quick Revision

-   Routes receive requests.
-   APIRouter organizes endpoints.
-   Depends() injects dependencies.
-   HTML routes return templates.
-   API routes return JSON.
-   CRUD = Create, Read, Update, Delete.
-   select() builds queries.
-   execute() runs queries.
-   scalars() returns ORM objects.
-   response_model controls output.
-   selectinload() prevents N+1 queries.
-   model_dump(exclude_unset=True) enables PATCH.
-   setattr() updates fields dynamically.
-   HTTPException handles errors cleanly.
