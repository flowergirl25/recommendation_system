import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime
from app.view.auth import AuthService
from app.view.user import UserService
from app.view.movie import MovieService
from app.view.recommendation import RecommendationService
from app.view.watchlist import WatchlistService
from app.models.users_data import User
from app.models.ratings_data import Rating

# Session validation
def validate_admin_session():
    if "user_email" not in st.session_state or st.session_state.get("user_role") != "admin":
        st.warning("Admin access only. Please login as admin.")
        st.stop()
    return st.session_state["user_email"]

# Overview section
def overview_section():
    st.title("System Overview")
    st.markdown("---")

    users = User.fetch_all(active_only=False)
    movies = MovieService.list_movies(limit=1000)
    ratings = Rating.fetch_all()
    watchlists = WatchlistService.get_all_watchlists()

    total_users = len(users)
    active_users = len([u for u in users if u["is_active"]])
    total_movies = len(movies.get("data", []))
    total_ratings = len(ratings.get("data", [])) if ratings["success"] else 0
    total_watchlist = len(watchlists.get("data", [])) if watchlists["success"] else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Users", total_users)
    c2.metric("Active Users", active_users)
    c3.metric("Movies", total_movies)
    c4.metric("Ratings", total_ratings)
    c5.metric("Watchlist Entries", total_watchlist)

    st.markdown(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown("---")

# User management section
def user_management_section():
    st.header("User Management")
    users = User.fetch_all(active_only=False)
    max_rows = st.slider("Max user rows", 10, 100, 20)
    st.dataframe(users[:max_rows])

    with st.form(key="user_action_form"):
        email = st.text_input("User Email")
        action = st.selectbox("Choose Action", ["Activate", "Deactivate", "Change Role"])
        submit = st.form_submit_button("Submit")

        if action == "Change Role":
            new_role = st.selectbox("New Role", ["user", "admin"])
            if submit and email:
                User.update_role(email, new_role)
                st.success(f"Role updated for {email} → {new_role}")
        elif action == "Deactivate":
            if submit and email:
                User.deactivate(email)
                st.warning(f"User {email} deactivated")
        elif action == "Activate":
            if submit and email:
                User.activate(email)
                st.success(f"User {email} activated")
    st.markdown("---")

# Movie management
def movie_management_section():
    st.header("Movie Management")
    action = st.selectbox("Action", ["Add", "Update", "Deactivate", "Activate"])

    if action == "Add":
        with st.form("add_movie_form"):
            title = st.text_input("Title")
            genres = st.text_input("Genres (comma separated)")
            overview = st.text_area("Overview")
            release_date = st.date_input("Release Date")
            runtime = st.number_input("Runtime (mins)", min_value=0)
            popularity = st.number_input("Popularity", min_value=0.0)
            vote_average = st.number_input("Vote Average", min_value=0.0, max_value=10.0)
            vote_count = st.number_input("Vote Count", min_value=0)
            language = st.text_input("Language", value="en")
            poster_path = st.text_input("Poster URL")
            submit = st.form_submit_button("Add Movie")
            if submit:
                res = MovieService.add_movie(
                    title=title, genres=genres, overview=overview, release_date=release_date,
                    runtime=runtime, popularity=popularity, vote_average=vote_average,
                    vote_count=vote_count, language=language, poster_path=poster_path
                )
                if res["success"]:
                    st.success(res["message"])
                else:
                    st.error(res["error"])

    elif action == "Update":
        with st.form("update_movie_form"):
            movieId = st.number_input("Movie ID", min_value=1, step=1)
            field = st.text_input("Field to update (e.g. title)")
            value = st.text_input("New value")
            submit = st.form_submit_button("Update Movie")
            if submit:
                res = MovieService.update_movie(movieId, **{field: value})
                if res["success"]:
                    st.success(res["message"])
                else:
                    st.error(res["error"])

    elif action == "Deactivate":
        movieId = st.number_input("Movie ID", min_value=1, step=1)
        if st.button("Deactivate Movie"):
            res = MovieService.deactivate_movie(movieId)
            if res["success"]:
                st.warning(res["message"])
            else:
                st.error(res["error"])

    elif action == "Activate":
        movieId = st.number_input("Movie ID", min_value=1, step=1)
        if st.button("Activate Movie"):
            res = MovieService.activate_movie(movieId)
            if res["success"]:
                st.success(res["message"])
            else:
                st.error(res["error"])
    st.markdown("---")

# Watchlist manager
def watchlist_manager_section():
    st.header("Watchlist Manager (All Users)")
    res = WatchlistService.get_all_watchlists()
    if res["success"] and res["data"]:
        st.info(f"Total Watchlist Entries: {len(res['data'])}")
        st.dataframe(res["data"])

        filter_email = st.text_input("Filter by User Email (optional)")
        if filter_email:
            filtered = [w for w in res["data"] if filter_email.lower() in w["user_email"].lower()]
            st.dataframe(filtered)

        if st.button("Export All to CSV"):
            import pandas as pd
            df = pd.DataFrame(res["data"])
            df.to_csv("all_watchlists.csv", index=False)
            st.success("Exported to all_watchlists.csv")
    else:
        st.warning("No watchlist entries found.")
    st.markdown("---")

# Analytics section
def analytics_section():
    st.header("Analytics Dashboard")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top Rated Movies")
        top_movies = RecommendationService.get_top_rated_movies(k=10)
        if top_movies["success"]:
            titles = [m["title"] for m in top_movies["data"]]
            ratings = [m["avg_rating"] for m in top_movies["data"]]
            fig, ax = plt.subplots()
            ax.barh(titles, ratings)
            st.pyplot(fig)
        else:
            st.warning("Unable to fetch top-rated movies.")

    with col2:
        st.subheader("Most Active Users")
        active_users = RecommendationService.get_most_active_users(k=10)
        if active_users["success"]:
            emails = [u["email"] for u in active_users["data"]]
            counts = [u["rating_count"] for u in active_users["data"]]
            fig, ax = plt.subplots()
            ax.barh(emails, counts)
            st.pyplot(fig)
        else:
            st.warning("Unable to fetch user activity data.")

    st.markdown("---")
    st.subheader("Rating Distribution")
    rating_dist = RecommendationService.get_rating_distribution()
    if rating_dist["success"]:
        x = [r["rating"] for r in rating_dist["data"]]
        y = [r["count"] for r in rating_dist["data"]]
        fig, ax = plt.subplots()
        ax.bar(x, y)
        ax.set_xlabel("Rating")
        ax.set_ylabel("Count")
        ax.set_title("Rating Distribution")
        st.pyplot(fig)
    else:
        st.warning("Could not display rating distribution.")

# Logout section
def logout_section():
    if st.button("Logout"):
        AuthService.logout(st.session_state["user_email"])
        st.session_state.clear()
        st.success("Logged out successfully.")
        st.stop()

# Main Dashboard
def admin_dashboard():
    admin_email = validate_admin_session()
    st.sidebar.title("Admin Panel")
    menu = st.sidebar.radio(
        "Navigation",
        [
            "Overview",
            "User Management",
            "Movie Management",
            "Watchlist Manager",
            "Analytics",
            "Logout",
        ],
    )

    if menu == "Overview":
        overview_section()
    elif menu == "User Management":
        user_management_section()
    elif menu == "Movie Management":
        movie_management_section()
    elif menu == "Watchlist Manager":
        watchlist_manager_section()
    elif menu == "Analytics":
        analytics_section()
    elif menu == "Logout":
        logout_section()
