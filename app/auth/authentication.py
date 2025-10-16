import bcrypt
from app.models.users_data import User

def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check if plain password matches hashed."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def authenticate_user(email: str, password: str):
    """Authenticate user by email and password, return user dict or None."""
    user = User.fetch_by_email(email)
    if not user or not user["is_active"]:
        return None
    if verify_password(password, user["password"]):
        return user
    return None
