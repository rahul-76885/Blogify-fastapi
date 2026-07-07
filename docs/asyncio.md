# Chapter 06 -- AsyncIO

**Related Files**

-   `database.py`
-   `__init__.py`
-   `frontend.py`
-   `users.py`
-   `posts.py`

------------------------------------------------------------------------

# Purpose

AsyncIO is the foundation of modern FastAPI applications.

It allows FastAPI to handle many concurrent requests efficiently while
waiting for slow I/O operations such as databases, APIs and files.

------------------------------------------------------------------------

# Learning Objectives

After this chapter you should understand:

-   Synchronous vs Asynchronous programming
-   Blocking vs Non-blocking I/O
-   Event Loop
-   Coroutines
-   `async`
-   `await`
-   Tasks
-   Futures
-   Async SQLAlchemy
-   `AsyncSession`
-   `create_async_engine`
-   Dependency Injection
-   `yield`
-   Connection Pooling
-   CPU-bound vs I/O-bound work

------------------------------------------------------------------------

# Why AsyncIO Exists

Traditional synchronous applications spend most of their time waiting.

``` text
Request

↓

Database

↓

Waiting...

↓

Continue
```

While waiting, the CPU is mostly idle.

AsyncIO solves this by allowing another request to run while the first
one waits.

------------------------------------------------------------------------

# Synchronous vs Asynchronous

## Synchronous

``` text
Request 1

↓

Wait

↓

Request 2

↓

Wait

↓

Request 3
```

## Asynchronous

``` text
Request 1

↓

Database Waiting

↘

Request 2 Runs

↘

Request 3 Runs

↘

Database Responds

↓

Resume Request 1
```

AsyncIO does **not** make the database faster.

It makes your server spend less time doing nothing.

------------------------------------------------------------------------

# Blocking vs Non-Blocking

Blocking means execution cannot continue until an operation finishes.

Examples:

-   Database query
-   HTTP request
-   File read
-   File upload

Non-blocking code pauses only the current coroutine and allows the Event
Loop to execute other work.

------------------------------------------------------------------------

# Event Loop

The Event Loop is the heart of AsyncIO.

It repeatedly performs:

``` text
Check Ready Tasks

↓

Run Tasks

↓

Pause Waiting Tasks

↓

Resume Completed Tasks

↓

Repeat
```

Every `async` function in FastAPI is executed by the Event Loop.

------------------------------------------------------------------------

# Coroutines

Functions declared with

``` python
async def
```

are coroutine functions.

Calling them creates a coroutine object.

Execution begins only when the Event Loop schedules it.

------------------------------------------------------------------------

# async

`async` tells Python that a function may pause and later resume
execution.

Example:

``` python
async def home():
    ...
```

------------------------------------------------------------------------

# await

`await` means:

> Pause this coroutine until the awaited operation completes.

Example:

``` python
await db.execute(query)
```

Only the current coroutine pauses.

The Event Loop immediately switches to another ready task.

------------------------------------------------------------------------

# Tasks

A Task is a coroutine scheduled by the Event Loop.

``` text
Coroutine

↓

Event Loop

↓

Task

↓

Execution
```

------------------------------------------------------------------------

# Futures

A Future represents a result that is not available yet.

``` text
Database Query

↓

Future

↓

Completed Result
```

Tasks internally build upon Futures.

------------------------------------------------------------------------

# AsyncIO in Your FastAPI Project

Your project follows this flow:

``` text
Client

↓

FastAPI

↓

Router

↓

Depends(get_db)

↓

AsyncSession

↓

await db.execute()

↓

Database

↓

Response
```

------------------------------------------------------------------------

# create_async_engine()

Creates an asynchronous SQLAlchemy engine.

Use it instead of `create_engine()` so database operations do not block
the Event Loop.

------------------------------------------------------------------------

# AsyncSession

Each request receives its own database session.

``` text
Request A → Session A

Request B → Session B

Request C → Session C
```

Sessions should never be shared across requests.

------------------------------------------------------------------------

# async_sessionmaker()

Acts as a session factory.

