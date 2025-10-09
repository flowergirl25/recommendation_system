import re

def validate_email(email: str) -> bool:
    """Validate email format for common domains."""
    pattern = r"^[a-zA-Z0-9._%+-]+@(gmail\.com|yahoo\.com|outlook\.com)$"
    return bool(email and re.match(pattern, email))

def validate_password(password: str) -> bool:
    """Validate password strength: 8+ chars, upper, lower, digit, special."""
    if not password or len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    if not re.search(r"[@$!%*?&]", password):
        return False
    return True

def validate_name(name: str) -> bool:
    """Validate name: non-empty, letters and spaces only."""
    return bool(name and re.match(r"^[A-Za-z ]+$", name))

 