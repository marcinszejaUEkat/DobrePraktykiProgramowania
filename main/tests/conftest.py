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

# Importy, które teraz powinny działać
from main.database import get_db
from main.models import Base
from main.apiZajecia import app
from main.models import Movie as MovieModel, Link as LinkModel, Rating as RatingModel, Tag as TagModel
import main.models  # Jawne załadowanie metadanych jest kluczowe!

# -----------------------------------------------------------
# KROK 2: Konfiguracja Testowej Bazy Danych
# -----------------------------------------------------------

# Używamy :memory: i StaticPool, aby upewnić się, że to jest ta sama baza danych dla WSZYSTKICH wątków
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    # KLUCZOWA POPRAWKA: StaticPool wymusza ponowne użycie tego samego połączenia
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
    """Tworzy strukturę tabel raz na sesję i używa StaticPool."""
    # Tworzenie wszystkich tabel na początku sesji
    # Musimy użyć jawnego połączenia do stworzenia struktury
    Base.metadata.drop_all(bind=test_engine)  # Dla pewności
    Base.metadata.create_all(bind=test_engine)

    yield test_engine

    # Sprzątanie po zakończeniu sesji testowej
    Base.metadata.drop_all(bind=test_engine)


# -----------------------------------------------------------
# KROK 4: Nadpisanie Zależności (get_db) - Używa Testowego Silnika
# -----------------------------------------------------------

# Ta funkcja podmienia standardowe get_db na funkcję używającą testowej sesji.
# Ponieważ używamy StaticPool, każda sesja korzysta z tej samej bazy in-memory.
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Nadpisujemy zależność w aplikacji na stałe
app.dependency_overrides[get_db] = override_get_db


# -----------------------------------------------------------
# KROK 5: Fixtura Klienta HTTP (Scope="session")
# -----------------------------------------------------------

@pytest.fixture(scope="session")
def client(db_engine):  # Wymuszenie zależności od db_engine (utworzenie tabel)
    """Tworzy klienta testowego HTTP dla FastAPI."""
    with TestClient(app) as c:
        yield c


# -----------------------------------------------------------
# KROK 6: Fixtura Transakcyjna Sesji i Ładowanie Danych (Scope="function")
# -----------------------------------------------------------

@pytest.fixture(scope="function")
def db_session(db_engine):
    """Zwraca świeżą sesję bazy danych dla każdego testu (w transakcji)."""

    connection = db_engine.connect()
    # Rozpocznij transakcję, aby móc wycofać zmiany po teście
    transaction = connection.begin()
    db = TestingSessionLocal(bind=connection)

    yield db

    # Sprzątanie po teście: Wycofujemy transakcję (rollback)
    db.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def init_data(db_session):
    """Ładuje mały zestaw danych do czystej bazy przed każdym testem."""

    # JAWNE CZYSZCZENIE: Usunięcie danych, które mogły w jakiś sposób się wczytać
    db_session.query(TagModel).delete()
    db_session.query(RatingModel).delete()
    db_session.query(LinkModel).delete()
    db_session.query(MovieModel).delete()
    db_session.commit()  # Zatwierdzenie usunięcia

    # 1. MOVIE
    movie1 = MovieModel(movieId=1, title="Test Movie 1", genres="Action|Comedy")
    movie2 = MovieModel(movieId=2, title="Test Movie 2", genres="Drama")
    db_session.add_all([movie1, movie2])
    db_session.commit()

    # 2. LINK
    link1 = LinkModel(id=101, movieId=1, imdbId="tt123", tmdbId=1001)
    db_session.add(link1)
    db_session.commit()

    # 3. RATING
    rating1 = RatingModel(id=201, userId=10, movieId=1, rating=4.5, timestamp=1000)
    db_session.add(rating1)
    db_session.commit()

    # 4. TAG
    tag1 = TagModel(id=301, userId=10, movieId=2, tag="sad", timestamp=1000)
    db_session.add(tag1)
    db_session.commit()

    return {
        "movie_id": movie1.movieId,
        "link_id": link1.id,
        "rating_id": rating1.id,
        "tag_id": tag1.id
    }