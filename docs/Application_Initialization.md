# Application Initialization

> **Source Code**
>
> `blog/__init__.py`

------------------------------------------------------------------------

# 📖 Purpose

`blog/__init__.py` is the bootstrap module of the application.

Its responsibility is **not** to implement business logic. Instead, it
prepares the FastAPI application before it starts handling requests.

Responsibilities:

-   Create the FastAPI application.
-   Configure shared framework components.
-   Mount Static and Media directories.
-   Configure the Jinja2 template engine.
-   Register application routes.

------------------------------------------------------------------------

# 🎯 Learning Objectives

After this chapter you should understand:

-   Why FastAPI requires `FastAPI()`
-   Why initialization is explicit
-   What an ASGI application is
-   Why `StaticFiles` is mounted
-   Why templates are configured explicitly
-   Why `__init__.py` should remain small

------------------------------------------------------------------------

# 🧠 Mental Model

Think of `__init__.py` as turning on a new office before employees
arrive.

``` text
Unlock Building
      │
      ▼
Turn On Electricity
      │
      ▼
Prepare Workstations
      │
      ▼
Employees Start Working
```

FastAPI follows the same idea.

``` text
Create FastAPI
      │
      ▼
Mount Static
      │
      ▼
Mount Media
      │
      ▼
Configure Templates
      │
      ▼
Register Routes
      │
      ▼
Application Ready
```

------------------------------------------------------------------------

# 🏗 High-Level Architecture

``` text
                 blog/__init__.py
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
   FastAPI App     StaticFiles      Templates
        │
        ▼
  Route Registration
        │
        ▼
 Application Ready
```

------------------------------------------------------------------------

# 🔬 Deep Dive

## FastAPI()

``` python
app = FastAPI()
```

This creates the application's central ASGI object.

Everything is registered against it:

-   Routers
-   Middleware
-   Exception Handlers
-   Startup Events
-   Mounted Applications
-   OpenAPI Documentation

------------------------------------------------------------------------

## What is ASGI?

ASGI stands for **Asynchronous Server Gateway Interface**.

The real request path is:

``` text
Browser
   │
HTTP Request
   │
   ▼
Uvicorn
   │
ASGI Protocol
   │
   ▼
FastAPI
```

`FastAPI()` does **not** start the server.

Uvicorn starts the server and forwards requests to the FastAPI
application.

------------------------------------------------------------------------

## Static Files

``` python
app.mount("/static", ...)
```

Static assets:

-   CSS
-   JavaScript
-   Fonts
-   Icons
-   Logos

Internal flow:

``` text
Browser
   │
GET /static/style.css
   │
   ▼
FastAPI
   │
Matches "/static"
   │
   ▼
StaticFiles
   │
Read File
   │
   ▼
Browser
```

Notice that no route function is executed.

------------------------------------------------------------------------

## Why FastAPI is Explicit

FastAPI intentionally avoids hidden framework behavior.

Instead of discovering folders automatically, the developer registers
every component explicitly.

Benefits:

-   Predictable
-   Easier debugging
-   Easier testing
-   Better scalability

This follows the Zen of Python:

> Explicit is better than implicit.

------------------------------------------------------------------------

## Media Files

Media contains user-generated content.

Examples:

-   Profile Pictures
-   Uploaded Documents
-   Attachments

Keeping media separate from static assets makes future cloud storage
migration much easier.

------------------------------------------------------------------------

## Templates

``` python
templates = Jinja2Templates(...)
```

FastAPI does not expose a global `render_template()` helper.

Instead, a reusable template renderer is created and shared across
routes.

------------------------------------------------------------------------

# 🌍 Flask vs FastAPI

  Flask                   FastAPI
  ----------------------- ------------------------
  Auto discovers static   Manual mount
  `render_template()`     `Jinja2Templates`
  WSGI                    ASGI
  More implicit           Explicit configuration

------------------------------------------------------------------------

# 💡 Production Notes

A production `__init__.py` should only:

-   Create the application.
-   Configure framework components.
-   Register routes.

Avoid putting:

-   SQL queries
-   Business logic
-   Validation logic
-   Utility functions

inside this file.

------------------------------------------------------------------------

# ⚠ Common Mistakes

-   Multiple FastAPI application instances.
-   Business logic inside `__init__.py`.
-   Mixing uploaded media with application assets.
-   Using `__init__.py` for route implementations.

------------------------------------------------------------------------

# 🎤 Interview Questions

