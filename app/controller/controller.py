import streamlit as st
from app.templates.auth import auth_home
from app.templates.user_dashboard import user_dashboard
from app.templates.admin_dashboard import admin_dashboard
from app.view.auth import AuthService

def _ensure_role_in_session():
    """
    If user_email exists in session but user_role is missing,
    try to fetch current user via AuthService and populate the role.
    If session invalid, clear state and rerun to show auth page.
    """
    if "user_email" in st.session_state and "user_role" not in st.session_state:
        try:
            user = AuthService.current_user(st.session_state["user_email"])
            if user:
                st.session_state["user_role"] = user.get("role", "user")
            else:
                st.session_state.clear()
                st.rerun()
        except Exception:
            st.session_state.clear()
            st.rerun()


def _sidebar_session_panel():
    """Small sidebar area to show current user and logout button."""
    st.sidebar.title(" Controls")
    if "user_email" in st.session_state:
        st.sidebar.markdown(f"**User:** `{st.session_state['user_email']}`")
        st.sidebar.markdown(f"**Role:** `{st.session_state.get('user_role', 'user')}`")
        st.sidebar.markdown("---")
        if st.sidebar.button(" Logout"):
            try:
                AuthService.logout(st.session_state["user_email"])
            except Exception:
                # best-effort logout; backend may already have cleared session
                pass
            st.session_state.clear()
            st.success("Logged out successfully.")
            st.rerun()
    else:
        st.sidebar.info("Not logged in — please use the Home page to Login/Register.")


def main():
    st.set_page_config(page_title=" Movie Recommendation System", layout="wide")
    _ensure_role_in_session()
    _sidebar_session_panel()

    # If not logged in, show the auth/home page (login/register)
    if "user_email" not in st.session_state:
        auth_home()
        return

    # role-based routing
    role = st.session_state.get("user_role", "user")
    if role == "admin":
        # admin dashboard expects an admin session
        admin_dashboard()
    else:
        user_dashboard()


