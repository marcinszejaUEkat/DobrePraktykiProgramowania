import json
from typing import Dict
from httpx import Client


# Testy wymagają fixtury client i init_data z conftest.py

# ####################################################################
# 1. TESTY ZASOBU: MOVIES
# ####################################################################

def test_get_all_movies(client: Client, db_session, init_data: Dict):
    """a. Weryfikacja czy endpoint GET (lista) zwraca poprawną liczbę i dane."""
    response = client.get("/movies")

    # Asercja 1: Poprawny status code
    assert response.status_code == 200

    data = response.json()
    # Asercja 2: Poprawna liczba elementów (2 z init_data)
    assert len(data) == 2

    # Asercja 3: Weryfikacja struktury danych
    assert data[0]["title"] == "Test Movie 1"
    assert "genres" in data[1]


def test_get_movie_by_id_success(client: Client, init_data: Dict):
    """b. Weryfikacja czy endpoint GET (item) zwraca element o istniejącym ID."""
    movie_id = init_data["movie_id"]
    response = client.get(f"/movies/{movie_id}")

    # Asercja 1: Poprawny status code
    assert response.status_code == 200

    data = response.json()
    # Asercja 2: Zwrócony element ma poprawne ID
    assert data["movieId"] == movie_id
    # Asercja 3: Zwrócony element ma poprawny tytuł
    assert data["title"] == "Test Movie 1"


def test_get_movie_by_id_not_found(client: Client):
    """c. Weryfikacja statusu 404 dla nieistniejącego ID."""
    response = client.get("/movies/999999")

    # Asercja 1: Status code powinien być 404
    assert response.status_code == 404
    # Asercja 2: Komunikat błędu
    assert response.json()["detail"] == "Movie not found"


def test_post_and_verify_movie(client: Client, db_session):
    """d. Weryfikacja czy endpoint POST dodaje nowy element do bazy."""
    new_movie_data = {
        "movieId": 100,
        "title": "New Test Film",
        "genres": "Sci-Fi"
    }

    response = client.post("/movies", json=new_movie_data)

    # Asercja 1: Status code 201 Created
    assert response.status_code == 201

    # Asercja 2: Sprawdzenie, czy element pojawił się w bazie danych
    from main.models import Movie as MovieModel
    db_movie = db_session.query(MovieModel).filter(MovieModel.movieId == 100).first()
    assert db_movie is not None

    # Asercja 3: Weryfikacja, czy tytuł w bazie jest poprawny
    assert db_movie.title == "New Test Film"


def test_put_and_verify_movie(client: Client, db_session, init_data: Dict):
    """e. Weryfikacja czy endpoint PUT aktualizuje element w bazie."""
    movie_id = init_data["movie_id"]
    update_data = {
        "movieId": movie_id,
        "title": "Updated Title",
        "genres": "Action"
    }

    response = client.put(f"/movies/{movie_id}", json=update_data)

    # Asercja 1: Poprawny status code
    assert response.status_code == 200

    # Asercja 2: Sprawdzenie, czy zmiana pojawiła się w bazie danych
    from main.models import Movie as MovieModel
    db_movie = db_session.query(MovieModel).filter(MovieModel.movieId == movie_id).first()
    assert db_movie.title == "Updated Title"  # Tytuł musi być zaktualizowany
    assert db_movie.genres == "Action"


def test_delete_movie(client: Client, db_session, init_data: Dict):
    """Weryfikacja czy endpoint DELETE usuwa element z bazy."""
    movie_id_to_delete = init_data["movie_id"]

    response = client.delete(f"/movies/{movie_id_to_delete}")

    # Asercja 1: Poprawny status code 204 No Content
    assert response.status_code == 204

    # Asercja 2: Sprawdzenie, czy element zniknął z bazy
    from main.models import Movie as MovieModel
    db_movie = db_session.query(MovieModel).filter(MovieModel.movieId == movie_id_to_delete).first()
    assert db_movie is None

    # Asercja 3: Sprawdzenie, czy powiązane encje (Link) też zniknęły (dzięki kaskadzie w models.py)
    from main.models import Link as LinkModel
    db_link = db_session.query(LinkModel).filter(LinkModel.movieId == movie_id_to_delete).first()
    assert db_link is None


# ####################################################################
# 2. TESTY ZASOBU: LINKS
# ####################################################################

def test_post_link(client: Client, db_session, init_data: Dict):
    """Test POST: Tworzenie nowego Link i weryfikacja istnienia."""
    new_link_data = {
        "movieId": init_data["movie_id"],
        "imdbId": "tt9999",
        "tmdbId": 9999
    }
    response = client.post("/links", json=new_link_data)

    assert response.status_code == 201
    data = response.json()
    assert data["imdbId"] == "tt9999"

    # Weryfikacja w bazie danych
    from main.models import Link as LinkModel
    db_link = db_session.query(LinkModel).filter(LinkModel.imdbId == "tt9999").first()
    assert db_link is not None
    assert db_link.tmdbId == 9999