1.  Why does FastAPI require `FastAPI()`?
2.  Why is FastAPI considered explicit?
3.  What does `app.mount()` do?
4.  What is an ASGI application?
5.  Why separate static and media directories?

------------------------------------------------------------------------

# 📝 Quick Revision

``` text
Create FastAPI
      │
      ▼
Mount Static
      │
      ▼
Mount Media
      │
      ▼
Configure Templates
      │
      ▼
Register Routes
      │
      ▼
Application Ready
```

------------------------------------------------------------------------

# 🧠 Knowledge Check

Can you answer these without looking?

-   Why doesn't FastAPI auto-discover static files?
-   What is ASGI?
-   Why is `app.mount()` different from `include_router()`?
-   Why should `__init__.py` remain small?

------------------------------------------------------------------------

# 🔗 Related Chapters

-   Database
-   Routing
-   Dependency Injection
-   Request Lifecycle
-   Jinja2
-   Static Files
-   AsyncIO


# Application Initialization

This document explains how the FastAPI application is initialized, why each component exists, and how the application starts internally.

---

# Application Startup Flow

When the following command is executed:

```bash
fastapi dev blog
```

FastAPI does **not** immediately start accepting requests.

Instead, it performs several initialization steps.

```
fastapi dev blog
        │
        ▼
Import Python Package (blog)
        │
        ▼
Execute blog/__init__.py
        │
        ▼
Create FastAPI Application
        │
        ▼
Mount Static & Media Directories
        │
        ▼
Register Routers
        │
        ▼
Register Exception Handlers
        │
        ▼
Execute Lifespan Startup Code
        │
        ▼
Start Accepting Requests
```

---

# Why do we run

```bash
fastapi dev blog
```

instead of

```bash
fastapi dev __init__.py
```

or

```bash
fastapi dev database.py
```

The folder **blog** is a Python package because it contains

```python
__init__.py
```

When Python imports a package, it automatically executes its `__init__.py`.

Conceptually:

```python
import blog
```

becomes

```
Execute blog/__init__.py
```

Since the FastAPI application is created inside `blog/__init__.py`

```python
app = FastAPI(...)
```

FastAPI automatically finds

```python
blog.app
```

and starts the application.

---

# Why do we use Path?

Instead of writing

```python
directory="static"
```

we write

```python
BASE_DIR = Path(__file__).resolve().parent

BASE_DIR / "static"
```

## What is Path?

`Path` is a Python class from the `pathlib` module used to represent filesystem paths.

Just like

- `list` represents collections
- `dict` represents key-value pairs

`Path` represents files and directories.

Unlike strings, a Path object provides useful filesystem operations.

Example

```python
path.exists()
path.parent
path.name
path.is_file()
path.is_dir()
path.resolve()
```

---

# Why not simply use strings?

Instead of

```python
"blog/static"
```

Path allows

```python
BASE_DIR / "static"
```

Benefits:

- Cross-platform
- Cleaner syntax
- Avoids manual path concatenation
- Provides useful methods
- Recommended modern Python approach

---

# Understanding __file__

Python automatically creates

```python
__file__
```

inside every module.

Inside

```
blog/__init__.py
```

it becomes

```
C:\Projects\BlogWebsite\blog\__init__.py
```

---

# Understanding resolve()

```python
Path(__file__).resolve()
```

returns the absolute path.

Example

```
blog/__init__.py

↓

C:\Projects\BlogWebsite\blog\__init__.py
```

---

# Understanding parent

```python
Path(__file__).resolve().parent
```

returns

```
C:\Projects\BlogWebsite\blog
```

which is stored in

```python
BASE_DIR
```

---

# Why do we need BASE_DIR?

Suppose the project structure is

```
BlogWebsite/

    blog/
        static/
```

If we write

```python
directory="static"
```

Python searches

```
BlogWebsite/static
```

because it searches relative to the Current Working Directory (CWD).

That directory doesn't exist.

Using

```python
BASE_DIR / "static"
```

always points to

```
BlogWebsite/blog/static
```

regardless of where the application is executed.

---

# Current Working Directory (CWD)

Many beginners confuse

```
Current Working Directory
```

with

```
Current File Location
```

They are completely different.

Current Working Directory depends on where the application is executed.

Current File Location is determined using

```python
__file__
```

Using `Path(__file__)` makes the application independent of the working directory.

---

# Creating the FastAPI Application

```python
app = FastAPI(...)
```

