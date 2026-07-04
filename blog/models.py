# models.py — Defines database structure. Each class = one table, each variable = one column.
# SQLAlchemy reads this and creates actual tables in the database.

from sqlalchemy import String, Text, ForeignKey, Integer, DateTime  # column data types
from sqlalchemy.orm import mapped_column, Mapped, relationship       # FIX: 'relationship' not 'Relationship'
from datetime import datetime, UTC                                   # FIX: was missing this import
from blog.database import Base                                            # parent class — connects models to DB


class User(Base):
    # __tablename__ — actual SQL table name. Python uses 'User', SQL uses 'users'
    __tablename__ = "users"

    # PRIMARY KEY — unique ID per row. index=True makes search faster. 
    # Mapped is used to tell sqlalchemy that this is a column in the database and the type of data it will hold
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # mapped_column() defines the column. String(50) = max length. nullable=False = required. unique=True = no duplicates.
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    
    email: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)

 # -----------------------------------------------------------------------------
# Q: How are images stored in a database?
#
# A:
# Usually we do NOT store the actual image inside the database.
#
# Instead:
#   1. Save the image file in a folder:
#        media/profile_pics/rahul.jpg
#
#   2. Store only the filename in the database:
#        image_file = "rahul.jpg"
#
# Benefits:
#   - Smaller database
#   - Faster queries
#   - Easier file management
#
# Database:
#   id | username | image_file
#   1  | Rahul    | rahul.jpg
#
# Folder:
#   media/profile_pics/rahul.jpg
#
# The image_file column stores only a reference to the image.
    image_file: Mapped[str | None] = mapped_column(String(120), default=None, nullable=True)
# -----------------------------------------------------------------------------

    # RELATIONSHIP — Python-only link. Lets you do: user.posts → get all posts by this user.
    # FIX: was mapped_column(Relationship(...)) — relationship() is NOT a column, remove mapped_column()
    # FIX: "Post" in quotes because Post class is not defined yet at this point
    # ForeignKey = database link (stores user_id number) | relationship = Python access (gives full object)
    posts: Mapped[list["Post"]] = relationship(back_populates="author",cascade="all, delete-orphan")

# -----------------------------------------------------------------------------
# Q: What does @property do?
#
# A:
# @property lets us use a method like a normal attribute.
#
# Without @property:
#     user.image_path()
#
# With @property:
#     user.image_path
#
# Used when a value is COMPUTED instead of stored in the database.
#
# Example:
#     image_file = "rahul.jpg"
#
#     @property
#     def image_path(self):
#         return f"/media/profile_pics/{self.image_file}"
#
# Result:
#     user.image_path
#     -> "/media/profile_pics/rahul.jpg"
#
# Benefits:
#   - No need to store full path in DB
#   - Path updates automatically
#   - Cleaner code
#
# Think:
#   image_file = stored value
#   image_path = computed value
# -----------------------------------------------------------------------------
    # @property — computed value, NOT stored in DB. Access as user.image_path (no brackets).
    # Pydantic/FastAPI calls this automatically when converting User object to JSON response.
    # Why not store full path? If folder moves, all stored paths break. Filename is safer.
    @property
    def image_path(self) -> str:
        if self.image_file:
            return f"/media/profile_pics/{self.image_file}"
        return "/static/profile_pics/default.jpg"  # fallback if no photo uploaded

# self = current User object.
# It lets Python know which user's data to use.
#
# user1.image_path -> uses user1.image_file
# user2.image_path -> uses user2.image_file
#
# -> str means this method returns a string.
# It is a type hint for readability and editor support.

class Post(Base):
    # __tablename__ — actual SQL table name. Python uses 'Post', SQL uses 'posts'
    __tablename__ = "posts"

    # PRIMARY KEY — unique ID per post. index=True makes search faster.
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    title: Mapped[str] = mapped_column(String(50), nullable=False)   # required
    content: Mapped[str] = mapped_column(Text, nullable=False)        # FIX: Text() not String(120) — 120 chars too short for post content

    # FOREIGN KEY — database-level link to users table. Stores user's id (e.g. 3), not the full user.
    # Ensures every post belongs to a valid user. index=True = fast lookup when fetching posts by user.
    # Relationship flow: user.id ←→ post.user_id | user.posts → all posts | post.author → user object
    # One-to-many: one user can have many posts.
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    # Stores post creation time. lambda = runs fresh on each insert (without lambda, all posts get same timestamp).
    date_posted: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    # RELATIONSHIP — Python-only link. Lets you do: post.author → get the full User object.
    author: Mapped["User"] = relationship(back_populates="posts")


