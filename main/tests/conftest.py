import sys
from pathlib import Path
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool  # Używamy StaticPool dla połączeń in-memory

# -----------------------------------------------------------
# KROK 1: Naprawienie ścieżek importu
# -----------------------------------------------------------

# Dodaj główny katalog projektu do ścieżki systemowej
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from main.database import get_db
from main.models import Base
from main.apiZajecia import app
from main.models import Movie as MovieModel, Link as LinkModel, Rating as RatingModel, Tag as TagModel, User as UserModel
from main.auth import create_access_token, hash_password

# -----------------------------------------------------------
# KROK 2: Konfiguracja Testowej Bazy Danych
# -----------------------------------------------------------

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    future=True
)

TestingSessionLocal = sessionmaker(
    bind=test_engine, autoflush=False, autocommit=False, future=True
)


# -----------------------------------------------------------
# KROK 3: Fixtura Bazy Danych (Scope="session")
# -----------------------------------------------------------

@pytest.fixture(scope="session")
def db_engine():
    """Tworzy strukturę tabel raz na sesję."""
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield test_engine
    Base.metadata.drop_all(bind=test_engine)


# -----------------------------------------------------------
# KROK 4: Nadpisanie Zależności (get_db)
# -----------------------------------------------------------

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


# -----------------------------------------------------------
# KROK 5: Fixtura Klienta HTTP
# -----------------------------------------------------------

@pytest.fixture(scope="session")
def client(db_engine):
    with TestClient(app) as c:
        yield c


# -----------------------------------------------------------
# KROK 6: Fixtura Sesji z CZYSZCZENIEM (Kluczowa zmiana)
# -----------------------------------------------------------

@pytest.fixture(scope="function")
def db_session(db_engine):
    """Zwraca sesję i CZYŚCI BAZĘ przed każdym testem."""
    connection = db_engine.connect()
    transaction = connection.begin()
    db = TestingSessionLocal(bind=connection)

    # --- KLUCZOWA ZMIANA: JAWNE CZYSZCZENIE WSZYSTKICH TABEL ---
    # Dzięki temu każdy test startuje z pustą bazą, nawet jeśli poprzedni zrobił commit()
    db.query(TagModel).delete()
    db.query(RatingModel).delete()
    db.query(LinkModel).delete()
    db.query(MovieModel).delete()
    db.query(UserModel).delete()  # <--- Usuwamy też użytkowników!
    db.commit()
    # -----------------------------------------------------------

    yield db

    db.close()
    transaction.rollback()
    connection.close()


# -----------------------------------------------------------
# KROK 7: Fixtury Danych i Tokenów
# -----------------------------------------------------------

@pytest.fixture(scope="function")
def init_data(db_session):
    """Ładuje dane filmów (bez czyszczenia, bo robi to db_session)."""
    # (Usunęliśmy stąd delete(), bo jest już w db_session)

    movie1 = MovieModel(movieId=1, title="Test Movie 1", genres="Action|Comedy")
    movie2 = MovieModel(movieId=2, title="Test Movie 2", genres="Drama")
    db_session.add_all([movie1, movie2])
    db_session.commit()

    link1 = LinkModel(id=101, movieId=1, imdbId="tt123", tmdbId=1001)
    db_session.add(link1);
    db_session.commit()

    rating1 = RatingModel(id=201, userId=10, movieId=1, rating=4.5, timestamp=1000)
    db_session.add(rating1);
    db_session.commit()

    tag1 = TagModel(id=301, userId=10, movieId=2, tag="sad", timestamp=1000)
    db_session.add(tag1);
    db_session.commit()

    return {
        "movie_id": movie1.movieId,
        "link_id": link1.id,
        "rating_id": rating1.id,
        "tag_id": tag1.id
    }


@pytest.fixture(scope="function")
def admin_token(db_session):
    """Tworzy admina i zwraca token."""
    # Tworzymy admina (baza jest czysta dzięki db_session)
    admin_data = UserModel(
        username="admin_test",
        hashed_password=hash_password("admin123"),
        roles="ROLE_USER|ROLE_ADMIN"
    )
    db_session.add(admin_data)
    db_session.commit()

    token = create_access_token(data={"username": "admin_test", "roles": ["ROLE_USER", "ROLE_ADMIN"]})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def user_token(db_session):
    """Tworzy zwykłego usera i zwraca token."""
    user_data = UserModel(
        username="user_test",
        hashed_password=hash_password("user123"),
        roles="ROLE_USER"
    )
    db_session.add(user_data)
    db_session.commit()

    token = create_access_token(data={"username": "user_test", "roles": ["ROLE_USER"]})
    return {"Authorization": f"Bearer {token}"}