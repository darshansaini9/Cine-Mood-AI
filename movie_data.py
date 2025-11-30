import pandas as pd
import ast
import os
import logging

logger = logging.getLogger(__name__)


class MovieDataLoader:
    def __init__(self):
        self.movies_df = None
        self.credits_df = None
        self.keywords_df = None
        self.links_df = None
        self._loaded = False

    def load_data(self):
        if self._loaded:
            return

        try:
            movies_path = 'attached_assets/tmdb_5000_movies_1764503479928.csv'
            credits_path = 'attached_assets/tmdb_5000_credits_1764503490293.csv'
            keywords_path = 'attached_assets/keywords_1_1764503399886.csv'
            links_path = 'attached_assets/links_1764503413375.csv'

            if os.path.exists(movies_path):
                self.movies_df = pd.read_csv(movies_path)
                logger.info(f"Loaded {len(self.movies_df)} movies from tmdb_5000_movies")

            if os.path.exists(credits_path):
                self.credits_df = pd.read_csv(credits_path)
                logger.info(f"Loaded {len(self.credits_df)} credits")

            if os.path.exists(keywords_path):
                self.keywords_df = pd.read_csv(keywords_path)
                logger.info(f"Loaded {len(self.keywords_df)} keywords")

            if os.path.exists(links_path):
                self.links_df = pd.read_csv(links_path)
                logger.info(f"Loaded {len(self.links_df)} links")

            self._loaded = True

        except Exception as e:
            logger.error(f"Error loading movie data: {e}")
            raise

    def parse_json_field(self, field):
        if pd.isna(field) or field == '' or field == '[]':
            return []
        try:
            if isinstance(field, str):
                return ast.literal_eval(field)
            return field
        except (ValueError, SyntaxError):
            return []

    def get_genre_names(self, genres_str):
        genres = self.parse_json_field(genres_str)
        return [g.get('name', '') for g in genres if isinstance(g, dict)]

    def get_keyword_names(self, keywords_str):
        keywords = self.parse_json_field(keywords_str)
        return [k.get('name', '') for k in keywords if isinstance(k, dict)]

    def get_cast_names(self, cast_str, limit=5):
        cast = self.parse_json_field(cast_str)
        names = [c.get('name', '') for c in cast[:limit] if isinstance(c, dict)]
        return names

    def get_all_movies(self, limit=100):
        self.load_data()
        if self.movies_df is None:
            return []

        movies = []
        df = self.movies_df.head(limit)

        for _, row in df.iterrows():
            movie = {
                'id': row.get('id'),
                'title': row.get('title', row.get('original_title', 'Unknown')),
                'overview': row.get('overview', ''),
                'genres': self.get_genre_names(row.get('genres', '[]')),
                'keywords': self.get_keyword_names(row.get('keywords', '[]')),
                'release_date': row.get('release_date', ''),
                'vote_average': row.get('vote_average', 0),
                'vote_count': row.get('vote_count', 0),
                'popularity': row.get('popularity', 0),
                'runtime': row.get('runtime', 0),
                'imdb_id': None
            }
            movies.append(movie)

        return movies

    def get_featured_movies(self, limit=20):
        self.load_data()
        if self.movies_df is None:
            return []

        df = self.movies_df.copy()
        df['vote_average'] = pd.to_numeric(df['vote_average'], errors='coerce').fillna(0)
        df['vote_count'] = pd.to_numeric(df['vote_count'], errors='coerce').fillna(0)
        df['popularity'] = pd.to_numeric(df['popularity'], errors='coerce').fillna(0)

        df = df[df['vote_count'] > 100]
        df = df.sort_values(by=['popularity', 'vote_average'], ascending=False)
        df = df.head(limit)

        movies = []
        for _, row in df.iterrows():
            movie = {
                'id': row.get('id'),
                'title': row.get('title', row.get('original_title', 'Unknown')),
                'overview': row.get('overview', ''),
                'genres': self.get_genre_names(row.get('genres', '[]')),
                'keywords': self.get_keyword_names(row.get('keywords', '[]')),
                'release_date': row.get('release_date', ''),
                'vote_average': row.get('vote_average', 0),
                'vote_count': row.get('vote_count', 0),
                'popularity': row.get('popularity', 0),
                'runtime': row.get('runtime', 0)
            }
            movies.append(movie)

        return movies

    def search_movies(self, query, limit=20):
        self.load_data()
        if self.movies_df is None or not query:
            return []

        query_lower = query.lower()
        df = self.movies_df.copy()

        mask = df['title'].fillna('').str.lower().str.contains(query_lower, regex=False)
        df = df[mask].head(limit)

        movies = []
        for _, row in df.iterrows():
            movie = {
                'id': row.get('id'),
                'title': row.get('title', row.get('original_title', 'Unknown')),
                'overview': row.get('overview', ''),
                'genres': self.get_genre_names(row.get('genres', '[]')),
                'release_date': row.get('release_date', ''),
                'vote_average': row.get('vote_average', 0),
                'popularity': row.get('popularity', 0)
            }
            movies.append(movie)

        return movies

    def get_movies_by_genre(self, genre, limit=20):
        self.load_data()
        if self.movies_df is None:
            return []

        genre_lower = genre.lower()
        df = self.movies_df.copy()

        def has_genre(genres_str):
            genres = self.get_genre_names(genres_str)
            return any(genre_lower in g.lower() for g in genres)

        mask = df['genres'].apply(has_genre)
        df = df[mask]
        df['vote_average'] = pd.to_numeric(df['vote_average'], errors='coerce').fillna(0)
        df = df.sort_values(by='vote_average', ascending=False)
        df = df.head(limit)

        movies = []
        for _, row in df.iterrows():
            movie = {
                'id': row.get('id'),
                'title': row.get('title', row.get('original_title', 'Unknown')),
                'overview': row.get('overview', ''),
                'genres': self.get_genre_names(row.get('genres', '[]')),
                'release_date': row.get('release_date', ''),
                'vote_average': row.get('vote_average', 0),
                'popularity': row.get('popularity', 0)
            }
            movies.append(movie)

        return movies

    def get_movie_by_id(self, movie_id):
        self.load_data()
        if self.movies_df is None:
            return None

        df = self.movies_df[self.movies_df['id'] == movie_id]
        if df.empty:
            return None

        row = df.iloc[0]

        cast_info = []
        if self.credits_df is not None:
            credits = self.credits_df[self.credits_df['movie_id'] == movie_id]
            if not credits.empty:
                cast_info = self.get_cast_names(credits.iloc[0].get('cast', '[]'))

        movie = {
            'id': row.get('id'),
            'title': row.get('title', row.get('original_title', 'Unknown')),
            'overview': row.get('overview', ''),
            'genres': self.get_genre_names(row.get('genres', '[]')),
            'keywords': self.get_keyword_names(row.get('keywords', '[]')),
            'release_date': row.get('release_date', ''),
            'vote_average': row.get('vote_average', 0),
            'vote_count': row.get('vote_count', 0),
            'popularity': row.get('popularity', 0),
            'runtime': row.get('runtime', 0),
            'cast': cast_info
        }

        return movie

    def get_all_genres(self):
        self.load_data()
        if self.movies_df is None:
            return []

        all_genres = set()
        for genres_str in self.movies_df['genres'].dropna():
            genres = self.get_genre_names(genres_str)
            all_genres.update(genres)

        return sorted(list(all_genres))

    def get_random_movies(self, count=10):
        self.load_data()
        if self.movies_df is None:
            return []

        df = self.movies_df.copy()
        df['vote_average'] = pd.to_numeric(df['vote_average'], errors='coerce').fillna(0)
        df = df[df['vote_average'] > 5]

        if len(df) < count:
            df = self.movies_df.sample(n=min(count, len(self.movies_df)))
        else:
            df = df.sample(n=count)

        movies = []
        for _, row in df.iterrows():
            movie = {
                'id': row.get('id'),
                'title': row.get('title', row.get('original_title', 'Unknown')),
                'overview': row.get('overview', ''),
                'genres': self.get_genre_names(row.get('genres', '[]')),
                'release_date': row.get('release_date', ''),
                'vote_average': row.get('vote_average', 0),
                'popularity': row.get('popularity', 0)
            }
            movies.append(movie)

        return movies


movie_loader = MovieDataLoader()
