import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from main.database import get_db
from main.models import User as UserModel

# Stałe Konfiguracji
SECRET_KEY = "super_secret_key_from_env"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# --- FUNKCJE HASHUJĄCE ---

def hash_password(password: str) -> str:
    """Haszuje hasło używając bcrypt."""
    pwd_bytes = password.encode('utf-8')
    hashed_bytes = bcrypt.hashpw(pwd_bytes, bcrypt.gensalt())
    return hashed_bytes.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Weryfikuje hasło jawne z hashem używając bcrypt."""
    try:
        plain_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(plain_bytes, hashed_bytes)
    except Exception:
        return False


# --- FUNKCJE JWT ---

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Tworzy token JWT z danymi i czasem ważności."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "iat": datetime.utcnow(), "sub": to_encode["username"]})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user_from_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Pobiera i weryfikuje token, zwracając obiekt User z bazy danych."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Dekodowanie
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        if username is None:
            raise credentials_exception

        user = db.query(UserModel).filter(UserModel.username == username).first()
        if user is None:
            raise credentials_exception

        user.payload_roles = payload.get("roles", [])
        user.jwt_payload = payload
        return user

    except jwt.PyJWTError:
        raise credentials_exception


# --- AUTORYZACJA ROLAMI ---

def role_required(required_roles: List[str]):
    """Zależność do weryfikacji, czy zalogowany użytkownik ma wymaganą rolę."""

    def role_checker(current_user: UserModel = Depends(get_current_user_from_token)):

        for required_role in required_roles:
            if required_role in current_user.payload_roles:
                return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have required permissions"
        )

    return role_checker