def authorize_user(user: dict, required_role: str = "user") -> bool:
    """Check if user has required role (default 'user')."""
    if not user:
        return False
    return user.get("role") == required_role

def is_admin(user: dict) -> bool:
    """Check if user is an admin."""
    return authorize_user(user, "admin")

def is_user(user: dict) -> bool:
    """Check if user is a normal user."""
    return authorize_user(user, "user")
