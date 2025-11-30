from pydantic import BaseModel, Field
from typing import Optional, List


# Base Schemas (używane do walidacji danych wejściowych POST/PUT)

class MovieBase(BaseModel):
    title: str
    # Wymagany format: "Adventure|Animation|..."
    genres: Optional[str] = None


class LinkBase(BaseModel):
    imdbId: Optional[str] = Field(None, title="IMDB Identifier")
    tmdbId: Optional[int] = Field(None, title="TMDB Identifier")


class RatingBase(BaseModel):
    userId: int
    rating: float = Field(..., ge=0.0, le=5.0)  # Ogranicz rating do zakresu 0.0 - 5.0
    timestamp: Optional[int] = None


class TagBase(BaseModel):
    userId: int
    tag: str
    timestamp: Optional[int] = None


# Create Schemas (dla operacji POST - dziedziczą z Base)

class MovieCreate(MovieBase):
    # W POST, jeśli movieId jest kluczem głównym, który chcesz ustawić
    # (a nie jest autoinkrementowany), musi być wymagany.
    # W Twoim przypadku movieId jest importowane z CSV i jest kluczem PK
    movieId: int
    pass


class LinkCreate(LinkBase):
    movieId: int


class RatingCreate(RatingBase):
    movieId: int


class TagCreate(TagBase):
    movieId: int


# --- Response Schemas (dla operacji GET - dziedziczą z Base i dodają PK) ---

# Usuwamy zewnętrzną klasę Config!
# Zamiast niej, użyjemy model_config jako słownika wewnątrz każdej klasy

class Movie(MovieBase):
    movieId: int

    # TUTAJ JEST POPRAWKA: Definiujemy model_config jako słownik.
    model_config = {
        'from_attributes': True
    }


class Link(LinkBase):
    id: int
    movieId: int

    model_config = {
        'from_attributes': True
    }


class Rating(RatingBase):
    id: int
    movieId: int

    model_config = {
        'from_attributes': True
    }


class Tag(TagBase):
    id: int
    movieId: int

    model_config = {
        'from_attributes': True
    }


# Wymiana schematu dla odpowiedzi na listę wszystkich filmów
class MovieList(BaseModel):
    movies: List[Movie]