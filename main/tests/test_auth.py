from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from main.models import User as UserModel


# Importy potrzebne do testów
# (Fixtury client, db_session, admin_token, user_token są pobierane automatycznie z conftest.py)

# ####################################################################
# 1. TESTY ENDPOINTU /login
# ####################################################################

def test_login_success(client, db_session):
    """a. Poprawne logowanie - zwraca token."""
    # Najpierw musimy mieć użytkownika w bazie (rejestracja przez SQL)
    from main.auth import hash_password
    user = UserModel(username="test_login", hashed_password=hash_password("pass123"), roles="ROLE_USER")
    db_session.add(user)
    db_session.commit()

    # Próba logowania
    login_data = {"username": "test_login", "password": "pass123"}
    response = client.post("/login", json=login_data)

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_failure(client, db_session):
    """a. Błędne logowanie - złe hasło lub użytkownik."""
    # Użytkownik istnieje
    from main.auth import hash_password
    user = UserModel(username="test_fail", hashed_password=hash_password("pass123"), roles="ROLE_USER")
    db_session.add(user)
    db_session.commit()

    # Złe hasło
    response = client.post("/login", json={"username": "test_fail", "password": "WRONG_PASSWORD"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

    # Nieistniejący użytkownik
    response = client.post("/login", json={"username": "NON_EXISTENT", "password": "pass123"})
    assert response.status_code == 401


# ####################################################################
# 2. TESTY ENDPOINTU /users (DODAWANIE UŻYTKOWNIKA)
# ####################################################################

def test_create_user_as_admin(client, admin_token):
    """b. Dodawanie użytkownika przez ADMINA (z uprawnieniami)."""
    new_user_data = {
        "username": "new_user",
        "password": "secret_password",
        "roles": ["ROLE_USER"]
    }

    # Używamy tokenu admina w nagłówku
    response = client.post("/users", json=new_user_data, headers=admin_token)

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "new_user"
    assert "password" not in data  # Hasło nie powinno być zwracane jawnie!


def test_create_user_as_normal_user_forbidden(client, user_token):
    """b. Próba dodania użytkownika przez zwykłego użytkownika (bez uprawnień)."""
    new_user_data = {
        "username": "hacker_user",
        "password": "secret_password",
        "roles": ["ROLE_ADMIN"]
    }

    # Używamy tokenu zwykłego usera
    response = client.post("/users", json=new_user_data, headers=user_token)

    # Oczekujemy 403 Forbidden (brak roli ROLE_ADMIN)
    assert response.status_code == 403


def test_create_user_unauthorized(client):
    """b. Próba dodania użytkownika bez żadnego tokena."""
    new_user_data = {"username": "anon", "password": "123", "roles": []}
    response = client.post("/users", json=new_user_data)
    assert response.status_code == 401  # Brak nagłówka Authorization


# ####################################################################
# 3. TESTY ENDPOINTU /user_details
# ####################################################################

def test_user_details_success(client, user_token):
    """c. Poprawna autoryzacja /user_details."""
    response = client.get("/user_details", headers=user_token)

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "user_test"
    assert "roles" in data
    assert "sub" in data


def test_user_details_no_token(client):
    """c. Przypadek braku tokena dla /user_details."""
    response = client.get("/user_details")
    assert response.status_code == 401  # Unauthorized


def test_user_details_invalid_token(client):
    """c. Przypadek błędnego tokena."""
    headers = {"Authorization": "Bearer INVALID_TOKEN_STRING"}
    response = client.get("/user_details", headers=headers)
    assert response.status_code == 401