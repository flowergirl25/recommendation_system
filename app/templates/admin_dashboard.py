import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime
from app.view.auth_view import AuthService
from app.view.user_view import UserService
from app.view.movie_view import MovieService
from app.view.recommendation_view import RecommendationService
from app.view.watchlist_view import WatchlistService
from app.models.users_data import User
from app.models.ratings_data import Rating


#session validation
def validate_admin_session():
    """Ensure current session belongs to an admin."""
    if "user_email" not in st.session_state or st.session_state.get("user_role") != "admin":
        st.warning("⚠️ Admin access only. Please login as admin.")
        st.stop()
    return st.session_state["user_email"]


#overview section
def overview_section():
    """System overview metrics."""
    st.title("📊 System Overview")

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
    c1.metric("👥 Users", total_users)
    c2.metric("🟢 Active Users", active_users)
    c3.metric("🎬 Movies", total_movies)
    c4.metric("⭐ Ratings", total_ratings)
    c5.metric("📺 Watchlist Entries", total_watchlist)

    st.info(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


#user management section
def user_management_section():
    """Manage users — activate/deactivate/change role."""
    st.subheader("👥 User Management")

    users = User.fetch_all(active_only=False)
    st.dataframe(users)

    email = st.text_input("Enter user email:")
    action = st.selectbox("Action", ["Activate", "Deactivate", "Change Role"])

    if action == "Change Role":
        new_role = st.selectbox("New Role", ["user", "admin"])
        if st.button("Update Role"):
            User.update_role(email, new_role)
            st.success(f"✅ Role updated for {email} → {new_role}")
    elif action == "Deactivate":
        if st.button("Deactivate User"):
            User.deactivate(email)
            st.warning(f"🚫 User {email} deactivated")
    elif action == "Activate":
        if st.button("Activate User"):
            User.activate(email)
            st.success(f"🟢 User {email} activated")


# --------------------------- Movie Management ---------------------------
def movie_management_section():
    """Add, update, or manage movies."""
    st.subheader("🎬 Movie Management")

    action = st.selectbox("Choose action", ["Add", "Update", "Deactivate", "Activate"])

    if action == "Add":
        title = st.text_input("Title")
        genres = st.text_input("Genres")
        overview = st.text_area("Overview")
        release_date = st.date_input("Release Date")
        runtime = st.number_input("Runtime (mins)", min_value=0)
        popularity = st.number_input("Popularity", min_value=0.0)
        vote_average = st.number_input("Vote Average", min_value=0.0, max_value=10.0)
        vote_count = st.number_input("Vote Count", min_value=0)
        language = st.text_input("Language", value="en")
        poster_path = st.text_input("Poster URL")

        if st.button("Add Movie"):
            res = MovieService.add_movie(
                title=title, genres=genres, overview=overview, release_date=release_date,
                runtime=runtime, popularity=popularity, vote_average=vote_average,
                vote_count=vote_count, language=language, poster_path=poster_path
            )
            st.success(res["message"] if res["success"] else res["error"])

    elif action == "Update":
        movieId = st.number_input("Enter Movie ID", min_value=1, step=1)
        field = st.text_input("Field to update (e.g. title, overview)")
        value = st.text_input("New Value")
        if st.button("Update Movie"):
            res = MovieService.update_movie(movieId, **{field: value})
            st.success(res["message"] if res["success"] else res["error"])

    elif action == "Deactivate":
        movieId = st.number_input("Movie ID", min_value=1, step=1)
        if st.button("Deactivate Movie"):
            res = MovieService.deactivate_movie(movieId)
            st.warning(res["message"] if res["success"] else res["error"])

    elif action == "Activate":
        movieId = st.number_input("Movie ID", min_value=1, step=1)
        if st.button("Activate Movie"):
            res = MovieService.activate_movie(movieId)
            st.success(res["message"] if res["success"] else res["error"])


# --------------------------- Watchlist Manager ---------------------------
def watchlist_manager_section():
    """View all user watchlists."""
    st.subheader("📺 Watchlist Manager (All Users)")

    res = WatchlistService.get_all_watchlists()
    if res["success"] and res["data"]:
        st.info(f"Total Watchlist Entries: {len(res['data'])}")
        st.dataframe(res["data"])

        #email filter
        filter_email = st.text_input("🔍 Filter by User Email (optional)")
        if filter_email:
            filtered = [w for w in res["data"] if filter_email.lower() in w["user_email"].lower()]
            st.dataframe(filtered)

        #csv export
        if st.button("📤 Export All to CSV"):
            import pandas as pd
            df = pd.DataFrame(res["data"])
            df.to_csv("all_watchlists.csv", index=False)
            st.success("✅ Exported to all_watchlists.csv")
    else:
        st.warning("No watchlist entries found.")


#analytics section
def analytics_section():
    """System analytics — top movies, users, and ratings."""
    st.subheader("📈 Analytics Dashboard")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🎥 Top Rated Movies")
        top_movies = RecommendationService.get_top_rated_movies(k=10)
        if top_movies["success"]:
            titles = [m["title"] for m in top_movies["data"]]
            ratings = [m["avg_rating"] for m in top_movies["data"]]
            plt.barh(titles, ratings)
            st.pyplot(plt)
        else:
            st.warning("Unable to fetch top-rated movies.")

    with col2:
        st.markdown("### 👥 Most Active Users")
        active_users = RecommendationService.get_most_active_users(k=10)
        if active_users["success"]:
            emails = [u["email"] for u in active_users["data"]]
            counts = [u["rating_count"] for u in active_users["data"]]
            plt.barh(emails, counts)
            st.pyplot(plt)
        else:
            st.warning("Unable to fetch user activity data.")

    st.markdown("---")
    st.markdown("### ⭐ Rating Distribution")
    rating_dist = RecommendationService.get_rating_distribution()
    if rating_dist["success"]:
        x = [r["rating"] for r in rating_dist["data"]]
        y = [r["count"] for r in rating_dist["data"]]
        plt.bar(x, y)
        plt.xlabel("Rating")
        plt.ylabel("Count")
        plt.title("Rating Distribution")
        st.pyplot(plt)
    else:
        st.warning("Could not display rating distribution.")


# --------------------------- Logout ---------------------------
def logout_section():
    """Logout for admin."""
    if st.button("🔒 Logout"):
        AuthService.logout(st.session_state["user_email"])
        st.session_state.clear()
        st.success("✅ Logged out successfully.")
        st.stop()


# --------------------------- Main Dashboard ---------------------------
def admin_dashboard():
    """Main admin dashboard controller."""
    admin_email = validate_admin_session()

    menu = st.sidebar.radio(
        "Admin Navigation",
        [
            "📊 Overview",
            "👥 User Management",
            "🎬 Movie Management",
            "📺 Watchlist Manager",
            "📈 Analytics",
            "🔒 Logout",
        ],
    )

    if menu == "📊 Overview":
        overview_section()
    elif menu == "👥 User Management":
        user_management_section()
    elif menu == "🎬 Movie Management":
        movie_management_section()
    elif menu == "📺 Watchlist Manager":
        watchlist_manager_section()
    elif menu == "📈 Analytics":
        analytics_section()
    elif menu == "🔒 Logout":
        logout_section()
