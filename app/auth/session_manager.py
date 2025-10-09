from datetime import datetime, timedelta
from typing import Dict, Optional, List

# session store
SESSIONS: Dict[str, Dict] = {}
SESSION_DURATION: timedelta = timedelta(hours=1)

def set_session_duration(duration: timedelta) -> None:
    """Adjust global session duration (for tests)."""
    global SESSION_DURATION
    SESSION_DURATION = duration

def create_session(user: Dict) -> None:
    """Create session for user dict; user must have 'email'."""
    if "email" not in user:
        raise ValueError("user dict must contain 'email' field")
    now = datetime.now()
    SESSIONS[user["email"]] = {
        "user": user,
        "login_time": now,
        "expiry": now + SESSION_DURATION,
    }

def get_session(email: Optional[str]) -> Optional[Dict]:
    """Return session dict for email if active; else None."""
    if not email:
        return None
    session = SESSIONS.get(email)
    if not session:
        return None
    if datetime.now() > session["expiry"]:
        destroy_session(email)
        return None
    return session

def get_current_user(email: Optional[str]) -> Optional[Dict]:
    """Return user dict for email if session active; else None."""
    session = get_session(email)
    return session["user"] if session else None

def is_session_active(email: Optional[str]) -> bool:
    """Return True if session exists and not expired."""
    return get_session(email) is not None

def destroy_session(email: Optional[str]) -> None:
    """Remove session for email if exists."""
    if not email:
        return
    SESSIONS.pop(email, None)

def cleanup_sessions() -> List[str]:
    """Remove expired sessions; return list of removed emails."""
    expired = []
    now = datetime.now()
    for email, session in list(SESSIONS.items()):
        if now > session["expiry"]:
            expired.append(email)
            SESSIONS.pop(email, None)
    return expired