def test_get_link_by_id_success(client: Client, init_data: Dict):
    """Test GET (item): Pobranie istniejącego Link po ID."""
    link_id = init_data["link_id"]
    response = client.get(f"/links/{link_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == link_id
    assert data["imdbId"] == "tt123"


def test_get_link_by_id_not_found(client: Client):
    """Test GET (item): Status 404 dla nieistniejącego Link ID."""
    response = client.get("/links/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Link not found"


def test_put_link(client: Client, db_session, init_data: Dict):
    """Test PUT: Aktualizacja istniejącego Link i weryfikacja zmiany."""
    link_id = init_data["link_id"]
    update_data = {
        "movieId": init_data["movie_id"],  # Wymagane, nawet jeśli się nie zmienia
        "imdbId": "ttCHANGED",
        "tmdbId": 10000
    }

    response = client.put(f"/links/{link_id}", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["imdbId"] == "ttCHANGED"

    # Weryfikacja w bazie danych
    from main.models import Link as LinkModel
    db_link = db_session.query(LinkModel).filter(LinkModel.id == link_id).first()
    assert db_link.imdbId == "ttCHANGED"


def test_delete_link(client: Client, db_session, init_data: Dict):
    """Test DELETE: Usunięcie istniejącego Link."""
    link_id_to_delete = init_data["link_id"]

    response = client.delete(f"/links/{link_id_to_delete}")

    assert response.status_code == 204  # No Content

    # Weryfikacja w bazie danych
    from main.models import Link as LinkModel
    db_link = db_session.query(LinkModel).filter(LinkModel.id == link_id_to_delete).first()
    assert db_link is None


# ####################################################################
# 3. TESTY ZASOBU: RATINGS
# ####################################################################

def test_post_rating(client: Client, db_session, init_data: Dict):
    """Test POST: Tworzenie nowego Rating."""
    new_rating_data = {
        "userId": 50,
        "movieId": init_data["movie_id"],
        "rating": 3.0,
        "timestamp": 2000
    }
    response = client.post("/ratings", json=new_rating_data)
    assert response.status_code == 201
    assert response.json()["rating"] == 3.0

    from main.models import Rating as RatingModel
    db_rating = db_session.query(RatingModel).filter(RatingModel.userId == 50).first()
    assert db_rating.rating == 3.0


def test_get_rating_by_id_success(client: Client, init_data: Dict):
    """Test GET (item): Pobranie istniejącego Rating po ID."""
    rating_id = init_data["rating_id"]
    response = client.get(f"/ratings/{rating_id}")
    assert response.status_code == 200
    assert response.json()["rating"] == 4.5


def test_put_rating(client: Client, db_session, init_data: Dict):
    """Test PUT: Aktualizacja istniejącego Rating."""
    rating_id = init_data["rating_id"]
    update_data = {
        "userId": 10,
        "movieId": init_data["movie_id"],
        "rating": 5.0,  # Zmieniamy z 4.5 na 5.0
        "timestamp": 1000
    }
    response = client.put(f"/ratings/{rating_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["rating"] == 5.0

    from main.models import Rating as RatingModel
    db_rating = db_session.query(RatingModel).filter(RatingModel.id == rating_id).first()
    assert db_rating.rating == 5.0


def test_delete_rating(client: Client, db_session, init_data: Dict):
    """Test DELETE: Usunięcie istniejącego Rating."""
    rating_id_to_delete = init_data["rating_id"]
    response = client.delete(f"/ratings/{rating_id_to_delete}")
    assert response.status_code == 204

    from main.models import Rating as RatingModel
    db_rating = db_session.query(RatingModel).filter(RatingModel.id == rating_id_to_delete).first()
    assert db_rating is None


# ####################################################################
# 4. TESTY ZASOBU: TAGS
# ####################################################################

def test_post_tag(client: Client, db_session, init_data: Dict):
    """Test POST: Tworzenie nowego Tag."""
    new_tag_data = {
        "userId": 60,
        "movieId": init_data["movie_id"],
        "tag": "amazing",
        "timestamp": 3000
    }
    response = client.post("/tags", json=new_tag_data)
    assert response.status_code == 201
    assert response.json()["tag"] == "amazing"

    from main.models import Tag as TagModel
    db_tag = db_session.query(TagModel).filter(TagModel.userId == 60).first()
    assert db_tag.tag == "amazing"


def test_get_tag_by_id_success(client: Client, init_data: Dict):
    """Test GET (item): Pobranie istniejącego Tag po ID."""
    tag_id = init_data["tag_id"]
    response = client.get(f"/tags/{tag_id}")
    assert response.status_code == 200
    assert response.json()["tag"] == "sad"


def test_put_tag(client: Client, db_session, init_data: Dict):
    """Test PUT: Aktualizacja istniejącego Tag."""
    tag_id = init_data["tag_id"]
    update_data = {
        "userId": 10,
        "movieId": init_data["movie_id"],
        "tag": "happy",  # Zmieniamy z "sad" na "happy"
        "timestamp": 1000
    }
    response = client.put(f"/tags/{tag_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["tag"] == "happy"

    from main.models import Tag as TagModel
    db_tag = db_session.query(TagModel).filter(TagModel.id == tag_id).first()
    assert db_tag.tag == "happy"


def test_delete_tag(client: Client, db_session, init_data: Dict):
    """Test DELETE: Usunięcie istniejącego Tag."""
    tag_id_to_delete = init_data["tag_id"]
    response = client.delete(f"/tags/{tag_id_to_delete}")
    assert response.status_code == 204

    from main.models import Tag as TagModel
    db_tag = db_session.query(TagModel).filter(TagModel.id == tag_id_to_delete).first()
    assert db_tag is None