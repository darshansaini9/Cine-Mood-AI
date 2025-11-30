# MovieMood - Movie Recommendation Web Application

## Overview
MovieMood is a Flask-based movie recommendation web application that suggests movies based on genre and mood. It uses CSV datasets from TMDB as the primary data source, enhanced with the OMDb API for high-quality movie posters and metadata. The application features AI-powered recommendations using OpenAI.

## Project Structure
```
├── app.py                 # Flask app configuration and database setup
├── main.py                # Main routes and entry point
├── models.py              # SQLAlchemy database models
├── movie_data.py          # CSV data processing and movie loader
├── omdb_api.py            # OMDb API integration with caching
├── openai_service.py      # OpenAI-powered recommendations
├── templates/
│   ├── base.html          # Base template with navigation
│   ├── index.html         # Homepage with hero, featured movies, mood selector
│   ├── movie_detail.html  # Individual movie details page
│   ├── genres.html        # All genres listing page
│   ├── genre_movies.html  # Movies by genre page
│   └── 404.html           # Error page
├── static/
│   ├── css/style.css      # Netflix-inspired dark theme styling
│   └── js/main.js         # Search, navigation, and UI interactions
└── attached_assets/       # CSV data files from TMDB
```

## Features
- **Hero Banner**: Large featured movie banner with poster, title, and overview
- **Search Functionality**: Real-time search with movie suggestions
- **Mood-Based Recommendations**: AI-powered movie suggestions based on user's mood
- **Genre Browsing**: Browse movies by genre with filtering
- **Movie Details**: Detailed movie information with OMDb enrichment
- **Responsive Design**: Mobile-friendly Netflix-inspired dark theme

## Technical Details

### Data Sources
- **TMDB CSV Files**: 4803+ movies with metadata, credits, keywords
- **OMDb API**: High-quality posters, ratings, cast information

### API Integration
- **OMDb API**: Uses persistent database caching to minimize API calls
- **OpenAI API**: Optional AI-powered recommendations (falls back to genre matching)

### Caching Strategy
- In-memory cache with 24-hour expiration
- PostgreSQL database cache for persistence across restarts
- Reduces OMDb API calls significantly after initial load

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string (auto-configured)
- `SESSION_SECRET`: Flask session secret key
- `OMDB_API_KEY`: OMDb API key (default provided, can be overridden)
- `OPENAI_API_KEY`: OpenAI API key for AI recommendations (optional)

## Running the Application
The application runs on port 5000 using gunicorn:
```bash
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
```

## Design System
The application uses a Netflix-inspired dark theme with:
- Primary background: #0f0f0f
- Accent color: #e50914 (Netflix red)
- Gold accent for ratings: #f5c518
- Inter font family
- Responsive horizontal scrolling movie cards
- Smooth transitions and hover effects

## Recent Changes
- Added persistent OMDb API caching using PostgreSQL
- Implemented diverse movie sampling for AI recommendations
- Enhanced fallback recommendations with rating-based sorting
- Moved API key to environment variable configuration
