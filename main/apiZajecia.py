from fastapi import FastAPI, HTTPException, Depends
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from database import get_db
from models import Movie as MovieModel, Link as LinkModel, Rating as RatingModel, Tag as TagModel

app = FastAPI(title="Movies API (SQLite + SQLAlchemy)")


def movie_to_dict(m: MovieModel) -> Dict:
    return {
        "movieId": m.movieId,
        "title": m.title,
        "genres": m.genres.split("|") if m.genres else []
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


@app.get("/movies")
def movies(db: Session = Depends(get_db)) -> List[Dict]:
    """
    Return all movies from the SQLite DB (uses SQLAlchemy models).
    """
    movies = db.query(MovieModel).all()
    return [movie_to_dict(m) for m in movies]


@app.get("/links")
def links(db: Session = Depends(get_db)) -> List[Dict]:
    links = db.query(LinkModel).all()
    return [link_to_dict(l) for l in links]


@app.get("/ratings")
def ratings(db: Session = Depends(get_db)) -> List[Dict]:
    ratings = db.query(RatingModel).all()
    return [rating_to_dict(r) for r in ratings]


@app.get("/tags")
def tags(db: Session = Depends(get_db)) -> List[Dict]:
    tags = db.query(TagModel).all()
    return [tag_to_dict(t) for t in tags]