``` text
Need Session

↓

Session Factory

↓

New AsyncSession
```

------------------------------------------------------------------------

# Why get_db() Uses yield

``` python
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

Flow:

``` text
Create Session

↓

Yield Session

↓

Route Executes

↓

Request Finishes

↓

Session Closed
```

`yield` allows FastAPI to clean up resources automatically.

------------------------------------------------------------------------

# Depends(get_db)

``` python
db: Annotated[AsyncSession, Depends(get_db)]
```

FastAPI automatically:

``` text
Request

↓

Create Session

↓

Inject Session

↓

Execute Route

↓

Close Session
```

------------------------------------------------------------------------

# What Happens During await db.execute()

``` text
Route Starts

↓

Send SQL Query

↓

Database Working

↓

Coroutine Paused

↓

Event Loop Executes Another Request

↓

Database Responds

↓

Resume Coroutine

↓

Continue Route
```

------------------------------------------------------------------------

# Connection Pooling

Opening database connections is expensive.

Instead, SQLAlchemy reuses existing connections.

``` text
Connection Pool

↓

Reuse Connection

↓

Better Performance
```

------------------------------------------------------------------------

# CPU-bound vs I/O-bound

## I/O-bound

-   Database
-   HTTP APIs
-   Redis
-   File operations
-   Cloud Storage

Best choice: **AsyncIO**

## CPU-bound

-   AI
-   Machine Learning
-   Image Processing
-   Video Encoding
-   Large computations

Best choice: **Multiprocessing / Workers**

------------------------------------------------------------------------

# Concurrency vs Parallelism

## Concurrency

One thread manages many waiting tasks.

``` text
Task A

↓

Waiting

↘

Task B

↘

Task C

↓

Resume
```

## Parallelism

Multiple CPU cores execute tasks simultaneously.

``` text
CPU 1 → Task A

CPU 2 → Task B

CPU 3 → Task C
```

AsyncIO provides concurrency, not parallel CPU execution.

------------------------------------------------------------------------

# AsyncIO vs Threads vs Multiprocessing

  Feature        AsyncIO     Threads        Multiprocessing
  -------------- ----------- -------------- -----------------
  Best For       I/O         Blocking I/O   CPU Work
  Memory         Low         Medium         High
  Parallel CPU   No          Limited        Yes
  FastAPI        Excellent   Sometimes      Background Jobs

------------------------------------------------------------------------

# Common Mistakes

-   Forgetting `await`
-   Mixing sync and async SQLAlchemy
-   Sharing one AsyncSession globally
-   Using blocking libraries inside async routes
-   Thinking AsyncIO makes CPU work faster

------------------------------------------------------------------------

# Best Practices

-   Use `async def` for I/O-heavy routes.
-   Await every asynchronous operation.
-   Use one `AsyncSession` per request.
-   Keep CPU-heavy work outside request handlers.
-   Use dependency injection for session management.

------------------------------------------------------------------------

# Interview Questions

-   What is AsyncIO?
-   What is the Event Loop?
-   What is a coroutine?
-   What does `await` do?
-   AsyncIO vs Threads?
-   AsyncIO vs Multiprocessing?
-   Why does FastAPI use AsyncIO?
-   Why use `AsyncSession`?
-   Why does `get_db()` use `yield`?
-   Does AsyncIO make code faster?

------------------------------------------------------------------------

# Quick Revision

``` text
FastAPI

↓

ASGI

↓

Event Loop

↓

Coroutine

↓

await

↓

AsyncSession

↓

Database

↓

Response


I/O-bound → AsyncIO

CPU-bound → Multiprocessing
```

------------------------------------------------------------------------

# Key Takeaways

-   AsyncIO improves concurrency, not CPU speed.
-   The Event Loop manages coroutine execution.
-   `async` creates coroutine functions.
-   `await` pauses only the current coroutine.
-   FastAPI uses AsyncIO because web applications are mostly I/O-bound.
-   `AsyncSession` enables non-blocking database access.
-   `Depends(get_db)` provides one session per request.
-   Use AsyncIO for scalable APIs.
