from fastapi import FastAPI, HTTPException, Depends
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from main.database import get_db
from main.models import Movie as MovieModel, Link as LinkModel, Rating as RatingModel, Tag as TagModel, User as UserModel
from main import schemas
import bcrypt
from main.auth import hash_password, verify_password, create_access_token, get_current_user_from_token, role_required

app = FastAPI(title="Movies API (SQLite + SQLAlchemy)")


def movie_to_dict(m: MovieModel) -> Dict:
    return {
        "movieId": m.movieId,
        "title": m.title,
        "genres": m.genres
    }


def link_to_dict(l: LinkModel) -> Dict:
    return {
        "movieId": l.movieId,
        "imdbId": l.imdbId,
        "tmdbId": l.tmdbId
    }


def rating_to_dict(r: RatingModel) -> Dict:
    return {
        "userId": r.userId,
        "movieId": r.movieId,
        "rating": r.rating,
        "timestamp": r.timestamp
    }


def tag_to_dict(t: TagModel) -> Dict:
    return {
        "userId": t.userId,
        "movieId": t.movieId,
        "tag": t.tag,
        "timestamp": t.timestamp
    }


@app.get("/", include_in_schema=False)
async def root():
    return {"hello": "world"}

# ENDPOINT: READ (LIST)
@app.get("/movies", response_model=List[schemas.Movie])
def get_all_movies(db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user_from_token)):
    """
    Zwraca listę wszystkich filmów.
    """
    return db.query(MovieModel).all()


# 1. ZASÓB: MOVIES

# a. POST - TWORZENIE
@app.post("/movies", response_model=schemas.Movie, status_code=201)
def create_movie(movie_data: schemas.MovieCreate, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user_from_token)):
    # Sprawdzenie, czy movieId już istnieje
    existing_movie = db.query(MovieModel).filter(MovieModel.movieId == movie_data.movieId).first()
    if existing_movie:
        raise HTTPException(status_code=409, detail=f"Movie with movieId {movie_data.movieId} already exists.")

    db_movie = MovieModel(**movie_data.model_dump())

    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie


# b. READ (ITEM) - POBIERANIE PO ID
@app.get("/movies/{movie_id}", response_model=schemas.Movie)
def get_movie_by_id(movie_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user_from_token)):
    movie = db.query(MovieModel).filter(MovieModel.movieId == movie_id).first()
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie


# c. PUT - AKTUALIZACJA
@app.put("/movies/{movie_id}", response_model=schemas.Movie)
def update_movie(movie_id: int, movie_data: schemas.MovieCreate, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user_from_token)):
    db_movie = db.query(MovieModel).filter(MovieModel.movieId == movie_id).first()
    if db_movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")

    # Aktualizacja pól
    for key, value in movie_data.model_dump(exclude_unset=True).items():
        setattr(db_movie, key, value)

    db.commit()
    db.refresh(db_movie)
    return db_movie


# d. DELETE - USUWANIE
@app.delete("/movies/{movie_id}", status_code=204)
def delete_movie(movie_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user_from_token)):
    db_movie = db.query(MovieModel).filter(MovieModel.movieId == movie_id).first()
    if db_movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")

    db.delete(db_movie)
    db.commit()
    return

@app.get("/links")
def links(db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user_from_token)) -> List[Dict]:
    links = db.query(LinkModel).all()
    return [link_to_dict(l) for l in links]


# 2. ZASÓB: LINKS

# a. POST - TWORZENIE
@app.post("/links", response_model=schemas.Link, status_code=201)
def create_link(link_data: schemas.LinkCreate, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user_from_token)):
    # Sprawdzenie, czy film istnieje (integralność klucza obcego)
    if not db.query(MovieModel).filter(MovieModel.movieId == link_data.movieId).first():
        raise HTTPException(status_code=400, detail="Invalid movieId: Movie does not exist.")

    db_link = LinkModel(**link_data.model_dump())
    db.add(db_link)
    db.commit()
    db.refresh(db_link)
    return db_link


# b. READ (ITEM) - POBIERANIE PO ID
@app.get("/links/{link_id}", response_model=schemas.Link)
def get_link_by_id(link_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user_from_token)):
    link = db.query(LinkModel).filter(LinkModel.id == link_id).first()
    if link is None:
        raise HTTPException(status_code=404, detail="Link not found")
    return link


# c. PUT - AKTUALIZACJA
@app.put("/links/{link_id}", response_model=schemas.Link)
def update_link(link_id: int, link_data: schemas.LinkCreate, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user_from_token)):
    db_link = db.query(LinkModel).filter(LinkModel.id == link_id).first()
    if db_link is None:
        raise HTTPException(status_code=404, detail="Link not found")

    # Wymagane sprawdzenie klucza obcego, jeśli zmieniamy movieId
    if link_data.movieId != db_link.movieId and not db.query(MovieModel).filter(
            MovieModel.movieId == link_data.movieId).first():
        raise HTTPException(status_code=400, detail="Invalid movieId: Movie does not exist.")

    for key, value in link_data.model_dump(exclude_unset=True).items():
        setattr(db_link, key, value)

    db.commit()
    db.refresh(db_link)
    return db_link


# d. DELETE - USUWANIE
@app.delete("/links/{link_id}", status_code=204)
def delete_link(link_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user_from_token)):
    db_link = db.query(LinkModel).filter(LinkModel.id == link_id).first()
    if db_link is None:
        raise HTTPException(status_code=404, detail="Link not found")

    db.delete(db_link)
    db.commit()
    return


# 3. ZASÓB: RATINGS

