import pytest
from datetime import timedelta
from unittest.mock import patch, MagicMock

# Import from your actual module structure
from app.auth.authentication import hash_password, verify_password, authenticate_user
from app.auth.session_manager import (
    create_session, get_session, get_current_user,
    is_session_active, destroy_session, cleanup_sessions,
    set_session_duration, SESSIONS
)
from app.auth.authorization import authorize_user, is_admin, is_user


def test_password_hash_and_check():
    """Test password hashing and verification."""
    pwd = "Secure123!"
    hashed = hash_password(pwd)
    assert hashed != pwd
    assert verify_password(pwd, hashed)
    assert not verify_password("WrongPass", hashed)


def test_session_lifecycle():
    """Test complete session lifecycle."""
    # Clear any existing sessions
    SESSIONS.clear()
    
    user = {"email": "user@gmail.com", "role": "user"}
    create_session(user)
    
    session = get_session(user["email"])
    assert session is not None
    assert "user" in session
    assert "login_time" in session
    assert "expiry" in session
    
    current = get_current_user(user["email"])
    assert current["email"] == user["email"]
    assert is_session_active(user["email"])
    
    destroy_session(user["email"])
    assert not is_session_active(user["email"])
    assert get_session(user["email"]) is None


def test_session_expiry():
    """Test session expiration functionality."""
    # Clear any existing sessions
    SESSIONS.clear()
    
    user = {"email": "expire@gmail.com", "role": "user"}
    
    # Set very short duration and create session
    set_session_duration(timedelta(seconds=-1))  # Already expired
    create_session(user)
    
    # Session should be expired and cleaned up
    expired_emails = cleanup_sessions()
    assert "expire@gmail.com" in expired_emails
    assert not is_session_active(user["email"])
    
    # Reset to normal duration
    set_session_duration(timedelta(hours=1))


def test_session_missing_email():
    """Test session creation with invalid user data."""
    with pytest.raises(ValueError, match="user dict must contain 'email' field"):
        create_session({"role": "user"})  # Missing email


def test_session_edge_cases():
    """Test session manager edge cases."""
    # Clear any existing sessions
    SESSIONS.clear()
    
    # Test with None email
    assert get_session(None) is None
    assert get_current_user(None) is None
    assert not is_session_active(None)
    
    # Test with non-existent email
    assert get_session("nonexistent@test.com") is None
    assert get_current_user("nonexistent@test.com") is None
    assert not is_session_active("nonexistent@test.com")
    
    # Test destroy with None and non-existent email (should not raise errors)
    destroy_session(None)
    destroy_session("nonexistent@test.com")


def test_authorize_user():
    """Test basic authorization functionality."""
    user_admin = {"email": "admin@gmail.com", "role": "admin"}
    user_regular = {"email": "user@gmail.com", "role": "user"}
    
    # Test admin authorization
    assert authorize_user(user_admin, "admin")
    assert not authorize_user(user_regular, "admin")
    
    # Test user authorization
    assert authorize_user(user_regular, "user")
    assert not authorize_user(user_admin, "user")  # Admin != user in strict mode
    
    # Test default role (user)
    assert authorize_user(user_regular)  # Should default to "user"
    assert not authorize_user(user_admin)  # Admin role != default "user"


def test_role_checks():
    """Test role checking convenience functions."""
    admin_user = {"email": "admin@gmail.com", "role": "admin"}
    regular_user = {"email": "user@gmail.com", "role": "user"}
    
    # Test role checking functions
    assert is_admin(admin_user) == True
    assert is_user(regular_user) == True
    assert not is_admin(regular_user)
    assert not is_user(admin_user)  # Admin role != user role in strict mode
    
    # Test a function that manually checks permissions
    def secured_function(u):
        if not is_admin(u):
            raise PermissionError("Admin access required")
        return f"Welcome {u['email']}"
    
    # Should work for admin
    assert secured_function(admin_user) == "Welcome admin@gmail.com"
    
    # Should fail for regular user
    with pytest.raises(PermissionError, match="Admin access required"):
        secured_function(regular_user)


def test_authorization_edge_cases():
    """Test edge cases for authorization functions."""
    # Test with None user
    assert not authorize_user(None, "user")
    assert not is_admin(None)
    assert not is_user(None)
    
    # Test with empty dict
    empty_user = {}
    assert not authorize_user(empty_user, "user")
    assert not is_admin(empty_user)
    assert not is_user(empty_user)
    
    # Test with missing role
    user_no_role = {"email": "test@example.com"}
    assert not authorize_user(user_no_role, "user")
    assert not is_admin(user_no_role)
    assert not is_user(user_no_role)

from app.auth.authentication import authenticate_user, hash_password
from unittest.mock import patch

@patch('app.auth.authentication.User.fetch_by_email')
def test_authenticate_user(mock_fetch_by_email):
    """Test user authentication with mocked User model."""
    # Mock successful authentication
    mock_user = {
        "email": "test@gmail.com",
        "password": hash_password("correct_password"),
        "is_active": True,
        "role": "user"
    }
    mock_fetch_by_email.return_value = mock_user
    
    # Test successful authentication
    result = authenticate_user("test@gmail.com", "correct_password")
    assert result is not None
    assert result["email"] == "test@gmail.com"
    
    # Test wrong password
    result = authenticate_user("test@gmail.com", "wrong_password")
    assert result is None
    
    # Test inactive user
    mock_user_inactive = {
        "email": "test@gmail.com",
        "password": hash_password("correct_password"),
        "is_active": False,
        "role": "user"
    }
    mock_fetch_by_email.return_value = mock_user_inactive
    result = authenticate_user("test@gmail.com", "correct_password")
    assert result is None
    
    # Test non-existent user
    mock_fetch_by_email.return_value = None
    result = authenticate_user("nonexistent@example.com", "password")
    assert result is None

def test_cleanup_sessions():
    """Test session cleanup functionality."""
    # Clear any existing sessions
    SESSIONS.clear()
    
    # Create multiple sessions with different expiry times
    user1 = {"email": "user1@test.com", "role": "user"}
    user2 = {"email": "user2@test.com", "role": "user"}
    user3 = {"email": "user3@test.com", "role": "user"}
    
    # Create sessions with short duration that will expire
    set_session_duration(timedelta(seconds=-1))
    create_session(user1)
    create_session(user2)
    
    # Create one session with normal duration
    set_session_duration(timedelta(hours=1))
    create_session(user3)
    
    # Run cleanup
    expired_emails = cleanup_sessions()
    
    # Should have cleaned up the first two sessions
    assert len(expired_emails) == 2
    assert "user1@test.com" in expired_emails
    assert "user2@test.com" in expired_emails
    assert "user3@test.com" not in expired_emails
    
    # Verify states
    assert not is_session_active("user1@test.com")
    assert not is_session_active("user2@test.com")
    assert is_session_active("user3@test.com")


# Cleanup function to run after tests
def teardown_module():
    """Clean up after all tests."""
    SESSIONS.clear()
    set_session_duration(timedelta(hours=1))