import re
from datetime import datetime

def validate_user_email(email: str) -> bool:
    """Validate user email format."""
    if not email:
        return False
    return bool(re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email))

def validate_movie_id(movieId) -> bool:
    """Movie ID must be a positive integer."""
    return isinstance(movieId, int) and movieId > 0

def validate_rating_value(rating) -> bool:
    """Rating must be float between 0.5 and 5.0 (MovieLens scale)."""
    if rating is None:
        return False
    return isinstance(rating, (int, float)) and 0.5 <= float(rating) <= 5.0

def validate_timestamp(timestamp) -> bool:
    """Check if timestamp is a valid datetime or None (defaults to now)."""
    if not timestamp:
        return True
    if isinstance(timestamp, datetime):
        return True
    try:
        if isinstance(timestamp, str):
            datetime.fromisoformat(timestamp)
            return True
    except ValueError:
        return False
    return False