# a. POST - TWORZENIE
@app.post("/ratings", response_model=schemas.Rating, status_code=201)
def create_rating(rating_data: schemas.RatingCreate, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user_from_token)):
    if not db.query(MovieModel).filter(MovieModel.movieId == rating_data.movieId).first():
        raise HTTPException(status_code=400, detail="Invalid movieId: Movie does not exist.")

    db_rating = RatingModel(**rating_data.model_dump())
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)
    return db_rating


# b. READ (ITEM) - POBIERANIE PO ID
@app.get("/ratings/{rating_id}", response_model=schemas.Rating)
def get_rating_by_id(rating_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user_from_token)):
    rating = db.query(RatingModel).filter(RatingModel.id == rating_id).first()
    if rating is None:
        raise HTTPException(status_code=404, detail="Rating not found")
    return rating


# c. PUT - AKTUALIZACJA
@app.put("/ratings/{rating_id}", response_model=schemas.Rating)
def update_rating(rating_id: int, rating_data: schemas.RatingCreate, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user_from_token)):
    db_rating = db.query(RatingModel).filter(RatingModel.id == rating_id).first()
    if db_rating is None:
        raise HTTPException(status_code=404, detail="Rating not found")

    if rating_data.movieId != db_rating.movieId and not db.query(MovieModel).filter(
            MovieModel.movieId == rating_data.movieId).first():
        raise HTTPException(status_code=400, detail="Invalid movieId: Movie does not exist.")

    for key, value in rating_data.model_dump(exclude_unset=True).items():
        setattr(db_rating, key, value)

    db.commit()
    db.refresh(db_rating)
    return db_rating


# d. DELETE - USUWANIE
@app.delete("/ratings/{rating_id}", status_code=204)
def delete_rating(rating_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user_from_token)):
    db_rating = db.query(RatingModel).filter(RatingModel.id == rating_id).first()
    if db_rating is None:
        raise HTTPException(status_code=404, detail="Rating not found")

    db.delete(db_rating)
    db.commit()
    return

@app.get("/ratings")
def ratings(db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user_from_token)) -> List[Dict]:
    ratings = db.query(RatingModel).all()
    return [rating_to_dict(r) for r in ratings]


# 4. ZASÓB: TAGS

# a. POST - TWORZENIE
@app.post("/tags", response_model=schemas.Tag, status_code=201)
def create_tag(tag_data: schemas.TagCreate, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user_from_token)):
    if not db.query(MovieModel).filter(MovieModel.movieId == tag_data.movieId).first():
        raise HTTPException(status_code=400, detail="Invalid movieId: Movie does not exist.")

    db_tag = TagModel(**tag_data.model_dump())
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


# b. READ (ITEM) - POBIERANIE PO ID
@app.get("/tags/{tag_id}", response_model=schemas.Tag)
def get_tag_by_id(tag_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user_from_token)):
    tag = db.query(TagModel).filter(TagModel.id == tag_id).first()
    if tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


# c. PUT - AKTUALIZACJA
@app.put("/tags/{tag_id}", response_model=schemas.Tag)
def update_tag(tag_id: int, tag_data: schemas.TagCreate, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user_from_token)):
    db_tag = db.query(TagModel).filter(TagModel.id == tag_id).first()
    if db_tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")

    if tag_data.movieId != db_tag.movieId and not db.query(MovieModel).filter(
            MovieModel.movieId == tag_data.movieId).first():
        raise HTTPException(status_code=400, detail="Invalid movieId: Movie does not exist.")

    for key, value in tag_data.model_dump(exclude_unset=True).items():
        setattr(db_tag, key, value)

    db.commit()
    db.refresh(db_tag)
    return db_tag


# d. DELETE - USUWANIE
@app.delete("/tags/{tag_id}", status_code=204)
def delete_tag(tag_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user_from_token)):
    db_tag = db.query(TagModel).filter(TagModel.id == tag_id).first()
    if db_tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")

    db.delete(db_tag)
    db.commit()
    return

@app.get("/tags")
def tags(db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user_from_token)) -> List[Dict]:
    tags = db.query(TagModel).all()
    return [tag_to_dict(t) for t in tags]


# 5. ZASÓB: USERS (REJESTRACJA I ZARZĄDZANIE)

@app.post("/users", response_model=schemas.User, status_code=201,
          dependencies=[Depends(role_required(["ROLE_ADMIN"]))])
def create_user(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Dodaje nowego użytkownika do bazy danych (wymaga ROLE_ADMIN).
    """
    existing_user = db.query(UserModel).filter(UserModel.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="User already exists")

    hashed_pw = hash_password(user_data.password)

    roles_str = "|".join(user_data.roles)

    db_user = UserModel(
        username=user_data.username,
        hashed_password=hashed_pw,
        roles=roles_str
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    db_user.roles = db_user.roles.split("|")

    return db_user


@app.get("/user_details")
def user_details(current_user: UserModel = Depends(get_current_user_from_token)):
    """
    Zwraca dane użytkownika z payloadu JWT tokena (username, roles, exp, itd.).
    """
    return current_user.jwt_payload


# 6. UWIERZYTELNIANIE

@app.post("/login", response_model=schemas.Token)
def login(data: schemas.LoginData, db: Session = Depends(get_db)):
    """
    Uwierzytelnia użytkownika po loginie i haśle, zwraca token JWT.
    """
    user = db.query(UserModel).filter(UserModel.username == data.username).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user_roles = user.roles.split("|")

    token_data = {
        "username": user.username,
        "roles": user_roles
    }

    access_token = create_access_token(data=token_data)

    return {"access_token": access_token, "token_type": "bearer"}