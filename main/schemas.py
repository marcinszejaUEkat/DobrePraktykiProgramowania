from pydantic import BaseModel, Field
from typing import Optional, List



class MovieBase(BaseModel):
    title: str
    genres: Optional[str] = None


class LinkBase(BaseModel):
    imdbId: Optional[str] = Field(None, title="IMDB Identifier")
    tmdbId: Optional[int] = Field(None, title="TMDB Identifier")


class RatingBase(BaseModel):
    userId: int
    rating: float = Field(..., ge=0.0, le=5.0)
    timestamp: Optional[int] = None


class TagBase(BaseModel):
    userId: int
    tag: str
    timestamp: Optional[int] = None



class MovieCreate(MovieBase):
    movieId: int
    pass


class LinkCreate(LinkBase):
    movieId: int


class RatingCreate(RatingBase):
    movieId: int


class TagCreate(TagBase):
    movieId: int


class Movie(MovieBase):
    movieId: int

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


class MovieList(BaseModel):
    movies: List[Movie]


class UserBase(BaseModel):
    username: str
    roles: List[str] = ['ROLE_USER']


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int

    model_config = {
        'from_attributes': True
    }


class LoginData(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"