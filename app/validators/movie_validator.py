import re
from datetime import datetime

def validate_title(title: str) -> bool:
    """Title must be non-empty and <= 255 chars."""
    return bool(title and isinstance(title, str) and len(title.strip()) <= 255)

def validate_genres(genres: str) -> bool:
    """Genres must be comma-separated string."""
    if not genres:
        return True
    return isinstance(genres, str) and len(genres.strip()) > 0

def validate_release_date(release_date: str) -> bool:
    """Check release_date valid (YYYY-MM-DD) and not future."""
    if not release_date:
        return True  
    try:
        date_obj = datetime.strptime(release_date, "%Y-%m-%d")
        return date_obj <= datetime.now()
    except ValueError:
        return False

def validate_runtime(runtime) -> bool:
    """Runtime must be a positive number."""
    if runtime is None:
        return True  
    return isinstance(runtime, (int, float)) and runtime > 0

def validate_popularity(popularity) -> bool:
    """Popularity must be non-negative number."""
    if popularity is None:
        return True
    return isinstance(popularity, (int, float)) and popularity >= 0

def validate_vote_average(vote_average) -> bool:
    """Vote average must be 0 to 10."""
    if vote_average is None:
        return True
    return isinstance(vote_average, (int, float)) and 0 <= vote_average <= 10

def validate_vote_count(vote_count) -> bool:
    """Vote count must be non-negative integer."""
    if vote_count is None:
        return True
    return isinstance(vote_count, int) and vote_count >= 0

def validate_language(language: str) -> bool:
    """Language must be 2-letter lowercase code (default en)."""
    if not language:
        return True
    return bool(re.match(r"^[a-z]{2}$", language))

def validate_poster_path(poster_path: str) -> bool:
    """Poster path must be valid URL (optional)."""
    if not poster_path:
        return True
    return poster_path.startswith("http://") or poster_path.startswith("https://")

