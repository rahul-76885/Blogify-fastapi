# Chapter 04 -- Schemas (`schemas.py`)

**Source File:** `blog/schemas.py`

------------------------------------------------------------------------

# Purpose

`schemas.py` defines the data format used by your API.

It controls:

-   What data the client can send.
-   What data the client receives.
-   Validation of incoming data.
-   Serialization of outgoing data.

Think of it as the **communication layer** between your API and the
outside world.

------------------------------------------------------------------------

# File Overview

``` text
schemas.py
│
├── User Schemas
│   ├── UserBase
│   ├── UserCreate
│   ├── UserUpdate
│   └── UserResponse
│
├── Post Schemas
│   ├── PostBase
│   ├── PostCreate
│   ├── PostUpdate
│   └── PostResponse
│
└── Pydantic Configuration
```

------------------------------------------------------------------------

# Why do Schemas exist?

Imagine the database contains:

``` text
id
username
email
password_hash
created_at
```

Should the client receive everything?

No.

Schemas decide exactly what enters and leaves your API.

``` text
Client

↓

Schema

↓

Route

↓

Model

↓

Database
```

------------------------------------------------------------------------

# Models vs Schemas

  Models               Schemas
  -------------------- ----------------
  Database structure   API structure
  SQLAlchemy           Pydantic
  Tables               JSON
  Stores data          Validates data

Use **Models** for the database.

Use **Schemas** for API requests and responses.

------------------------------------------------------------------------

# What is Pydantic?

Pydantic is FastAPI's validation library.

It converts JSON into Python objects and validates the data before your
route executes.

``` text
JSON

↓

Pydantic

↓

Validated Python Object

↓

Route
```

------------------------------------------------------------------------

# BaseModel

Every schema inherits from:

``` python
class UserBase(BaseModel):
```

`BaseModel` provides:

-   Validation
-   Serialization
-   Type conversion
-   Helpful error messages

------------------------------------------------------------------------

# Field()

Example:

``` python
title: str = Field(
    min_length=1,
    max_length=100
)
```

## Why use Field()?

Python only knows the type.

`Field()` defines validation rules.

Examples:

-   Minimum length
-   Maximum length
-   Default value
-   Description

------------------------------------------------------------------------

# EmailStr

``` python
email: EmailStr
```

Instead of accepting any string, `EmailStr` checks that the value is a
valid email.

Valid:

    rahul@gmail.com

Invalid:

    rahulgmail.com

------------------------------------------------------------------------

# ConfigDict(from_attributes=True)

``` python
model_config = ConfigDict(
    from_attributes=True
)
```

## Why do we need it?

SQLAlchemy returns objects.

Pydantic normally expects dictionaries.

This option tells Pydantic:

> Read values directly from object attributes.

``` text
SQLAlchemy Model

↓

Pydantic

↓

JSON
```

------------------------------------------------------------------------

# Schema Inheritance

Instead of repeating fields:

``` python
username
email
```

in every class,

you create:

``` python
UserBase
```

Then inherit.

``` text
UserBase
   │
   ├── UserCreate
   └── UserResponse
```

Benefits:

-   Less duplication
-   Easier maintenance
-   Cleaner code

------------------------------------------------------------------------

# Create, Update and Response Schemas

## UserCreate

Used when creating a new user.

``` text
Client

↓

POST /users

↓

UserCreate
```

------------------------------------------------------------------------

## UserUpdate

Fields are optional.

``` python
username: str | None
```

Allows partial updates.

------------------------------------------------------------------------

## UserResponse

Controls what the API returns.

Never expose sensitive fields such as:

-   Password
-   Password hash
-   Internal tokens

------------------------------------------------------------------------

# Nested Schemas

Example:

``` python
author: UserResponse
```

Instead of returning:

``` json
{
  "user_id": 1
}
```

FastAPI can return:

``` json
{
  "author": {
    "id": 1,
    "username": "Rahul"
  }
}
```

This creates richer API responses.

------------------------------------------------------------------------

# Validation Flow

``` text
Client

↓

JSON

↓

Pydantic Schema

↓

Validation

↓

Route

↓

SQLAlchemy Model

↓

Database
```

Response:

``` text
Database

↓

SQLAlchemy Model

↓

Pydantic Schema

↓

JSON

↓

Client
```

------------------------------------------------------------------------

# Common Mistakes

-   Returning ORM models directly.
-   Forgetting `from_attributes=True`.
-   Using one schema for Create, Update and Response.
-   Exposing sensitive fields.
-   Putting business logic inside schemas.

------------------------------------------------------------------------

# Best Practices

-   Separate Create, Update and Response schemas.
-   Reuse fields through inheritance.
-   Keep validation inside schemas.
-   Keep database logic inside models.
-   Use descriptive validation rules.

------------------------------------------------------------------------

# Quick Revision

-   Schemas define the API contract.
-   Models define the database.
-   Pydantic validates incoming data.
-   BaseModel is the parent of all schemas.
-   Field() adds validation.
-   EmailStr validates email addresses.
-   from_attributes=True converts SQLAlchemy objects.
-   Separate schemas for Create, Update and Response.
-   Nested schemas improve API responses.

------------------------------------------------------------------------

# Related Chapters

-   Database Layer
-   Models
-   Routers
-   Dependency Injection
-   Validation
