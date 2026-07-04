from datetime import datetime

# BaseModel = parent class for all Pydantic schemas
# ConfigDict(from_attributes=True) = allows converting SQLAlchemy objects -> Pydantic objects
# EmailStr = validates email format automatically
# Field() = add validation rules (min_length, max_length, etc.)
from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


# =============================================================================
# USER SCHEMAS
# =============================================================================

class UserBase(BaseModel):
    # Common fields shared by multiple user schemas

    # Must be between 1 and 50 characters
    username: str = Field(min_length=1, max_length=50)

    # Must be a valid email address
    email: EmailStr


# Used when creating/registering a user
# Inherits username + email from UserBase
class UserCreate(UserBase):
    pass


# Used when RETURNING user data through API
# Controls what fields the client can see
class UserResponse(UserBase):

    # Allows:
    # SQLAlchemy User object -> UserResponse schema
    model_config = ConfigDict(from_attributes=True)

    # Returned to client
    id: int

    # Stored filename only (e.g. rahul.jpg)
    image_file: str | None

    # Computed property from model (@property)
    # Example:
    # /media/profile_pics/rahul.jpg
    image_path: str

class UserUpdate(BaseModel):
    username:str | None=Field(default=None,min_length=1,max_length=20)
    email:EmailStr|None=Field(default=None,min_length=1,max_length=50)
    image_file: str | None = Field(default=None, min_length=1, max_length=100)

    @model_validator(mode="before")
    @classmethod
    def empty_strings_become_none(cls, data):
        if isinstance(data, dict):
            for key, value in list(data.items()):
                if isinstance(value, str) and not value.strip():
                    data[key] = None
        return data

# ============================================================================= 
# POST SCHEMAS
# =============================================================================

class PostBase(BaseModel):
    # Common fields shared by create/response schemas

    title: str = Field(
        min_length=1,
        max_length=100
    )

    # No max length because blog posts can be long
    content: str = Field(min_length=1)


# Used when creating a post
class PostCreate(PostBase):

    # TEMPORARY
    # Later this usually comes from logged-in user
    # instead of client sending it manually
    user_id: int


class PostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    content: str | None = Field(default=None, min_length=1)



# Used when RETURNING a post from API
class PostResponse(PostBase):

    # Convert SQLAlchemy Post object -> Pydantic schema
    model_config = ConfigDict(from_attributes=True)

    id: int

    # Foreign key stored in database
    user_id: int

    # Automatically generated timestamp
    date_posted: datetime

    # Nested schema
    # Instead of returning only user_id,
    # FastAPI can return complete author information
    #
    # Example:
    # {
    #   "id":1,
    #   "title":"FastAPI",
    #   "author":{
    #       "id":1,
    #       "username":"Rahul"
    #   }
    # }

    author: UserResponse


# =============================================================================
# SCHEMAS.PY REVISION NOTES
# =============================================================================
#
# Q: What is schemas.py?
#
# A:
# Schemas define API input/output formats.
#
# Models.py
#     -> Database structure
#
# Schemas.py
#     -> API request/response structure
#
# Models store data.
# Schemas control what data can enter or leave the API.
#
# =============================================================================
#
# Q: Why do we need schemas if we already have models?
#
# A:
# Models describe the database.
#
# Schemas describe:
#     1. What client can SEND
#     2. What client can RECEIVE
#
# Example:
#
# Database Model:
#     id
#     username
#     email
#     password_hash
#
# API Response:
#     id
#     username
#     email
#
# password_hash stays hidden.
#
# =============================================================================
#
# Q: Why do we need UserCreate?
#
# A:
# APIs are not only used to return data.
#
# APIs also:
#     Create
#     Read
#     Update
#     Delete
#
# Example:
#
# Frontend Registration Form
#         ↓
# POST /register
#         ↓
# JSON Request
#         ↓
# UserCreate Schema
#         ↓
# Route
#         ↓
# Database
#
# UserCreate validates incoming data before storing it.
#
# UserCreate = data client can SEND.
#
# =============================================================================
#
# Q: What happens when frontend sends JSON?
#
# A:
#
# Frontend
#      ↓
# JSON Request
#      ↓
# Pydantic Schema
#      ↓
# Validation
#      ↓
# Python Object
#      ↓
# Route Function
#      ↓
# SQLAlchemy Model
#      ↓
# Database
#
# Example:
#
# def create_user(user: UserCreate):
#
# FastAPI automatically converts JSON into a UserCreate object.
#
# user.username
# user.email
#
# can then be accessed inside the route.
#
# =============================================================================
#
# Q: Why validate in both Pydantic and Database?
#
# A:
#
# Pydantic:
#     validates API requests
#
# Database:
#     protects stored data forever
#
# Example:
#
# Schema:
#     email: EmailStr
#
# Model:
#     unique=True
#
# Pydantic checks:
#     "Is email valid?"
#
# Database checks:
#     "Can duplicates exist?"
#
# Never trust only one layer.
#
# =============================================================================
#
# Q: What does Field() do?
#
# A:
# Adds validation rules.
#
# Example:
#
# title: str = Field(
#     min_length=1,
#     max_length=100
# )
#
# Prevents invalid data before reaching the route.
#
# Similar idea:
#
# Pydantic:
#     Field()
#
# SQLAlchemy:
#     mapped_column()
#
# =============================================================================
#
# Q: What does EmailStr do?
#
# A:
# Automatically validates email format.
#
# Valid:
#     rahul@gmail.com
#
# Invalid:
#     rahulgmail.com
#
# =============================================================================
#
# Q: What does ConfigDict(from_attributes=True) do?
#
# A:
# Allows Pydantic to read SQLAlchemy objects directly.
#
# Without it:
#
#     Pydantic expects dictionaries
#
# With it:
#
#     post.title
#     post.content
#     user.username
#
# can be read directly.
#
# SQLAlchemy Object
#         ↓
# Pydantic Schema
#         ↓
# JSON Response
#
# =============================================================================
#
# Q: What is a Nested Schema?
#
# Example:
#
# author: UserResponse
#
# A:
# Lets related objects be returned automatically.
#
# Instead of:
#
# {
#     "user_id": 1
# }
#
# We can return:
#
# {
#     "author": {
#         "id": 1,
#         "username": "Rahul"
#     }
# }
#
# relationship() gives User object.
# UserResponse converts it into JSON.
#
# =============================================================================
#
# Q: UserCreate vs UserResponse
#
# UserCreate:
#     Incoming data
#
# UserResponse:
#     Outgoing data
#
# Example:
#
# UserCreate:
#     username
#     email
#     password
#
# UserResponse:
#     id
#     username
#     email
#
# Password should never be returned.
#
# =============================================================================
#
# MEMORY MAP
#
# Frontend
#      ↓
# JSON
#      ↓
# Schema (Validation)
#      ↓
# Route
#      ↓
# Model
#      ↓
# Database
#
# Database
#      ↓
# Model
#      ↓
# Schema (Response)
#      ↓
# JSON
#      ↓
# Frontend
#
# =============================================================================