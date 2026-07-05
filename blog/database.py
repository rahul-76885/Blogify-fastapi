from sqlalchemy.ext.asyncio  import AsyncSession, create_async_engine ,async_sessionmaker
from sqlalchemy.orm import  DeclarativeBase

# ---------------------------------------------------------------------------
# Database location
# ---------------------------------------------------------------------------
#
# sqlite:///   → database type = SQLite (file-based, no server needed)
# ./blog.db    → file created in project root on first run
#
# project/
#    blog.db   ← tables live here

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./blog.db"


# ---------------------------------------------------------------------------
# Engine  —  the connection manager
# ---------------------------------------------------------------------------
#
# Every query travels through the engine:
#
#   FastAPI → SQLAlchemy → ENGINE → database
#
# Internally the engine:
#   1. opens a connection
#   2. sends SQL
#   3. receives results
#
# check_same_thread=False
#   SQLite default: only the thread that created a connection may use it.
#   FastAPI handles multiple requests across threads simultaneously.
#   Without this → crash: "SQLite objects created in a thread can only
#   be used in that same thread."

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)


# ---------------------------------------------------------------------------
# Session factory  —  creates database sessions on demand
# ---------------------------------------------------------------------------
#
# A session = one conversation with the database:
#
#   open session → run queries → commit → close session
#
# SessionLocal()  creates a new session each time it is called.
#
# autocommit=False  → you must call db.commit() manually.
#                     prevents accidental writes.
#
# autoflush=False   → SQLAlchemy won't push pending changes to the DB
#                     before queries automatically. You stay in control.
#
# bind=engine       → every session created here talks to this engine.

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ---------------------------------------------------------------------------
# Base class  —  parent for all ORM models (tables)
# ---------------------------------------------------------------------------
#
# All models inherit from Base:
#   class User(Base): ...
#   class Post(Base): ...
#
# Base tracks every model automatically.
# Later in main.py:
#   Base.metadata.create_all(bind=engine)
#   → SQLAlchemy scans all Base subclasses and creates their tables.

# -----------------------------------------------------------------------------
# Q: Why do we create a Base class and inherit User/Post from Base?
#
# Instead of:
#     class User(DeclarativeBase):
#     class Post(DeclarativeBase):
#
# Why not inherit directly from DeclarativeBase?
#
# A:
# DeclarativeBase is SQLAlchemy's root ORM class.
#
# We create:
#
#     class Base(DeclarativeBase):
#         pass
#
# so that ALL models share ONE common parent.
#
# Then:
#
#     class User(Base)
#     class Post(Base)
#
# SQLAlchemy can track every model through Base.
#
# This allows:
#
#     Base.metadata.create_all(bind=engine)
#
# to automatically find and create all tables
# (User, Post, Comment, etc.).
#
# If every model inherited directly from DeclarativeBase,
# each model would have its own registry/metadata and SQLAlchemy
# could not easily manage all tables together.
#
# Think of it like:
#
#     DeclarativeBase = SQLAlchemy blueprint machine
#     Base            = project's master blueprint
#     User/Post       = actual tables built from that blueprint
#
# So Base is not a useless middleman.
# It acts as a central registry that groups all models together.
# -----------------------------------------------------------------------------

class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------------------------
# Database dependency  —  provides a session to every route that needs one
# ---------------------------------------------------------------------------
#
# yield (not return)
#   Turns this into a generator — the function pauses at yield, hands the
#   session to the route, and resumes (to close the session) only after
#   the request finishes. return would end the function immediately,
#   leaving no chance to clean up.
#
# with SessionLocal() as db:
#   Context manager equivalent of:
#     db = SessionLocal()
#     try: ...
#     finally: db.close()
#   Session is always closed safely, even if the route raises an error.
#
# Full lifecycle per request:
#
#   client request arrives
#         │
#   FastAPI calls get_db()        ← triggered by Depends(get_db)
#         │
#   session created
#         │
#   yield db  ──────────────────► route receives db
#         │ (paused)                    │
#         │                       db.query() / db.add() / db.commit()
#         │                            │
#   request finishes  ◄──────────────
#         │
#   function resumes → session closes
#
# Used in routes as:
#   db: Annotated[Session, Depends(get_db)]
#   FastAPI automatically calls get_db(), injects the session, and
#   handles cleanup — you never call get_db() manually.
#
# Design goal: 1 request = 1 session
#   Prevents session conflicts, memory leaks, and shared state
#   between requests.

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
        