# =============================================================================
# MODELS.PY QUICK REVISION (Questions I Asked While Learning)
# =============================================================================
#
# Q: What is models.py?
# A: Defines database tables using Python classes.
#    Each class = one table.
#    Each mapped_column = one database column.

# -----------------------------------------------------------------------------
# Q: What is __tablename__?
#
# __tablename__ = "users"
#
# A:
# Actual table name inside SQLite/database.
#
# Python:
#     User
#
# Database:
#     users
#
# Used by SQLAlchemy when generating SQL queries and ForeignKeys.
# There is Two level one is Orm and second is database level
#
# -----------------------------------------------------------------------------
# Q: Why use Mapped[int] instead of just int?
#
# id: Mapped[int]
#
# A:
# Tells SQLAlchemy:
#   1. This attribute belongs to ORM
#   2. It stores an integer
#
# Pydantic:
#     age: int
#
# SQLAlchemy:
#     age: Mapped[int]
#
# Mapped = ORM-managed attribute and also used to show relationship 
#
# -----------------------------------------------------------------------------
# Q: What is mapped_column()?
#
# username: Mapped[str] = mapped_column(String(50))
#
# A:
# Creates a real database column.
#
# Lets us define:
#   type
#   nullable
#   unique
#   default
#   primary key
#   index
#
# Think:
#     Pydantic -> Field()
#     SQLAlchemy -> mapped_column()
#
# -----------------------------------------------------------------------------
# Q: What is primary_key=True?
#
# A:
# Makes column unique identifier.
#
# No duplicates.
# Cannot be NULL.
#
# Example:
#     User 1
#     User 2
#     User 3
#
# -----------------------------------------------------------------------------
# Q: Is primary key automatically incremented?
#
# A:
# Yes.
#
# SQLite automatically generates:
#
# 1
# 2
# 3
# 4
#
# No need to manually increment ids.
#
# -----------------------------------------------------------------------------
# Q: What is index=True?
#
# A:
# Makes searching faster.
#
# Database creates a special lookup structure.
#
# Like book index:
#
# Without index:
#     search page by page
#
# With index:
#     jump directly to page
#
# Use on:
#     id
#     user_id
#     email
#     username
#
# -----------------------------------------------------------------------------
# Q: Why ForeignKey("users.id") uses table name not class name?
#
# user_id = mapped_column(
#     ForeignKey("users.id")
# )
#
# A:
# ForeignKey works at DATABASE level.
#
# Database knows:
#     users table
#
# Database does NOT know:
#     User class
#
# Therefore:
#     ForeignKey("users.id")
#
# not:
#     ForeignKey("User.id")
#
# -----------------------------------------------------------------------------
# Q: Difference between ForeignKey and relationship?
#
# ForeignKey:
#     database connection
#
# relationship:
#     Python connection
#
# Example:
#
# ForeignKey stores:
#     user_id = 1
#
# relationship gives:
#     post.author
#     user.posts
#
# Think:
#     ForeignKey = DB link
#     relationship = Python access
#
# -----------------------------------------------------------------------------
# Q: Why use Mapped[list["Post"]]?
#
# posts: Mapped[list["Post"]] = relationship(...)
#
# A:
# user.posts returns MANY Post objects.
#
# Example:
#
# [
#     Post(...),
#     Post(...),
#     Post(...)
# ]
#
# Therefore datatype:
#
# list[Post]
#
# NOT:
#
# "posts"
#
# because "posts" is table name,
# while list[Post] is Python datatype.
#
# -----------------------------------------------------------------------------
# Q: Why "Post" is in quotes?
#
# posts: Mapped[list["Post"]]
#
# A:
# Post class is defined later in file.
#
# Quotes tell Python:
# "Resolve this type later."
#
# -----------------------------------------------------------------------------
# Q: How do relationships work practically?
#
# USERS TABLE
#
# id | username
# 1  | Rahul
#
#
# POSTS TABLE
#
# id | title | user_id
# 1  | A     | 1
# 2  | B     | 1
#
#
# user.posts
#
# returns:
#
# [
#     Post A,
#     Post B
# ]
#
#
# post.author
#
# returns:
#
# User Rahul
#
# relationship converts foreign keys into Python objects.