creates one FastAPI object.

Conceptually

```
FastAPI Object

├── Routes
├── Middleware
├── Exception Handlers
├── Lifespan
├── OpenAPI
└── Dependencies
```

Everything in the application is registered into this object.

---

# Why pass app into functions?

Example

```python
register_routers(app)
```

The FastAPI object is **not imported**.

It is **passed as an argument**.

Exactly like

```python
student = Student()

print_name(student)
```

Inside

```python
def register_routers(app: FastAPI):
```

the parameter `app` refers to the exact same FastAPI object.

No copy is created.

---

# Understanding

```python
def register_routers(app: FastAPI) -> None:
```

## app

The FastAPI application object.

---

## : FastAPI

Type Hint.

It tells Python developers and IDEs

> This parameter should be a FastAPI object.

It is not required for execution.

---

## -> None

Indicates that the function returns nothing.

Its purpose is only to modify the FastAPI application.

---

# Why use register_routers()

Instead of writing

```python
app.include_router(users_router)

app.include_router(posts_router)

app.include_router(frontend_router)
```

inside the main application file,

we move everything into

```python
register_routers(app)
```

Benefits

- Cleaner main file
- Easier maintenance
- Single place for router registration
- Easy to add new routers later

---

# include_router()

Each APIRouter stores routes internally.

Example

```
users_router

GET /{id}

POST /

PATCH /{id}

DELETE /{id}
```

When

```python
app.include_router(users_router)
```

is executed,

FastAPI copies those routes into the application's routing table.

Conceptually

```
users_router

↓

app.routes
```

Without calling

```python
include_router()
```

FastAPI would never know those routes exist.

---

# Understanding Prefix

Suppose

```python
@router.get("/{id}")
```

Without a prefix

```
/{id}
```

With

```python
prefix="/api/users"
```

FastAPI automatically creates

```
/api/users/{id}
```

No need to repeat

```
/api/users
```

for every endpoint.

---

# Understanding Tags

```python
tags=["Users"]
```

Tags are used only by Swagger/OpenAPI documentation.

They organize endpoints into groups.

They do not affect routing.

---

# Exception Handler Registration

FastAPI already has default exception handlers.

When

```python
raise HTTPException(...)
```

occurs,

FastAPI automatically returns

```json
{
    "detail": "..."
}
```

When custom behaviour is required,

we create our own handler.

Example

```python
async def general_http_exception_handler(...)
```

Creating the function is **not enough**.

FastAPI has no way to know it should use that function.

Therefore we explicitly register it.

```python
app.add_exception_handler(
    HTTPException,
    general_http_exception_handler
)
```

Meaning

```
HTTPException

↓

general_http_exception_handler()
```

---

# Why register_exception_handlers()

Instead of

```python
app.add_exception_handler(...)

app.add_exception_handler(...)
```

inside the main application,

we wrap them inside

```python
register_exception_handlers(app)
```

Benefits

- Cleaner architecture
- Single registration point
- Easy expansion
- Better project organization

---

# Why template_env.py?

The template engine could be created inside

```
__init__.py
```

However, placing it inside

```
template_env.py
```

follows the Single Responsibility Principle.

Responsibilities become

```
__init__.py

↓

Application Initialization
```

```
template_env.py

↓

Jinja Template Configuration
```

Benefits

- Cleaner architecture
- Better separation of concerns
- Easier reuse
- Avoids potential circular imports
- Easier maintenance

---

# FastAPI Registration Pattern

Almost everything in FastAPI is created first and then registered with the application.

Routes

```python
app.include_router(router)
```

Exception Handlers

```python
app.add_exception_handler(...)
```

Middleware

```python
app.add_middleware(...)
```

Static Files

```python
app.mount(...)
```

Lifespan

```python
FastAPI(
    lifespan=lifespan
)
```

This registration pattern is one of the core architectural ideas of FastAPI.

The FastAPI application object acts as the central registry for everything that belongs to the application.

---

# Key Takeaways

- `blog` is a Python package because it contains `__init__.py`.
- `fastapi dev blog` imports the package and executes `blog/__init__.py`.
- `Path` is Python's modern filesystem path object.
- `BASE_DIR` ensures file paths work regardless of the current working directory.
- `app = FastAPI()` creates the application's central object.
- Routers, exception handlers, middleware, lifespan, and static files are all registered into the same FastAPI object.
- `register_routers()` and `register_exception_handlers()` improve project organization by keeping the application entry point clean.