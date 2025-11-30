from app import app
from flask import render_template, request, jsonify
import logging
from movie_data import movie_loader
from omdb_api import get_movie_details, get_poster_url, enrich_movie_with_omdb
from openai_service import get_mood_based_recommendations, get_genre_recommendations

logger = logging.getLogger(__name__)


@app.route('/')
def index():
    try:
        featured_movies = movie_loader.get_featured_movies(limit=20)

        for movie in featured_movies[:10]:
            poster = get_poster_url(title=movie.get('title'))
            movie['poster_url'] = poster

        hero_movie = None
        if featured_movies:
            hero_movie = featured_movies[0]
            omdb_data = get_movie_details(title=hero_movie.get('title'))
            if omdb_data:
                hero_movie['poster_url'] = omdb_data.get('poster')
                hero_movie['imdb_rating'] = omdb_data.get('imdb_rating')
                hero_movie['director'] = omdb_data.get('director')

        genres = movie_loader.get_all_genres()

        action_movies = movie_loader.get_movies_by_genre('Action', limit=10)
        for movie in action_movies[:5]:
            poster = get_poster_url(title=movie.get('title'))
            movie['poster_url'] = poster

        comedy_movies = movie_loader.get_movies_by_genre('Comedy', limit=10)
        for movie in comedy_movies[:5]:
            poster = get_poster_url(title=movie.get('title'))
            movie['poster_url'] = poster

        return render_template('index.html',
                               hero_movie=hero_movie,
                               featured_movies=featured_movies,
                               action_movies=action_movies,
                               comedy_movies=comedy_movies,
                               genres=genres)
    except Exception as e:
        logger.error(f"Error in index route: {e}")
        return render_template('index.html',
                               hero_movie=None,
                               featured_movies=[],
                               action_movies=[],
                               comedy_movies=[],
                               genres=[])


@app.route('/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify({'movies': []})

    try:
        movies = movie_loader.search_movies(query, limit=20)

        for movie in movies[:8]:
            poster = get_poster_url(title=movie.get('title'))
            movie['poster_url'] = poster

        return jsonify({'movies': movies})
    except Exception as e:
        logger.error(f"Error in search: {e}")
        return jsonify({'movies': [], 'error': str(e)})


@app.route('/recommend/mood')
def recommend_by_mood():
    mood = request.args.get('mood', '')
    if not mood:
        return jsonify({'movies': [], 'error': 'Mood is required'})

    try:
        all_movies = movie_loader.get_featured_movies(limit=100)
        recommended = get_mood_based_recommendations(mood, all_movies, limit=12)

        for movie in recommended[:6]:
            poster = get_poster_url(title=movie.get('title'))
            movie['poster_url'] = poster

        return jsonify({'movies': recommended, 'mood': mood})
    except Exception as e:
        logger.error(f"Error in mood recommendation: {e}")
        return jsonify({'movies': [], 'error': str(e)})


@app.route('/recommend/genre')
def recommend_by_genre():
    genre = request.args.get('genre', '')
    if not genre:
        return jsonify({'movies': [], 'error': 'Genre is required'})

    try:
        all_movies = movie_loader.get_featured_movies(limit=100)
        recommended = get_genre_recommendations(genre, all_movies, limit=12)

        for movie in recommended[:6]:
            poster = get_poster_url(title=movie.get('title'))
            movie['poster_url'] = poster

        return jsonify({'movies': recommended, 'genre': genre})
    except Exception as e:
        logger.error(f"Error in genre recommendation: {e}")
        return jsonify({'movies': [], 'error': str(e)})


@app.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    try:
        movie = movie_loader.get_movie_by_id(movie_id)
        if not movie:
            return render_template('404.html'), 404

        movie = enrich_movie_with_omdb(movie)

        similar_movies = movie_loader.get_movies_by_genre(
            movie.get('genres', ['Drama'])[0] if movie.get('genres') else 'Drama',
            limit=6
        )

        for m in similar_movies[:4]:
            poster = get_poster_url(title=m.get('title'))
            m['poster_url'] = poster

        return render_template('movie_detail.html', movie=movie, similar_movies=similar_movies)
    except Exception as e:
        logger.error(f"Error in movie detail: {e}")
        return render_template('404.html'), 404


@app.route('/genres')
def genres():
    try:
        all_genres = movie_loader.get_all_genres()
        return render_template('genres.html', genres=all_genres)
    except Exception as e:
        logger.error(f"Error in genres: {e}")
        return render_template('genres.html', genres=[])


@app.route('/genre/<genre_name>')
def genre_movies(genre_name):
    try:
        movies = movie_loader.get_movies_by_genre(genre_name, limit=30)

        for movie in movies[:12]:
            poster = get_poster_url(title=movie.get('title'))
            movie['poster_url'] = poster

        return render_template('genre_movies.html', genre=genre_name, movies=movies)
    except Exception as e:
        logger.error(f"Error in genre movies: {e}")
        return render_template('genre_movies.html', genre=genre_name, movies=[])


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
