from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
#------------------------------------------------------------------------------------------------
# FastAPI() needs no args. Flask needs __name__ to auto-find folders.
# FastAPI is explicit — you configure everything yourself.
#------------------------------------------------------------------------------------------------
app = FastAPI()
# Here we create an instance of FastAPI so we can attach routes, configurations, and endpoints to the application.
# Flask auto-serves static/ with zero config.
# FastAPI requires explicit mounting — it's API-first, static is optional.
# name="static" lets templates use: {{ request.url_for('static', path='...') }}
app.mount("/static", StaticFiles(directory="blog/static"), name="static")

# Flask auto-discovers templates/ folder.
# FastAPI needs an explicit object — no hidden globals, fully testable.
templates = Jinja2Templates(directory="blog/templates")

from blog import routes













# User opens website
#         │
#         ▼
# Browser sends request
# GET /
#         │
#         ▼
# FastAPI route
# @app.get("/")
#         │
#         ▼
# Jinja loads template
# templates/home.html
#         │
#         ▼
# Browser receives HTML
#         │
#         ▼
# HTML contains static links --> converted in url using request 
# /static/style.css
# /static/logo.png
#         │
#         ▼
# Browser sends new requests
# GET /static/style.css
# GET /static/logo.png
#         │
#         ▼
# FastAPI StaticFiles serves them
# static/style.css
# static/logo.png
#         │
#         ▼
# Browser renders full webpage




### NOTES 

# -----------------------------------------------------------------------------
# WHY: app.mount("/static", ...) — Manual static file mounting
# -----------------------------------------------------------------------------
#
# FLASK behavior (automatic):
#   You create a folder called 'static/' next to your app.
#   Flask serves it at /static/... automatically. Zero config.
#   In templates: url_for('static', filename='style.css') → /static/style.css
#
# FASTAPI behavior (explicit):
#   FastAPI does NOT auto-serve any folder. You must mount it yourself.
#
# WHY FastAPI made this choice:
#   FastAPI is an API-first framework. Most APIs never serve static files.
#   Auto-mounting a 'static/' folder would be "magic" — something happening
#   behind the scenes that you didn't ask for.
#
#   Explicit mounting gives you:
#   ✅ Mount multiple folders at different URLs (e.g., /static AND /uploads)
#   ✅ Mount only when you actually need it
#   ✅ Full control over which disk path maps to which URL
#   ✅ No surprise routes you didn't know about
#
# How StaticFiles works under the hood:
#   It's a mini ASGI app mounted at a sub-path.
#   When a request hits /static/..., FastAPI hands it to StaticFiles,
#   which reads the file from disk and sends it back directly.
#   Your Python route functions are never called for static files.
#
# Parameter breakdown:
#   "/static"          → URL prefix. Browser requests /static/style.css
#   directory="static" → Folder on disk (relative to where you run uvicorn)
#                        IMPORTANT: Run from FAST_API_BLOG/, not from blog/
#   name="static"      → Internal alias used in templates:
#                        {{ request.url_for('static', path='style.css') }}

# -----------------------------------------------------------------------------
# WHY: Jinja2Templates — Explicit template engine setup
# -----------------------------------------------------------------------------
#
# FLASK behavior (automatic):
#   Flask auto-discovers templates/ next to your app file.
#   render_template("home.html") works with zero setup.
#   Flask uses a global app context internally.
#
# FASTAPI behavior (explicit):
#   You create a Jinja2Templates object and import/use it in route files.
#   There is NO global app context. 'templates' is just a plain Python object.
#
# WHY this matters:
#   ✅ You can have MULTIPLE template objects (e.g., one for admin, one for users)
#   ✅ Easier to test — you can mock or swap the templates object
#   ✅ No hidden global state — all dependencies are visible in code
#   ✅ You can pass it as a dependency using FastAPI's Depends() system
#
# This 'templates' object is exported and imported in routes.py
# IMPORTANT: Paths are relative to where you run uvicorn (FAST_API_BLOG/ root)
# -----------------------------------------------------------------------------
