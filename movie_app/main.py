from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from movie_app.logger import logger
from movie_app.middleware import log_middleware
from starlette.middleware.base import BaseHTTPMiddleware
from movie_app.auth import authenticate_user, create_access_token, pwd_context
from movie_app.crud import user_crud_service
import movie_app.schemas as schemas
from movie_app.database import engine, Base, get_db
from movie_app.routers.users import user_router
from movie_app.routers.comments import comment_router
from movie_app.routers.movies import movie_router
from movie_app.routers.ratings import rating_router


Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(BaseHTTPMiddleware, dispatch=log_middleware)
logger.info('Starting API....')


@app.get('/')
async def index():
    return {'message': 'Welcome to Movie API'}

app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(
    comment_router, prefix="/movies/comments", tags=["Comments"])
app.include_router(movie_router, prefix="/movies", tags=["Movies"])
app.include_router(
    rating_router, prefix="/movies/ratings", tags=["Ratings"])


@app.post("/signup/", status_code=201, response_model=schemas.User)
async def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = user_crud_service.get_user_by_email_or_username(
        db, credentials=user.username)
    hashed_password = pwd_context.hash(user.password)
    if db_user:
        logger.warning("User already exists in database.....")
        raise HTTPException(
            status_code=400, detail="User already registered")
    return user_crud_service.create_user(db=db, user=user, hashed_password=hashed_password)


@app.post("/login", status_code=200)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logger.warning("Signup made with incorrect credentials...")
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
