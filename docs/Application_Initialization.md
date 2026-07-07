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
