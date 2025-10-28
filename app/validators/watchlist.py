
def validate_user_email(email: str) -> bool:
    """Basic check: user email contains '@' and '.'."""
    return bool(email and "@" in email and "." in email)

def validate_movie_id(movieId: int) -> bool:
    """Movie ID must be a positive integer."""
    return isinstance(movieId, int) and movieId > 0

def validate_status(status: str) -> bool:
    """Status must be 'watched' or 'not_watched'."""
    return status in {"watched", "not_watched"}
