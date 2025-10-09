import streamlit as st
from app.view.auth_view import AuthService  


#register view
def register_view():
    """User Registration UI"""
    st.subheader("🔐 Register New Account")

    with st.form("register_form"):
        name = st.text_input("👤 Full Name")
        email = st.text_input("📧 Email")
        password = st.text_input("🔑 Password", type="password")
        confirm_password = st.text_input("🔑 Confirm Password", type="password")
        submit = st.form_submit_button("Register")

    if submit:
        if not name or not email or not password:
            st.warning("⚠️ All fields are required.")
        elif password != confirm_password:
            st.error("❌ Passwords do not match.")
        else:
            res = AuthService.register(name, email, password)
            if res["success"]:
                st.success("✅ Registration successful! Please login now.")
            else:
                st.error(f"❌ {res['error']}")


#login view
def login_view():
    """User Login UI"""
    st.subheader("🔑 Login")

    with st.form("login_form"):
        email = st.text_input("📧 Email")
        password = st.text_input("🔒 Password", type="password")
        submit = st.form_submit_button("Login")

    if submit:
        if not email or not password:
            st.warning("⚠️ Please enter both email and password.")
        else:
            res = AuthService.login(email, password)
            if res["success"]:
                # Save session info
                st.session_state["user_email"] = email
                st.session_state["user_role"] = res["user"]["role"]

                st.success("✅ Login successful! Redirecting...")

                # 🔁 Reload app – controller will automatically route
                try:
                    st.rerun()  # ✅ Streamlit >= 1.32
                except AttributeError:
                    st.experimental_rerun()  # ✅ Backward compatibility


            else:
                st.error(f"❌ {res['error']}")



#logout view
def logout_view():
    """Clear user session and logout"""
    if "user_email" in st.session_state:
        email = st.session_state["user_email"]
        AuthService.logout(email)
        st.session_state.clear()
        st.success("👋 Logged out successfully.")
        st.experimental_rerun()
    else:
        st.info("You are not logged in.")


#current user details
def show_current_user():
    """Show currently logged-in user details."""
    if "user_email" in st.session_state:
        email = st.session_state["user_email"]
        user = AuthService.current_user(email)
        if user:
            st.write(f"📧 **Email:** {user['email']}")
            st.write(f"👤 **Name:** {user['name']}")
            st.write(f"🔑 **Role:** {user['role']}")
        else:
            st.warning("⚠️ Session expired, please login again.")
            st.session_state.clear()
    else:
        st.info("No active session found.")


#home view
def auth_home():
    """Home page with Login / Register selection."""
    st.title("🎬 Movie Recommendation System")
    st.markdown("Welcome! Please login or register to continue.")
    st.markdown("---")

    # Tabs for Login and Register
    tabs = st.tabs(["🔑 Login", "📝 Register"])

    with tabs[0]:
        login_view()

    with tabs[1]:
        register_view()
