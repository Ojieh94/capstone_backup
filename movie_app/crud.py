from sqlalchemy import func, select
from sqlalchemy.orm import Session
import movie_app.models as models
import movie_app.schemas as schemas

# User CRUD Operations


class UserCRUDService:

    @staticmethod
    def create_user(db: Session, user: schemas.UserCreate, hashed_password: str):
        db_user = models.User(
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            hashed_password=hashed_password
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def get_users(db: Session, offset: int = 0, limit: int = 10):
        return db.query(models.User).offset(offset).limit(limit).all()

    @staticmethod
    def get_user_by_id(db: Session, user_id: int):
        return db.query(models.User).filter(models.User.id == user_id).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str):
        return db.query(models.User).filter(models.User.username == username).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str):
        return db.query(models.User).filter(models.User.email == email).first()

    @staticmethod
    def get_user_by_email_or_username(db: Session, credentials: str):
        user = user_crud_service.get_user_by_email(db, credentials)
        if not user:
            user = user_crud_service.get_user_by_username(db, credentials)
        if not user:
            return None
        return user

    @staticmethod
    def update_user(db: Session, user_id: int, user_payload: schemas.UserUpdate):
        user = user_crud_service.get_user_by_id(db, user_id)
        if not user:
            return None

        user_payload_dict = user_payload.model_dump(exclude_unset=True)

        for key, value in user_payload_dict.items():
            setattr(user, key, value)

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def delete_user(db: Session, user_id: int):
        user = user_crud_service.get_user_by_id(db, user_id)

        db.delete(user)
        db.commit()

        return None


# Movies CRUD Operations

class MovieCRUDService:

    @staticmethod
    def create_movie(db: Session, movie: schemas.MovieCreate, user_id: int):
        db_movie = models.Movie(
            **movie.model_dump(),
            user_id=user_id
        )
        db.add(db_movie)
        db.commit()
        db.refresh(db_movie)
        return db_movie

    @staticmethod
    def get_movies(db: Session, offset: int = 0, limit: int = 10):
        return db.query(models.Movie).offset(offset).limit(limit).all()

    @staticmethod
    def get_movie_by_id(db: Session, movie_id: int):
        return db.query(models.Movie).filter(models.Movie.id == movie_id).first()

    @staticmethod
    def get_movie_by_title(db: Session, title: str):
        return db.query(models.Movie).filter(models.Movie.title == title).all()

    @staticmethod
    def get_movie_by_genre(db: Session, genre: str):
        return db.query(models.Movie).filter(models.Movie.genre == genre).all()

    @staticmethod
    def update_movie(db: Session, movie_payload: schemas.MovieUpdate, movie_id: int):
        movie = movie_crud_service.get_movie_by_id(db, movie_id)
        if not movie:
            return None

        movie_payload_dict = movie_payload.model_dump(exclude_unset=True)

        for k, v in movie_payload_dict.items():
            setattr(movie, k, v)

        db.add(movie)
        db.commit()
        db.refresh(movie)
        return movie

    @staticmethod
    def delete_movie(db: Session, movie_id: int = None):
        movie = movie_crud_service.get_movie_by_id(db, movie_id)

        db.delete(movie)
        db.commit()

        return None

# Ratings CRUD Operations

class RatingCRUDService:

    @staticmethod
    def rate_movie_by_id(db: Session, rating: schemas.RatingCreate, user_id: int):
        db_rating = models.Rating(
            **rating.model_dump(),
            user_id=user_id
        )

        db.add(db_rating)
        db.commit()
        db.refresh(db_rating)
        return db_rating

    @staticmethod
    def get_ratings(db: Session, offset: int = 0, limit: int = 10):
        return db.query(models.Rating).offset(offset).limit(limit).all()

    @staticmethod
    def get_rating(db: Session, user_id: int, movie_id: int):
        return db.query(models.Rating).filter(models.Rating.user_id == user_id, models.Rating.movie_id == movie_id).first()

    @staticmethod
    def get_rating_by_id(db: Session, rating_id: int):
        return db.query(models.Rating).filter(models.Rating.id == rating_id).first()

    @staticmethod
    def get_ratings_by_movie_id(db: Session, movie_id: int, offset: int = 0, limit: int = 10):
        return db.query(models.Rating).filter(models.Rating.movie_id == movie_id).offset(offset).limit(limit).all()

    @staticmethod
    def update_rating(db: Session, rating_payload: schemas.RatingUpdate, rating_id: int):
        rating = rating_crud_service.get_rating_by_id(db, rating_id)
        if not rating:
            return None

        rating_payload_dict = rating_payload.model_dump(exclude_unset=True)

        for k, v in rating_payload_dict.items():
            setattr(rating, k, v)

        db.add(rating)
        db.commit()
        db.refresh(rating)
        return rating

    @staticmethod
    def delete_rating(db: Session, rating_id: int = None):
        rating = rating_crud_service.get_rating_by_id(db, rating_id)

        db.delete(rating)
        db.commit()

        return None

