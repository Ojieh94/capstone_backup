from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None


class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class MovieBase(BaseModel):
    title: str
    genre: str
    description: Optional[str] = None
    release_year: Optional[int] = None


class MovieCreate(MovieBase):
    pass


class MovieUpdate(BaseModel):
    title: Optional[str] = None
    genre: Optional[str] = None
    description: Optional[str] = None
    release_year: Optional[int] = None


class Movie(MovieBase):
    id: int
    user_id: int
    created_at: datetime
    owner: User

    class Config:
        from_attributes = True


class RatingBase(BaseModel):
    rating_value: int = Field(ge=1, le=10)


class RatingCreate(RatingBase):
    movie_id: int


class RatingUpdate(RatingBase):
    pass


class Rating(RatingBase):
    id: int
    user_id: int
    movie_id: int
    created_at: datetime
    user: User

    class Config:
        from_attributes = True


class CommentBase(BaseModel):
    comment: str


class CommentCreate(CommentBase):
    pass


class CommentUpdate(BaseModel):
    comment: Optional[str] = None


class Comment(CommentBase):
    id: int
    user_id: int
    movie_id: int
    created_at: datetime
    parent_id: Optional[int]
    author: User

    class Config:
        from_attributes = True


class AuthorResponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True


class CommentResponse(BaseModel):
    id: int
    user_id: int
    movie_id: int
    comment: str
    parent_id: Optional[int]
    created_at: datetime
    author: AuthorResponse  # Include author details
    replies: int

    class Config:
        from_attributes = True


class CommentOut(BaseModel):
    Comment: Comment
    replies: int
