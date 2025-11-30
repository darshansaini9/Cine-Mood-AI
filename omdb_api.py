import os
import requests
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

OMDB_API_KEY = os.environ.get("OMDB_API_KEY")
OMDB_BASE_URL = "http://www.omdbapi.com/"

_cache = {}
CACHE_DURATION_HOURS = 24


def _get_cache_key(title=None, imdb_id=None):
    if imdb_id:
        return f"imdb:{imdb_id}"
    elif title:
        return f"title:{title.lower()}"
    return None


def _get_from_cache(key):
    if key in _cache:
        entry = _cache[key]
        if datetime.now() - entry['timestamp'] < timedelta(hours=CACHE_DURATION_HOURS):
            logger.debug(f"Cache hit for {key}")
            return entry['data']
        else:
            del _cache[key]
    return None


def _save_to_cache(key, data):
    _cache[key] = {
        'data': data,
        'timestamp': datetime.now()
    }


def _save_to_db_cache(title, imdb_id, data):
    try:
        from app import app, db
        from models import OMDbCache

        with app.app_context():
            cache_key = imdb_id if imdb_id else title
            existing = OMDbCache.query.filter_by(cache_key=cache_key).first()

            if existing:
                existing.poster_url = data.get('poster') if data else None
                existing.imdb_rating = data.get('imdb_rating') if data else None
                existing.director = data.get('director') if data else None
                existing.actors = data.get('actors') if data else None
                existing.awards = data.get('awards') if data else None
                existing.cached_at = datetime.utcnow()
            else:
                cache_entry = OMDbCache(
                    cache_key=cache_key,
                    title=title,
                    imdb_id=imdb_id,
                    poster_url=data.get('poster') if data else None,
                    imdb_rating=data.get('imdb_rating') if data else None,
                    director=data.get('director') if data else None,
                    actors=data.get('actors') if data else None,
                    awards=data.get('awards') if data else None
                )
                db.session.add(cache_entry)

            db.session.commit()
    except Exception as e:
        logger.debug(f"Could not save to DB cache: {e}")


def _get_from_db_cache(title=None, imdb_id=None):
    try:
        from app import app, db
        from models import OMDbCache

        with app.app_context():
            cache_key = imdb_id if imdb_id else title
            if not cache_key:
                return None

            entry = OMDbCache.query.filter_by(cache_key=cache_key).first()
            if entry:
                cache_age = datetime.utcnow() - entry.cached_at
                if cache_age < timedelta(hours=CACHE_DURATION_HOURS):
                    logger.debug(f"DB cache hit for {cache_key}")
                    return {
                        'title': entry.title,
                        'poster': entry.poster_url,
                        'imdb_rating': entry.imdb_rating,
                        'director': entry.director,
                        'actors': entry.actors,
                        'awards': entry.awards,
                        'imdb_id': entry.imdb_id
                    }
    except Exception as e:
        logger.debug(f"Could not read from DB cache: {e}")
    return None


def get_movie_details(title=None, imdb_id=None):
    cache_key = _get_cache_key(title=title, imdb_id=imdb_id)

    if cache_key:
        cached = _get_from_cache(cache_key)
        if cached is not None:
            return cached

        db_cached = _get_from_db_cache(title=title, imdb_id=imdb_id)
        if db_cached:
            _save_to_cache(cache_key, db_cached)
            return db_cached

    try:
        params = {
            'apikey': OMDB_API_KEY,
            'plot': 'short'
        }

        if imdb_id:
            params['i'] = f"tt{imdb_id}" if not str(imdb_id).startswith('tt') else imdb_id
        elif title:
            params['t'] = title
        else:
            return None

        response = requests.get(OMDB_BASE_URL, params=params, timeout=5)
        response.raise_for_status()

        data = response.json()

        if data.get('Response') == 'True':
            result = {
                'title': data.get('Title'),
                'year': data.get('Year'),
                'rated': data.get('Rated'),
                'runtime': data.get('Runtime'),
                'genre': data.get('Genre'),
                'director': data.get('Director'),
                'actors': data.get('Actors'),
                'plot': data.get('Plot'),
                'poster': data.get('Poster') if data.get('Poster') != 'N/A' else None,
                'imdb_rating': data.get('imdbRating'),
                'imdb_id': data.get('imdbID'),
                'box_office': data.get('BoxOffice'),
                'awards': data.get('Awards')
            }

            if cache_key:
                _save_to_cache(cache_key, result)
            _save_to_db_cache(title, imdb_id, result)

            return result
        else:
            logger.debug(f"Movie not found: {title or imdb_id}")
            if cache_key:
                _save_to_cache(cache_key, None)
            return None

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching from OMDb: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in get_movie_details: {e}")
        return None


def get_poster_url(title=None, imdb_id=None):
    details = get_movie_details(title=title, imdb_id=imdb_id)
    if details and details.get('poster'):
        return details['poster']
    return None


def search_movies_omdb(query, limit=10):
    try:
        params = {
            'apikey': OMDB_API_KEY,
            's': query,
            'type': 'movie'
        }

        response = requests.get(OMDB_BASE_URL, params=params, timeout=5)
        response.raise_for_status()

        data = response.json()

        if data.get('Response') == 'True':
            movies = []
            for item in data.get('Search', [])[:limit]:
                movies.append({
                    'title': item.get('Title'),
                    'year': item.get('Year'),
                    'imdb_id': item.get('imdbID'),
                    'poster': item.get('Poster') if item.get('Poster') != 'N/A' else None
                })
            return movies
        else:
            return []

    except Exception as e:
        logger.error(f"Error searching OMDb: {e}")
        return []


def enrich_movie_with_omdb(movie):
    title = movie.get('title')
    if not title:
        return movie

    omdb_data = get_movie_details(title=title)

    if omdb_data:
        movie['poster_url'] = omdb_data.get('poster')
        movie['imdb_rating'] = omdb_data.get('imdb_rating')
        movie['director'] = omdb_data.get('director')
        movie['actors'] = omdb_data.get('actors')
        movie['awards'] = omdb_data.get('awards')

    return movie