# Comments CRUD Operations

class CommentCRUDService:

    @staticmethod
    def create_comment(db: Session, comment: schemas.CommentCreate, movie_id: int, user_id: int):
        db_comment = models.Comment(
            **comment.model_dump(),
            user_id=user_id,
            movie_id=movie_id
        )

        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)
        return db_comment

    @staticmethod
    def get_comments(db: Session, offset: int = 0, limit: int = 10):
        # Join comments with the reply counts

        # Subquery to count replies
        subquery = (
            db.query(
                models.Comment.parent_id,
                func.count(models.Comment.id).label("reply_count")
            )
            .group_by(models.Comment.parent_id)
            .subquery()
        )

        # Main query to get comments with reply count and author details
        comments_with_no_of_replies = (
            db.query(
                models.Comment,
                models.User,  # Join the User table [so as to get the author]
                func.coalesce(subquery.c.reply_count, 0).label("replies")
            )

            .join(models.User, models.Comment.user_id == models.User.id)
            .outerjoin(subquery, models.Comment.id == subquery.c.parent_id)
            .offset(offset)
            .limit(limit)
            .all()
        )

        # The above query ensures that the comments are returned with no. of replies of each comment
        return comments_with_no_of_replies

    @staticmethod
    def get_replies_to_comment(db: Session, parent_id: int, offset: int = 0, limit: int = 10):
        return db.query(models.Comment).filter(models.Comment.parent_id == parent_id).offset(offset).limit(limit).all()

    @staticmethod
    def get_comments_by_movie(db: Session, movie_id: int, offset: int = 0, limit: int = 10):
        return db.query(models.Comment).filter(models.Comment.movie_id == movie_id).offset(offset).limit(limit).all()

    @staticmethod
    def get_comment_by_id(db: Session, comment_id: int):
        # Subquery to count replies
        reply_count_subquery = (
            select(
                models.Comment.parent_id,
                func.count(models.Comment.id).label("reply_count")
            )
            .group_by(models.Comment.parent_id)
            .subquery()
        )

        # Query to get a specific comment with reply count
        query = (
            select(
                models.Comment,
                func.coalesce(reply_count_subquery.c.reply_count,
                              0).label("replies")
            )
            .outerjoin(reply_count_subquery, models.Comment.id == reply_count_subquery.c.parent_id)
            .where(models.Comment.id == comment_id)
        )
        comment_with_no_of_replies = db.execute(query).fetchone()

        # The above query ensures that comment is returned with the no. of replies
        return comment_with_no_of_replies

    @staticmethod
    def get_comment_by_user(db: Session, user_id: int, offset: int = 0, limit: int = 10):
        return db.query(models.Comment).filter(models.Comment.user_id == user_id).offset(offset).limit(limit).all()

    @staticmethod
    def get_a_comment(db: Session, comment_id: int):
        return db.query(models.Comment).filter(models.Comment.id == comment_id).first()

    @staticmethod
    def reply_comment(comment_id: int, db: Session, comment: schemas.CommentBase, user_id: int):
        parent_comment = comment_crud_service.get_a_comment(db, comment_id)
        if not parent_comment:
            return None
        movie_id = parent_comment.movie_id
        parent_id = parent_comment.id

        # Create a reply using the comment model
        new_comment = models.Comment(
            **comment.model_dump(), movie_id=movie_id, parent_id=parent_id, user_id=user_id)

        db.add(new_comment)
        db.commit()
        db.refresh(new_comment)
        return new_comment

    @staticmethod
    def update_comment(db: Session, comment_payload: schemas.CommentUpdate, comment_id: int):
        comment = comment_crud_service.get_a_comment(db, comment_id)
        if not comment:
            return None
        comment_payload_dict = comment_payload.model_dump(exclude_unset=True)

        for k, v in comment_payload_dict.items():
            setattr(comment, k, v)

        db.add(comment)
        db.commit()
        db.refresh(comment)
        return comment

    @staticmethod
    def delete_comment(db: Session, comment_id: int):
        comment = comment_crud_service.get_a_comment(db, comment_id)

        db.delete(comment)
        db.commit()

        return None


user_crud_service = UserCRUDService()
movie_crud_service = MovieCRUDService()
rating_crud_service = RatingCRUDService()
comment_crud_service = CommentCRUDService()
