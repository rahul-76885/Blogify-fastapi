# Database Layer

**Source:** `blog/database.py`

------------------------------------------------------------------------

# Purpose

This file centralizes everything related to database configuration.
Instead of creating database connections inside every route, the
application creates the shared configuration once and reuses it
throughout the project.

Responsibilities:

-   Configure the database engine.
-   Create database sessions.
-   Define the base class for ORM models.
-   Provide database sessions to FastAPI routes.

------------------------------------------------------------------------

# File Overview

``` text
database.py
│
├── Database URL
├── Engine
├── Session Factory
├── Base Class
└── get_db()
```

------------------------------------------------------------------------

# 1. Database URL

``` python
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./blog.db"
```

## What is it?

It tells SQLAlchemy **which database** to connect to.

## Why do we need it?

Without a database URL, SQLAlchemy has no idea where your data is
stored.

## In this project

-   `sqlite` → SQLite database
-   `aiosqlite` → asynchronous SQLite driver
-   `./blog.db` → database file stored in the project root

------------------------------------------------------------------------

# 2. Engine

``` python
engine = create_async_engine(...)
```

## What is it?

The Engine is SQLAlchemy's connection manager.

## Why do we need an Engine?

Imagine opening a brand-new database connection every time you execute a
query.

``` text
Route
 │
 ▼
Open Connection
 │
 ▼
Run Query
 │
 ▼
Close Connection
```

Doing this repeatedly is inefficient.

The Engine manages communication with the database so the rest of the
application doesn't need to worry about connection details.

## How it is used here

Every AsyncSession created later communicates with the database through
this Engine.

------------------------------------------------------------------------

# 3. Why Async Engine?

Your project uses:

``` python
create_async_engine(...)
```

instead of:

``` python
create_engine(...)
```

## Why?

FastAPI is designed around AsyncIO.

When the application waits for a database query to finish, it can
process other requests instead of blocking the current worker.

This improves scalability for I/O-bound applications.

------------------------------------------------------------------------

# AsyncIO Basics

## Synchronous

``` text
Request A
 │
Wait for DB
 │
Response

Request B waits...
```

## Asynchronous

``` text
Request A
 │
await database
 │
 ▼
Event Loop

Runs Request B

Runs Request C

Database finishes

Resume Request A
```

### Important

Async does **not** make the database faster.

It reduces idle waiting while the database is working.

------------------------------------------------------------------------

# 4. Session Factory

``` python
AsyncSessionLocal = async_sessionmaker(...)
```

## What is it?

A factory that creates new AsyncSession objects.

## Why do we need it?

Sharing one session between all requests is unsafe.

Instead, each request receives its own session.

``` text
Request 1 ──► Session A

Request 2 ──► Session B

Request 3 ──► Session C
```

This avoids shared state and transaction conflicts.

------------------------------------------------------------------------

# 5. Base

``` python
class Base(DeclarativeBase):
    pass
```

## Why do we create Base?

Instead of every model inheriting directly from `DeclarativeBase`, all
models inherit from one shared `Base`.

``` text
Base
├── User
├── Post
└── Comment
```

This allows SQLAlchemy to collect metadata for all models in one place.

Later, operations such as table creation can work with every registered
model.

------------------------------------------------------------------------

# 6. get_db()

``` python
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

## What is it?

A FastAPI dependency that creates a database session for one request.

## Why use `yield` instead of `return`?

`yield` pauses the function.

``` text
Create Session
      │
yield session
      │
Route Executes
      │
Resume
      │
Session Closes
```

If `return` were used, cleanup after the route finishes would not happen
automatically.

------------------------------------------------------------------------

# Request Flow

``` text
Client
   │
   ▼
FastAPI Route
   │
Depends(get_db)
   │
Create AsyncSession
   │
await session.execute(...)
   │
Engine
   │
SQLite
   │
Response
   │
Session Closed
```

------------------------------------------------------------------------

# Common Mistakes

-   Forgetting to `await` async database calls.
-   Sharing one session globally.
-   Using `return` instead of `yield` in dependencies.
-   Mixing synchronous SQLAlchemy APIs with async routes.

------------------------------------------------------------------------

# Best Practices

-   One request = one database session.
-   Keep business logic out of `database.py`.
-   Use async drivers with async FastAPI routes.
-   Close sessions automatically using `yield`.

------------------------------------------------------------------------

# Quick Revision

-   **Engine** → manages database connections.
-   **AsyncSession** → performs database work.
-   **async_sessionmaker** → creates sessions.
-   **Base** → parent of all ORM models.
-   **get_db()** → provides one session per request.
-   **yield** → guarantees cleanup after the request.
