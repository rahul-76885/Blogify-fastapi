# Chapter 03 -- Models (`models.py`)

**Source File:** `blog/models.py`

------------------------------------------------------------------------

# Purpose

The `models.py` file defines the structure of your database using Python
classes.

It tells SQLAlchemy:

-   What tables should exist.
-   What columns each table contains.
-   How tables are related.
-   What rules each column follows.

Routes interact with models, while SQLAlchemy converts model operations
into SQL.

------------------------------------------------------------------------

# Learning Objectives

After reading this chapter you should understand:

-   What a Model is
-   Why ORMs exist
-   Why SQLAlchemy is used
-   Why models inherit from `Base`
-   What `__tablename__` does
-   What `Mapped` and `mapped_column()` are
-   Primary Keys and Indexes
-   Foreign Keys and Relationships
-   `back_populates`
-   `@property`

------------------------------------------------------------------------

# File Overview

``` text
models.py
│
├── User Model
│   ├── Columns
│   ├── Relationship
│   └── Computed Property
│
├── Post Model
│   ├── Columns
│   └── Relationship
│
└── SQLAlchemy ORM Configuration
```

------------------------------------------------------------------------

# What is a Model?

A model is a Python class that represents a database table.

``` python
class User(Base):
    __tablename__ = "users"
```

``` text
Python Class
      │
      ▼
SQLAlchemy ORM
      │
      ▼
Database Table
```

------------------------------------------------------------------------

# Why do we need Models?

Without models, every operation requires writing SQL.

With SQLAlchemy models you work with Python objects instead.

``` text
Python Object
      │
      ▼
SQLAlchemy
      │
      ▼
SQL
      │
      ▼
Database
```

Advantages:

-   Cleaner code
-   Easier maintenance
-   Database independence
-   Better FastAPI integration

------------------------------------------------------------------------

# What is an ORM?

ORM = Object Relational Mapper.

-   **Object** → Python class
-   **Relational** → Database tables
-   **Mapper** → Converts between them

------------------------------------------------------------------------

# Why SQLAlchemy?

SQLAlchemy is Python's most popular ORM because it is:

-   Mature
-   Well documented
-   Production ready
-   Supports sync and async
-   Database independent

------------------------------------------------------------------------

# Why inherit from Base?

``` python
class User(Base):
```

`Base` registers every model with SQLAlchemy.

``` text
Base
│
├── User
├── Post
└── Comment
```

Without Base, SQLAlchemy treats it as a normal Python class.

------------------------------------------------------------------------

# **tablename**

``` python
__tablename__ = "users"
```

Python class name:

    User

Database table:

    users

The database only knows table names, not Python class names.

------------------------------------------------------------------------

# Mapped\[\]

``` python
id: Mapped[int]
```

`Mapped` tells SQLAlchemy:

> This attribute belongs to the ORM.

It is the SQLAlchemy 2.x way of declaring mapped attributes.

------------------------------------------------------------------------

# mapped_column()

``` python
username: Mapped[str] = mapped_column(
    String(50),
    nullable=False,
    unique=True
)
```

`Mapped` describes the Python type.

`mapped_column()` describes the database column.

Common parameters:

-   `primary_key=True`
-   `nullable=False`
-   `unique=True`
-   `default=...`
-   `index=True`

------------------------------------------------------------------------

# Primary Keys

A primary key uniquely identifies every row.

``` text
Users

ID | Username

1  | Rahul
2  | Aman
```

Every table should have one.

------------------------------------------------------------------------

# Indexes

Indexes speed up searching.

Without an index:

``` text
Database

↓

Row 1

↓

Row 2

↓

...

↓

Target Row
```

With an index:

``` text
Index

↓

Target Row
```

Use indexes for frequently searched columns like:

-   id
-   email
-   username
-   user_id

------------------------------------------------------------------------

# Column Types

Common types used in your project:

-   Integer
-   String
-   Text
-   DateTime

Use `Text` for long content such as blog posts.

------------------------------------------------------------------------

# Foreign Keys

``` python
ForeignKey("users.id")
```

A Foreign Key connects two tables.

``` text
posts.user_id

↓

users.id
```

It ensures every post belongs to a valid user.

------------------------------------------------------------------------

# relationship()

`relationship()` does **not** create a database column.

Instead, it creates a Python object relationship.

Database:

``` text
user_id = 1
```

Python:

``` python
post.author
```

returns

``` python
User(...)
```

------------------------------------------------------------------------

# ForeignKey vs relationship()

  ForeignKey            relationship()
  --------------------- -----------------------
  Database feature      Python feature
  Stores IDs            Returns objects
  Maintains integrity   Simplifies navigation

------------------------------------------------------------------------

# One-to-Many Relationship

``` text
User

↓

Post A

Post B

Post C
```

One user can have many posts.

Each post belongs to one user.

------------------------------------------------------------------------

# back_populates

``` text
User

↓

posts

↑

author

↓

Post
```

Allows navigation in both directions.

``` python
user.posts
```

and

``` python
post.author
```

------------------------------------------------------------------------

# Cascade Delete

``` python
cascade="all, delete-orphan"
```

Deleting a parent automatically removes dependent child records.

``` text
Delete User

↓

Delete Posts

↓

Database stays consistent
```

------------------------------------------------------------------------

# @property

Your model uses:

``` python
@property
def image_path(...):
```

This creates a computed value.

Database stores:

``` text
rahul.jpg
```

Property returns:

``` text
/media/profile_pics/rahul.jpg
```

Benefits:

-   Smaller database
-   Flexible paths
-   Cleaner design

------------------------------------------------------------------------

# Flow

``` text
Client

↓

FastAPI Route

↓

SQLAlchemy Model

↓

Engine

↓

Database

↓

Python Object

↓

JSON Response
```

------------------------------------------------------------------------

# Common Mistakes

-   Forgetting to inherit from Base
-   Confusing ForeignKey with relationship()
-   Forgetting back_populates
-   Using String for very large content instead of Text
-   Storing image files inside the database instead of filenames

------------------------------------------------------------------------

# Best Practices

-   One model = one table
-   Keep business logic outside models
-   Use relationships wisely
-   Store file paths instead of files
-   Index frequently searched columns

------------------------------------------------------------------------

# Quick Revision

-   Models represent database tables.
-   ORM maps Python objects to database rows.
-   Base registers all models.
-   `Mapped` declares ORM attributes.
-   `mapped_column()` defines database columns.
-   Primary keys uniquely identify rows.
-   ForeignKey connects tables.
-   relationship() connects Python objects.
-   back_populates creates bidirectional navigation.
-   `@property` creates computed values without storing them.
