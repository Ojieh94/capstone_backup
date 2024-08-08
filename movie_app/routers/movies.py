from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from movie_app.logger import logger
from movie_app.auth import get_current_user
from sqlalchemy.orm import Session
import movie_app.schemas as schemas
from movie_app.crud import movie_crud_service
from movie_app.database import get_db

movie_router = APIRouter()


@movie_router.get("/", status_code=200, response_model=List[schemas.Movie])
async def get_movies(db: Session = Depends(get_db), offset: int = 0, limit: int = 10):
    movies = movie_crud_service.get_movies(
        db,
        offset=offset,
        limit=limit
    )
    return movies


@movie_router.get("/{movie_id}", status_code=200, response_model=schemas.Movie)
async def get_movie_by_id(movie_id: str, db: Session = Depends(get_db)):
    movie = movie_crud_service.get_movie_by_id(db, movie_id)
    if not movie:
        logger.warning("Getting movie with wrong id....")
        raise HTTPException(detail="Movie not found",
                            status_code=status.HTTP_404_NOT_FOUND)
    return movie


@movie_router.get("/genre/{genre}", status_code=200, response_model=List[schemas.Movie])
async def get_movie_by_genre(genre: str, db: Session = Depends(get_db)):
    movie = movie_crud_service.get_movie_by_genre(db, genre)
    if not movie:
        raise HTTPException(detail="Movie not found",
                            status_code=status.HTTP_404_NOT_FOUND)
    return movie


@movie_router.get("/title/{movie_title}", status_code=200, response_model=List[schemas.Movie])
async def get_movie_by_title(movie_title: str, db: Session = Depends(get_db)):
    movie = movie_crud_service.get_movie_by_title(db, movie_title)
    if not movie:
        logger.info("Getting movie with wrong title...")
        raise HTTPException(detail="Movie not found",
                            status_code=status.HTTP_404_NOT_FOUND)
    return movie


@movie_router.post('/', status_code=201, response_model=schemas.Movie)
async def list_movie(payload: schemas.MovieCreate, current_user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    movie = movie_crud_service.create_movie(
        db,
        payload,
        user_id=current_user.id
    )
    return movie


@movie_router.put('/{movie_id}', status_code=200, response_model=schemas.Movie)
async def update_movie(movie_id: int, payload: schemas.MovieUpdate, current_user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_movie = movie_crud_service.get_movie_by_id(db, movie_id=movie_id)
    if not db_movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    if db_movie.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
    movie = movie_crud_service.update_movie(
        db, movie_id=movie_id, movie_payload=payload)
    return movie


@movie_router.delete("/{movie_id}", status_code=200)
async def delete_movie(movie_id: int, current_user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    movie = movie_crud_service.get_movie_by_id(db, movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    if movie.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")

    movie_crud_service.delete_movie(db, movie_id)

    return {"message": "Successful"}
