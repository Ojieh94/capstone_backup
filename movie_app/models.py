from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship

from movie_app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True,
                autoincrement=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, nullable=False, index=True)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False,
                        server_default=text('CURRENT_TIMESTAMP'))

    movies = relationship("Movie", back_populates="owner")
    ratings = relationship('Rating', back_populates='user')
    comments = relationship('Comment', back_populates='author')


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True,
                autoincrement=True, nullable=False)
    title = Column(String, nullable=False, index=True)
    genre = Column(String, nullable=False)
    description = Column(String)
    release_year = Column(Integer)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), nullable=False,
                        server_default=text('CURRENT_TIMESTAMP'))

    owner = relationship("User", back_populates="movies")
    ratings = relationship("Rating", back_populates="movie")
    comments = relationship("Comment", back_populates="movie")


class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True,
                autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    movie_id = Column(Integer, ForeignKey("movies.id"))
    rating_value = Column(Integer)
    created_at = Column(DateTime(timezone=True), nullable=False,
                        server_default=text('CURRENT_TIMESTAMP'))

    user = relationship('User', back_populates='ratings')
    movie = relationship('Movie', back_populates='ratings')


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, nullable=False,
                autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    movie_id = Column(Integer, ForeignKey("movies.id"))
    comment = Column(String)
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False,
                        server_default=text('CURRENT_TIMESTAMP'))

    author = relationship('User', back_populates='comments')
    movie = relationship('Movie', back_populates='comments')
    replies = relationship('Comment', backref='parent', remote_side=[id])
