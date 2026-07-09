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
---

# FastAPI Application Lifespan

Modern FastAPI applications use **Lifespan** to manage resources that should be initialized once when the application starts and cleaned up once when the application stops.

Examples include:

- Database connections
- Database engines
- Redis connections
- Machine Learning models
- Cache initialization
- External API clients

Instead of initializing these resources on every request, they are initialized only once during application startup.

---

# Evolution of FastAPI Startup & Shutdown

## Old Method

Earlier versions of FastAPI recommended using two separate event decorators.

```python
@app.on_event("startup")
async def startup():
    ...

@app.on_event("shutdown")
async def shutdown():
    ...
```

Startup and shutdown logic were written in separate functions.

Although this still works in many applications, the recommended modern approach is to use **Lifespan**.

---

## Modern Method

```python
@asynccontextmanager
async def lifespan(app: FastAPI):

    ...

    yield

    ...
```

The lifespan function combines startup and shutdown logic into one place.

This makes resource management easier to understand and maintain.

---

# What is Lifespan?

Lifespan represents the complete lifecycle of the FastAPI application.

```
Application Starts
        │
        ▼
Startup Code
        │
        ▼
Application Running
        │
        ▼
Shutdown Code
        │
        ▼
Application Stops
```

Everything before `yield` executes only once during startup.

Everything after `yield` executes only once during shutdown.

---

# Why do we pass lifespan into FastAPI?

```python
app = FastAPI(
    lifespan=lifespan
)
```

Earlier we registered startup and shutdown functions separately.

Now we register one lifespan function.

Conceptually FastAPI performs something similar to

```python
async with lifespan(app):

    # Handle incoming requests
```

The lifespan function tells FastAPI

> "Use this function to manage the application's lifetime."

---

# Understanding Context Managers

Before understanding `asynccontextmanager`, it is important to understand what a Context Manager is.

Consider opening a file.

```python
with open("data.txt") as file:

    data = file.read()
```

Execution flow

```
Open File

↓

Use File

↓

Close File
```

The file is automatically closed even if an exception occurs.

A Context Manager is responsible for acquiring a resource and releasing it safely.

Common resources include

- Files
- Database connections
- Locks
- Network sockets
- Cache connections

---

# Why Context Managers?

Without a Context Manager

```python
file = open("data.txt")

data = file.read()

raise Exception()

file.close()
```

If an exception occurs,

```
file.close()
```

never executes.

The file remains open.

This is called a resource leak.

Context Managers guarantee proper cleanup.

---

# Context Manager vs Normal Function

A normal function simply executes and finishes.

```
Start

↓

Execute

↓

Return

↓

Finished
```

A Context Manager has three phases.

```
Enter

↓

Use Resource

↓

Exit
```

This makes it ideal for managing application resources.

---

# Synchronous Context Manager

Python provides

```python
from contextlib import contextmanager
```

Example

```python
from contextlib import contextmanager

@contextmanager
def demo():

    print("Enter")

    yield

    print("Exit")
```

Used with

```python
with demo():

    print("Inside")
```

Execution

```
Enter

↓

Inside

↓

Exit
```

---

# Asynchronous Context Manager

For asynchronous applications Python provides

```python
from contextlib import asynccontextmanager
```

Example

```python
@asynccontextmanager
async def demo():

    print("Enter")

    yield

    print("Exit")
```

Used with

```python
async with demo():

    print("Inside")
```

Execution

```
Enter

↓

Inside

↓

Exit
```

The concept is identical.

The only difference is that asynchronous resources require

```
async with
```

instead of

```
with
```

---

# What does @asynccontextmanager do?

`@asynccontextmanager` is **not** a FastAPI feature.

It is a Python feature from

```python
contextlib
```

Its purpose is to convert a normal asynchronous function into an asynchronous context manager.

Without it

```python
async def lifespan():

    ...
```

the function is just a normal async function.

It cannot be used with

```python
async with
```

After adding

```python
@asynccontextmanager
```

the function becomes an Async Context Manager that FastAPI can use.

---

# Difference Between Normal Async Function and Async Context Manager

## Normal Async Function

```python
async def hello():

    print("Hello")

    return
```

Execution

```
await hello()

↓

Start

↓

Execute

↓

Return

↓

Finished
```

Once it returns, execution is complete.

---

## Async Context Manager

```python
@asynccontextmanager
async def demo():

    print("Startup")

    yield

    print("Shutdown")
```

Execution

```
async with demo():

    print("Running")
```

Flow

```
Startup

↓

yield

↓

Running

↓

Shutdown
```

Unlike a normal async function, execution pauses at `yield` and resumes later.

---

# Understanding yield inside Lifespan

Inside the lifespan function,

`yield` separates startup and shutdown.

```
Before yield

↓

Startup Code

↓

yield

↓

Application Handles Requests

↓

After yield

↓

Shutdown Code
```

Everything before `yield`

- Executes once
- Before the server accepts requests

Everything after `yield`

- Executes once
- When the server is shutting down

---

# Does yield stop execution?

Yes.

`yield` pauses the function.

Execution resumes only after FastAPI finishes running the application.

Conceptually

```
Create Resources

↓

yield

↓

Server Runs For Hours

↓

Resume

↓

Release Resources
```

This behaviour makes lifespan ideal for resource management.

---

# Lifespan Flow in This Project

```python
@asynccontextmanager
async def lifespan(app: FastAPI):

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()
```

Execution

```
Application Starts

↓

Create Database Tables

↓

yield

════════════════════════════════════

Application Running

GET /users

POST /posts

GET /

PATCH /users

...

════════════════════════════════════

↓

Server Stops

↓

Dispose Database Engine

↓

Application Ends
```

---

# Why do we use Lifespan?

Resources like database engines should

- be created once
- be reused
- be closed properly

Lifespan provides a single place to perform startup and shutdown work.

This keeps initialization logic together and avoids splitting related code across multiple functions.

---

# Why is Lifespan preferred over @app.on_event?

Old approach

```
startup()

...

shutdown()
```

Two different functions.

Modern approach

```
lifespan()

↓

Startup

↓

Application Running

↓

Shutdown
```

Everything related to the application's lifetime is grouped together.

This improves readability and follows the ASGI Lifespan specification used by FastAPI.

---

# Key Takeaways

- Lifespan represents the complete lifecycle of the application.
- Everything before `yield` executes once during startup.
- Everything after `yield` executes once during shutdown.
- `@asynccontextmanager` is a Python feature, not a FastAPI feature.
- It converts a normal async function into an Async Context Manager.
- FastAPI internally uses the lifespan function as an asynchronous context manager.
- `yield` pauses execution while the application serves requests.
- Lifespan replaces the older startup/shutdown event approach and is the recommended modern pattern.