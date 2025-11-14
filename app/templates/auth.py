import streamlit as st
from app.view.auth import AuthService
from app.validators.user import validate_first_last_name, validate_email, validate_password

# Register View with Flags and Field Validation
def register_view():
    st.subheader("Register New Account")

    # Initialize session state for form fields if not exists
    if 'reg_first_name' not in st.session_state:
        st.session_state.reg_first_name = ""
    if 'reg_last_name' not in st.session_state:
        st.session_state.reg_last_name = ""
    if 'reg_email' not in st.session_state:
        st.session_state.reg_email = ""
    if 'reg_password' not in st.session_state:
        st.session_state.reg_password = ""
    if 'reg_confirm_password' not in st.session_state:
        st.session_state.reg_confirm_password = ""

    with st.form("register_form"):
        # First Name Field
        first_name = st.text_input("First Name", value=st.session_state.reg_first_name)
        first_name_valid = False
        if first_name:
            first_name_valid = validate_first_last_name(first_name)
            if not first_name_valid:
                st.error("❌ First name must contain only letters (no spaces or special characters)")
            else:
                st.success("✓ Valid first name")
        
        # Last Name Field
        last_name = st.text_input("Last Name", value=st.session_state.reg_last_name)
        last_name_valid = False
        if last_name:
            last_name_valid = validate_first_last_name(last_name)
            if not last_name_valid:
                st.error("❌ Last name must contain only letters (no spaces or special characters)")
            else:
                st.success("✓ Valid last name")
        
        # Email Field
        email = st.text_input("Email", value=st.session_state.reg_email)
        email_valid = False
        if email:
            email_valid = validate_email(email)
            if not email_valid:
                st.error("❌ Email must be from gmail.com, yahoo.com, or outlook.com")
            else:
                st.success("✓ Valid email address")
        
        # Password Field
        password = st.text_input("Password", type="password", value=st.session_state.reg_password)
        password_valid = False
        if password:
            password_valid = validate_password(password)
            if not password_valid:
                st.error("❌ Password must be 8+ characters with uppercase, lowercase, digit, and special character (@$!%*?&)")
            else:
                st.success("✓ Strong password")
        
        # Confirm Password Field
        confirm_password = st.text_input("Confirm Password", type="password", value=st.session_state.reg_confirm_password)
        passwords_match = False
        if confirm_password:
            passwords_match = (password == confirm_password and password != "")
            if not passwords_match:
                st.error("❌ Passwords do not match")
            else:
                st.success("✓ Passwords match")
        
        submit = st.form_submit_button("Register")

    if submit:
        # Update session state
        st.session_state.reg_first_name = first_name
        st.session_state.reg_last_name = last_name
        st.session_state.reg_email = email
        st.session_state.reg_password = password
        st.session_state.reg_confirm_password = confirm_password

        # Recalculate all validation flags
        first_name_valid = validate_first_last_name(first_name) if first_name else False
        last_name_valid = validate_first_last_name(last_name) if last_name else False
        email_valid = validate_email(email) if email else False
        password_valid = validate_password(password) if password else False
        passwords_match = (password == confirm_password and password != "" and confirm_password != "")

        # Check if all fields are filled
        all_fields_filled = bool(first_name and last_name and email and password and confirm_password)

        # Check if all validations pass
        all_validations_pass = (first_name_valid and last_name_valid and 
                               email_valid and password_valid and passwords_match)

        # Display validation summary
        if not all_fields_filled:
            st.warning("⚠️ All fields are required.")
        elif not all_validations_pass:
            st.error("❌ Please fix the errors above before submitting.")
            # Show specific issues
            if not first_name_valid:
                st.error("• Invalid first name")
            if not last_name_valid:
                st.error("• Invalid last name")
            if not email_valid:
                st.error("• Invalid email address")
            if not password_valid:
                st.error("• Invalid password")
            if not passwords_match:
                st.error("• Passwords do not match")
        else:
            # All flags are True - proceed with registration
            res = AuthService.register(first_name.strip(), last_name.strip(), email.strip(), password)
            if res["success"]:
                st.success("✅ Registration successful! Please login now.")
                # Clear form fields on success
                st.session_state.reg_first_name = ""
                st.session_state.reg_last_name = ""
                st.session_state.reg_email = ""
                st.session_state.reg_password = ""
                st.session_state.reg_confirm_password = ""
                st.session_state["show_login_tab"] = True
            else:
                st.error(res.get("error", "Registration failed."))


# Login View
def login_view():
    st.subheader("Login")

    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

    if submit:
        if not email or not password:
            st.warning("Please enter both email and password.")
        else:
            res = AuthService.login(email, password)
            if res["success"]:
                st.session_state["user_email"] = email
                st.session_state["user_role"] = res["user"]["role"]
                st.success("Login successful! Redirecting...")
                try:
                    st.rerun()  
                except AttributeError:
                    st.experimental_rerun()
            else:
                st.error(res.get("error", "Login failed."))


# Logout View
def logout_view():
    if "user_email" in st.session_state:
        email = st.session_state["user_email"]
        AuthService.logout(email)
        st.session_state.clear()
        st.success("Logged out successfully.")
        st.experimental_rerun()
    else:
        st.info("You are not logged in.")


# Show Current User Details
def show_current_user():
    if "user_email" in st.session_state:
        email = st.session_state["user_email"]
        user = AuthService.current_user(email)
        if user:
            st.write(f"**Email:** {user['email']}")
            st.write(f"**Name:** {user['name']}")
            st.write(f"**Role:** {user['role']}")
        else:
            st.warning("Session expired, please login again.")
            st.session_state.clear()
    else:
        st.info("No active session found.")


# Home View (Login / Register Selection)
def auth_home():
    st.title("Movie Recommendation System")
    st.markdown("Welcome! Please login or register to continue.")
    st.markdown("---")

    tabs = st.tabs(["Login", "Register"])

    if st.session_state.get("show_login_tab", False):
        tabs[0].select()  # Show Login tab
        st.session_state["show_login_tab"] = False   # Reset flag
    else:
        with tabs[0]:
            login_view()
        with tabs[1]:
            register_view()
