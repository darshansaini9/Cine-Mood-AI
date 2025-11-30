import os
import json
import logging
import random

logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

openai_client = None

if OPENAI_API_KEY:
    try:
        from openai import OpenAI
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
        logger.info("OpenAI client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI client: {e}")


def get_diverse_movie_sample(available_movies, sample_size=200):
    if len(available_movies) <= sample_size:
        return available_movies

    sorted_by_rating = sorted(
        [m for m in available_movies if m.get('vote_average', 0) > 0],
        key=lambda x: x.get('vote_average', 0),
        reverse=True
    )

    top_rated = sorted_by_rating[:50]

    sorted_by_popularity = sorted(
        available_movies,
        key=lambda x: x.get('popularity', 0),
        reverse=True
    )
    popular = sorted_by_popularity[:50]

    remaining = [m for m in available_movies if m not in top_rated and m not in popular]
    random_sample = random.sample(remaining, min(sample_size - 100, len(remaining)))

    diverse_sample = list({m.get('id'): m for m in (top_rated + popular + random_sample)}.values())
    return diverse_sample[:sample_size]


def get_mood_based_recommendations(mood, available_movies, limit=10):
    if not openai_client:
        return get_fallback_mood_recommendations(mood, available_movies, limit)

    try:
        diverse_movies = get_diverse_movie_sample(available_movies, sample_size=200)
        movie_data = []
        for m in diverse_movies[:100]:
            movie_data.append({
                'title': m.get('title', ''),
                'genres': m.get('genres', []),
                'rating': m.get('vote_average', 0)
            })

        prompt = f"""Based on the user's mood: "{mood}", recommend the best movies from this list.
        
Available movies: {json.dumps(movie_data[:50])}

Return a JSON object with this exact format:
{{"recommendations": ["Movie Title 1", "Movie Title 2", "Movie Title 3", ...], "reason": "Brief explanation of why these movies match the mood"}}

Select up to {limit} movies that best match the mood. Only include movies from the provided list."""

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a movie recommendation expert. You understand human emotions and can suggest movies that match different moods. Always respond with valid JSON."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=1024
        )

        result = json.loads(response.choices[0].message.content)
        recommended_titles = result.get('recommendations', [])

        recommended_movies = []
        for movie in diverse_movies:
            if movie.get('title') in recommended_titles:
                movie['recommendation_reason'] = result.get('reason', '')
                recommended_movies.append(movie)
                if len(recommended_movies) >= limit:
                    break

        return recommended_movies

    except Exception as e:
        logger.error(f"Error getting AI recommendations: {e}")
        return get_fallback_mood_recommendations(mood, available_movies, limit)


def get_genre_recommendations(genre, available_movies, limit=10):
    if not openai_client:
        return get_fallback_genre_recommendations(genre, available_movies, limit)

    try:
        diverse_movies = get_diverse_movie_sample(available_movies, sample_size=200)
        movies_data = []
        for m in diverse_movies[:100]:
            movies_data.append({
                'title': m.get('title', ''),
                'genres': m.get('genres', []),
                'rating': m.get('vote_average', 0)
            })

        prompt = f"""The user wants to watch movies in the "{genre}" genre.
        
Available movies with their genres: {json.dumps(movies_data[:50])}

Return a JSON object with this exact format:
{{"recommendations": ["Movie Title 1", "Movie Title 2", "Movie Title 3", ...], "reason": "Brief explanation of the selection"}}

Select up to {limit} movies that best match the requested genre. Prioritize higher-rated movies. Only include movies from the provided list."""

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a movie recommendation expert. Help users find the best movies in their preferred genres. Always respond with valid JSON."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=1024
        )

        result = json.loads(response.choices[0].message.content)
        recommended_titles = result.get('recommendations', [])

        recommended_movies = []
        for movie in diverse_movies:
            if movie.get('title') in recommended_titles:
                recommended_movies.append(movie)
                if len(recommended_movies) >= limit:
                    break

        return recommended_movies

    except Exception as e:
        logger.error(f"Error getting genre recommendations: {e}")
        return get_fallback_genre_recommendations(genre, available_movies, limit)


def get_search_recommendations(query, available_movies, limit=10):
    if not openai_client:
        return []

    try:
        diverse_movies = get_diverse_movie_sample(available_movies, sample_size=200)
        movies_data = []
        for m in diverse_movies[:100]:
            movies_data.append({
                'title': m.get('title', ''),
                'overview': m.get('overview', '')[:200],
                'genres': m.get('genres', [])
            })

        prompt = f"""The user searched for: "{query}"
        
Available movies: {json.dumps(movies_data[:50])}

Return a JSON object with this exact format:
{{"recommendations": ["Movie Title 1", "Movie Title 2", "Movie Title 3", ...], "reason": "Brief explanation of why these match the search"}}

Select up to {limit} movies that are most relevant to the search query. Consider title matches, plot keywords, and thematic similarities. Only include movies from the provided list."""

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a movie search expert. Help users find movies based on their search queries. Always respond with valid JSON."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=1024
        )

        result = json.loads(response.choices[0].message.content)
        recommended_titles = result.get('recommendations', [])

        recommended_movies = []
        for movie in diverse_movies:
            if movie.get('title') in recommended_titles:
                recommended_movies.append(movie)
                if len(recommended_movies) >= limit:
                    break

        return recommended_movies

    except Exception as e:
        logger.error(f"Error getting search recommendations: {e}")
        return []


def get_fallback_mood_recommendations(mood, available_movies, limit=10):
    mood_lower = mood.lower()

    mood_genre_map = {
        'happy': ['Comedy', 'Family', 'Animation', 'Musical'],
        'excited': ['Action', 'Adventure', 'Thriller', 'Science Fiction'],
        'relaxed': ['Romance', 'Drama', 'Music'],
        'adventurous': ['Adventure', 'Action', 'Fantasy', 'Science Fiction'],
        'scared': ['Horror', 'Thriller', 'Mystery'],
        'romantic': ['Romance', 'Drama'],
        'thoughtful': ['Drama', 'Documentary', 'History'],
        'nostalgic': ['Family', 'Animation', 'Comedy'],
        'sad': ['Drama', 'Romance'],
        'funny': ['Comedy', 'Animation'],
        'inspiring': ['Drama', 'Biography', 'History'],
        'curious': ['Mystery', 'Science Fiction', 'Documentary']
    }

    matched_genres = []
    for key, genres in mood_genre_map.items():
        if key in mood_lower:
            matched_genres.extend(genres)
            break

    if not matched_genres:
        matched_genres = ['Drama', 'Comedy', 'Action']

    diverse_movies = get_diverse_movie_sample(available_movies, sample_size=500)

    matching_movies = [
        m for m in diverse_movies
        if any(g in m.get('genres', []) for g in matched_genres)
    ]

    matching_movies.sort(key=lambda x: x.get('vote_average', 0), reverse=True)

    recommended = matching_movies[:limit]

    if len(recommended) < limit:
        for movie in diverse_movies:
            if movie not in recommended:
                recommended.append(movie)
                if len(recommended) >= limit:
                    break

    return recommended


def get_fallback_genre_recommendations(genre, available_movies, limit=10):
    genre_lower = genre.lower()

    diverse_movies = get_diverse_movie_sample(available_movies, sample_size=500)

    matching = []
    for movie in diverse_movies:
        movie_genres = [g.lower() for g in movie.get('genres', [])]
        if any(genre_lower in g for g in movie_genres):
            matching.append(movie)

    matching.sort(key=lambda x: x.get('vote_average', 0), reverse=True)

    return matching[:limit]
