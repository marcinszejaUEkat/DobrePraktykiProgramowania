from pathlib import Path
import csv
from typing import List
from sqlalchemy import delete
from database import SessionLocal, engine
from models import Base, Movie, Link, Rating, Tag

RES_DIR = Path(__file__).resolve().parent.parent / "resources"

def create_tables():
    """Upewnij się, że tabele istnieją."""
    Base.metadata.create_all(bind=engine)
    print("Tables created / ensured.")

def clear_tables(session):
    """Usuń istniejące dane (zapobiega duplikatom przy wielokrotnym uruchomieniu)."""
    # usuwaj w kolejności zależności (najpierw zależne, potem główne)
    session.execute(delete(Link))
    session.execute(delete(Rating))
    session.execute(delete(Tag))
    session.execute(delete(Movie))
    session.commit()
    print("Existing data cleared.")

def load_movies(session) -> int:
    path = RES_DIR / "movies.csv"
    if not path.exists():
        print("movies.csv not found, skipping movies load.")
        return 0

    items: List[Movie] = []
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mid_raw = (row.get("movieId") or "").strip()
            title = (row.get("title") or "").strip()
            genres = (row.get("genres") or "").strip()
            if not mid_raw:
                continue
            try:
                mid = int(mid_raw)
            except ValueError:
                continue
            m = Movie(movieId=mid, title=title, genres=genres)
            items.append(m)

    if items:
        # bulk save objects is fast; Movie.movieId is PK so no duplicates because we cleared table
        session.bulk_save_objects(items)
        session.commit()
    print(f"Loaded movies: {len(items)}")
    return len(items)

def load_links(session) -> int:
    path = RES_DIR / "links.csv"
    if not path.exists():
        print("links.csv not found, skipping links load.")
        return 0

    # get set of valid movieIds in DB to skip invalid references
    existing_movie_ids = {r[0] for r in session.query(Movie.movieId).all()}

    items: List[Link] = []
    skipped = 0
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mid_raw = (row.get("movieId") or "").strip()
            imdb = (row.get("imdbId") or "").strip()
            tmdb_raw = (row.get("tmdbId") or "").strip()
            if not mid_raw:
                skipped += 1
                continue
            try:
                mid = int(mid_raw)
            except ValueError:
                skipped += 1
                continue
            if mid not in existing_movie_ids:
                skipped += 1
                continue
            try:
                tmdb = int(tmdb_raw) if tmdb_raw != "" else None
            except ValueError:
                tmdb = None
            items.append(Link(movieId=mid, imdbId=imdb, tmdbId=tmdb))

    if items:
        session.bulk_save_objects(items)
        session.commit()
    print(f"Loaded links: {len(items)} (skipped: {skipped})")
    return len(items)

def load_ratings(session) -> int:
    path = RES_DIR / "ratings.csv"
    if not path.exists():
        print("ratings.csv not found, skipping ratings load.")
        return 0

    existing_movie_ids = {r[0] for r in session.query(Movie.movieId).all()}

    items: List[Rating] = []
    skipped = 0
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            user_raw = (row.get("userId") or "").strip()
            mid_raw = (row.get("movieId") or "").strip()
            rating_raw = (row.get("rating") or "").strip()
            ts_raw = (row.get("timestamp") or "").strip()
            try:
                user = int(user_raw)
                mid = int(mid_raw)
                rating_val = float(rating_raw)
            except Exception:
                skipped += 1
                continue
            if mid not in existing_movie_ids:
                skipped += 1
                continue
            try:
                ts = int(ts_raw) if ts_raw != "" else None
            except Exception:
                ts = None
            items.append(Rating(userId=user, movieId=mid, rating=rating_val, timestamp=ts))

    if items:
        session.bulk_save_objects(items)
        session.commit()
    print(f"Loaded ratings: {len(items)} (skipped: {skipped})")
    return len(items)

def load_tags(session) -> int:
    path = RES_DIR / "tags.csv"
    if not path.exists():
        print("tags.csv not found, skipping tags load.")
        return 0

    existing_movie_ids = {r[0] for r in session.query(Movie.movieId).all()}

    items: List[Tag] = []
    skipped = 0
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            user_raw = (row.get("userId") or "").strip()
            mid_raw = (row.get("movieId") or "").strip()
            tag_text = (row.get("tag") or "").strip()
            ts_raw = (row.get("timestamp") or "").strip()
            try:
                user = int(user_raw)
                mid = int(mid_raw)
            except Exception:
                skipped += 1
                continue
            if mid not in existing_movie_ids:
                skipped += 1
                continue
            try:
                ts = int(ts_raw) if ts_raw != "" else None
            except Exception:
                ts = None
            items.append(Tag(userId=user, movieId=mid, tag=tag_text, timestamp=ts))

    if items:
        session.bulk_save_objects(items)
        session.commit()
    print(f"Loaded tags: {len(items)} (skipped: {skipped})")
    return len(items)

def main():
    print("Loading CSV files into database (SQLite).")
    create_tables()
    session = SessionLocal()
    try:
        clear_tables(session)
        load_movies(session)
        load_links(session)
        load_ratings(session)
        load_tags(session)
        print("All done.")
    finally:
        session.close()

if __name__ == "__main__":
    main()