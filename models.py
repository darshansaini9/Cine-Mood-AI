from app import db
from datetime import datetime


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tmdb_id = db.Column(db.Integer, unique=True, nullable=True)
    imdb_id = db.Column(db.String(20), nullable=True)
    title = db.Column(db.String(500), nullable=False)
    overview = db.Column(db.Text, nullable=True)
    genres = db.Column(db.Text, nullable=True)
    keywords = db.Column(db.Text, nullable=True)
    cast = db.Column(db.Text, nullable=True)
    release_date = db.Column(db.String(20), nullable=True)
    vote_average = db.Column(db.Float, nullable=True)
    vote_count = db.Column(db.Integer, nullable=True)
    popularity = db.Column(db.Float, nullable=True)
    runtime = db.Column(db.Integer, nullable=True)
    poster_url = db.Column(db.String(500), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'tmdb_id': self.tmdb_id,
            'imdb_id': self.imdb_id,
            'title': self.title,
            'overview': self.overview,
            'genres': self.genres,
            'keywords': self.keywords,
            'cast': self.cast,
            'release_date': self.release_date,
            'vote_average': self.vote_average,
            'vote_count': self.vote_count,
            'popularity': self.popularity,
            'runtime': self.runtime,
            'poster_url': self.poster_url
        }


class SearchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    query = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())


class OMDbCache(db.Model):
    __tablename__ = 'omdb_cache'
    id = db.Column(db.Integer, primary_key=True)
    cache_key = db.Column(db.String(500), unique=True, nullable=False, index=True)
    title = db.Column(db.String(500), nullable=True)
    imdb_id = db.Column(db.String(20), nullable=True)
    poster_url = db.Column(db.String(500), nullable=True)
    imdb_rating = db.Column(db.String(10), nullable=True)
    director = db.Column(db.String(500), nullable=True)
    actors = db.Column(db.Text, nullable=True)
    awards = db.Column(db.Text, nullable=True)
    cached_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<OMDbCache {self.title}>'
