from app.validators.user import validate_email, validate_password
from app.auth.authentication import hash_password, authenticate_user
from app.utils.logging_decorator import log_call
from app.auth.session_manager import (
    create_session, destroy_session, get_current_user, is_session_active
)
from app.auth.authorization import authorize_user, is_admin, is_user
from app.models.users_data import User


class AuthService:
    @staticmethod
    @log_call(level=20, log_args=True, log_result=False, redact=("password",))
    def register(name: str, email: str, password: str, role: str = "user"):
        """Register a new user with validation and password hashing."""
        if not validate_email(email):
            return {"success": False, "error": "Invalid email format"}
        if not validate_password(password):
            return {"success": False, "error": "Weak password"}

        if User.fetch_by_email(email):
            return {"success": False, "error": "Email already registered"}

        hashed_pwd = hash_password(password)
        new_user = User(name=name, email=email, password=hashed_pwd, role=role)
        new_user.save()
        return {"success": True, "message": "User registered successfully"}

    @staticmethod
    def login(email: str, password: str):
        """Authenticate user and create session."""
        user = authenticate_user(email, password)
        if not user:
            return {"success": False, "error": "Invalid email or password"}

        create_session(user)
        return {"success": True, "message": "Login successful", "user": user}

    @staticmethod
    def logout(email: str):
        """Log out a user."""
        destroy_session(email)
        return {"success": True, "message": "Logout successful"}

    @staticmethod
    def current_user(email: str):
        """Return currently logged-in user if active session exists."""
        if not is_session_active(email):
            return None
        return get_current_user(email)

    # ---------------- Authorization ----------------
    @staticmethod
    def check_role(user: dict, required_role: str = "user"):
        """Check if user has required role."""
        return authorize_user(user, required_role)

    @staticmethod
    def is_admin(user: dict) -> bool:
        """checking if user is admin."""
        return is_admin(user)

    @staticmethod
    def is_user(user: dict) -> bool:
        """checking if user is normal user."""
        return is_user(user)
