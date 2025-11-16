from fastapi import FastAPI, HTTPException
from dataclasses import dataclass
from typing import List, Dict, Optional
import csv
from pathlib import Path
import os

app = FastAPI()


def get_resources_dir() -> Path:
    """
    Proste rozwiązywanie katalogu resources:
    1) jeśli ustawiona zmienna środowiskowa RESOURCES_DIR -> użyj jej
    2) w przeciwnym razie ./resources obok apiZajecia.py
    3) fallback: Windows path podany wcześniej
    """
    env = os.environ.get("RESOURCES_DIR")
    if env:
        p = Path(env)
        if p.is_dir():
            return p
        # jeśli wskazano plik, weź jego katalog
        return p.parent

    rel = Path(__file__).parent / "resources"
    if rel.exists():
        return rel

    return Path(r"C:\Users\Student\PycharmProjects\DobrePraktykiProgramowania\resources")


def csv_path(filename: str) -> Path:
    return get_resources_dir() / filename


@dataclass
class Movie:
    movieId: int
    title: str
    genres: List[str]


@dataclass
class Link:
    movieId: int
    imdbId: str
    tmdbId: Optional[int]


@dataclass
class Rating:
    userId: int
    movieId: int
    rating: float
    timestamp: Optional[int]


@dataclass
class Tag:
    userId: int
    movieId: int
    tag: str
    timestamp: Optional[int]


@app.get("/", include_in_schema=False)
async def root():
    return {"hello": "world"}


@app.get("/movies")
async def movies() -> List[Dict]:
    path = csv_path("movies.csv")
    if not path.exists():
        raise HTTPException(status_code=500, detail=f"movies.csv not found at {path}")

    out: List[Dict] = []
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                movie_id = int((row.get("movieId") or "").strip())
            except Exception:
                continue
            title = (row.get("title") or "").strip()
            genres_field = (row.get("genres") or "").strip()
            genres = [g for g in genres_field.split("|") if g] if genres_field else []
            movie = Movie(movieId=movie_id, title=title, genres=genres)
            out.append(movie.__dict__)
    return out


@app.get("/links")
async def links() -> List[Dict]:
    path = csv_path("links.csv")
    if not path.exists():
        raise HTTPException(status_code=500, detail=f"links.csv not found at {path}")

    out: List[Dict] = []
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                movie_id = int((row.get("movieId") or "").strip())
            except Exception:
                continue
            imdb_id = (row.get("imdbId") or "").strip()
            tmdb_raw = (row.get("tmdbId") or "").strip()
            try:
                tmdb_id = int(tmdb_raw) if tmdb_raw != "" else None
            except Exception:
                tmdb_id = None
            link = Link(movieId=movie_id, imdbId=imdb_id, tmdbId=tmdb_id)
            out.append(link.__dict__)
    return out


@app.get("/ratings")
async def ratings() -> List[Dict]:
    path = csv_path("ratings.csv")
    if not path.exists():
        raise HTTPException(status_code=500, detail=f"ratings.csv not found at {path}")

    out: List[Dict] = []
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                user_id = int((row.get("userId") or "").strip())
                movie_id = int((row.get("movieId") or "").strip())
                rating_val = float((row.get("rating") or "").strip())
            except Exception:
                continue
            ts_raw = (row.get("timestamp") or "").strip()
            try:
                ts = int(ts_raw) if ts_raw != "" else None
            except Exception:
                ts = None
            rating = Rating(userId=user_id, movieId=movie_id, rating=rating_val, timestamp=ts)
            out.append(rating.__dict__)
    return out


@app.get("/tags")
async def tags() -> List[Dict]:
    path = csv_path("tags.csv")
    if not path.exists():
        raise HTTPException(status_code=500, detail=f"tags.csv not found at {path}")

    out: List[Dict] = []
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                user_id = int((row.get("userId") or "").strip())
                movie_id = int((row.get("movieId") or "").strip())
            except Exception:
                continue
            tag_text = (row.get("tag") or "").strip()
            ts_raw = (row.get("timestamp") or "").strip()
            try:
                ts = int(ts_raw) if ts_raw != "" else None
            except Exception:
                ts = None
            tag = Tag(userId=user_id, movieId=movie_id, tag=tag_text, timestamp=ts)
            out.append(tag.__dict__)
    return out