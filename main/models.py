from sqlalchemy import Column, Integer, String, Float, BigInteger, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from typing import Optional

Base = declarative_base()


class Movie(Base):
    __tablename__ = "movies"

    movieId = Column(Integer, primary_key=True, index=True)  # id z CSV
    title = Column(String, nullable=False)
    # Proste przechowanie gatunków jako tekst "Adventure|Animation|..."
    # Jeśli w przyszłości chcesz normalizować, zrobimy dodatkową tabelę many-to-many
    genres = Column(String, nullable=True)

    links = relationship("Link", back_populates="movie", cascade="all, delete-orphan")
    ratings = relationship("Rating", back_populates="movie", cascade="all, delete-orphan")
    tags = relationship("Tag", back_populates="movie", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Movie(movieId={self.movieId}, title={self.title})>"


class Link(Base):
    __tablename__ = "links"

    id = Column(Integer, primary_key=True, autoincrement=True)
    movieId = Column(Integer, ForeignKey("movies.movieId"), nullable=False, index=True)
    imdbId = Column(String, nullable=True)
    tmdbId = Column(Integer, nullable=True)

    movie = relationship("Movie", back_populates="links")

    def __repr__(self):
        return f"<Link(movieId={self.movieId}, imdbId={self.imdbId}, tmdbId={self.tmdbId})>"


class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(Integer, nullable=False, index=True)
    movieId = Column(Integer, ForeignKey("movies.movieId"), nullable=False, index=True)
    rating = Column(Float, nullable=False)
    timestamp = Column(BigInteger, nullable=True)

    movie = relationship("Movie", back_populates="ratings")

    def __repr__(self):
        return f"<Rating(userId={self.userId}, movieId={self.movieId}, rating={self.rating})>"


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(Integer, nullable=False, index=True)
    movieId = Column(Integer, ForeignKey("movies.movieId"), nullable=False, index=True)
    tag = Column(String, nullable=False)
    timestamp = Column(BigInteger, nullable=True)

    movie = relationship("Movie", back_populates="tags")

    def __repr__(self):
        return f"<Tag(userId={self.userId}, movieId={self.movieId}, tag={self.tag})>"