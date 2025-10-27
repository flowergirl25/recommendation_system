import streamlit as st
from datetime import datetime

from app.view.movie_view import MovieService
from app.view.watchlist_view import WatchlistService
from app.view.rating_view import RatingService
from app.view.recommendation_view import RecommendationService
from app.view.user_view import UserService

# Custom CSS theme (no branding or emojis)
st.markdown("""
<style>
:root {
    --primary-red: #E50914;
    --primary-dark-red: #B20710;
    --primary-black: #141414;
    --primary-dark-gray: #181818;
    --primary-gray: #2F2F2F;
    --primary-light-gray: #B3B3B3;
    --primary-white: #FFFFFF;
}
/* App background and typography */
.stApp { background-color: var(--primary-black); color: var(--primary-white); }
h1, h2, h3, h4, h5, h6 { color: var(--primary-white) !important; font-weight: 700; letter-spacing: -0.5px; }
h1 { font-size: 3rem !important; margin-bottom: 1rem; }
h2 { font-size: 2rem !important; margin-top: 2rem; margin-bottom: 1rem; }
h3 { font-size: 1.5rem !important; color: var(--primary-red) !important; }
p, span, label, .stMarkdown { color: var(--primary-light-gray) !important; }
/* Card styles */
.movie-card { background: linear-gradient(145deg, var(--primary-dark-gray), var(--primary-gray)); border-radius: 12px; padding: 20px; margin: 15px 0; border: 1px solid transparent; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
.movie-card:hover { transform: translateY(-8px) scale(1.02); border: 1px solid var(--primary-red); box-shadow: 0 8px 25px rgba(229,9,20,0.3); }
/* Button styles */
.stButton button { background: linear-gradient(90deg, var(--primary-red), var(--primary-dark-red)); color: var(--primary-white); border: none; border-radius: 6px; padding: 12px 28px; font-weight: 700; font-size: 1rem; letter-spacing: 1px; box-shadow: 0 4px 15px rgba(229,9,20,0.4); }
.stButton button:hover { background: linear-gradient(90deg,#F40612,var(--primary-red)); transform: scale(1.05); box-shadow: 0 6px 20px rgba(229,9,20,0.6); }
.stButton button:active { transform: scale(0.98); }
.stButton button[kind="secondary"] { background: transparent; border: 2px solid var(--primary-white); color: var(--primary-white); }
.stButton button[kind="secondary"]:hover { background: var(--primary-white); color: var(--primary-black); }
/* Metrics */
[data-testid="stMetricValue"] { color: var(--primary-red); font-size: 32px; font-weight: 900; text-shadow: 0 2px 10px rgba(229,9,20,0.5); }
[data-testid="stMetricLabel"] { color: var(--primary-light-gray) !important; font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }
[data-testid="stMetricDelta"] { color: #46D369; }
.stTextInput input, .stSelectbox select, .stNumberInput input { background-color: var(--primary-gray); color: var(--primary-white); border: 2px solid #404040; border-radius: 6px; padding: 12px; font-size: 1rem; }
.stTextInput input:focus, .stSelectbox select:focus, .stNumberInput input:focus { border-color: var(--primary-red); box-shadow: 0 0 0 2px rgba(229,9,20,0.2); background-color: var(--primary-dark-gray); }
/* Slider */
.stSlider { padding: 20px 0; }
.stSlider [data-baseweb="slider"] { background-color: var(--primary-gray); }
.stSlider [data-testid="stTickBar"] div { background-color: var(--primary-red); }
/* Radio buttons */
.stRadio [role="radiogroup"] { gap: 15px; }
.stRadio label { background-color: var(--primary-gray); padding: 12px 24px; border-radius: 6px; border: 2px solid #404040; color: var(--primary-white) !important; }
.stRadio label:hover { border-color: var(--primary-red); background-color: var(--primary-dark-gray); }
.stRadio [data-checked="true"] label { background-color: var(--primary-red); border-color: var(--primary-red); color: var(--primary-white) !important; }
/* Sidebar */
[data-testid="stSidebar"] { background: linear-gradient(180deg, #000000, var(--primary-dark-gray)); border-right: 1px solid var(--primary-gray); }
[data-testid="stSidebar"] .stRadio label { color: var(--primary-light-gray) !important; background-color: transparent; border: none; padding: 12px 20px; border-left: 3px solid transparent; border-radius: 0; }
[data-testid="stSidebar"] .stRadio label:hover { background-color: var(--primary-gray); border-left-color: var(--primary-red); color: var(--primary-white) !important; }
[data-testid="stSidebar"] .stRadio [data-checked="true"] label { background-color: var(--primary-gray); border-left-color: var(--primary-red); color: var(--primary-white) !important; }
/* Badge styles */
.badge { display: inline-block; padding: 4px 12px; border-radius: 4px; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }
.badge-watched { background-color: #46D369; color: #000000; }
.badge-unwatched { background-color: var(--primary-red); color: var(--primary-white); }
.stDataFrame { background-color: var(--primary-dark-gray); }
.element-container { margin-bottom: 20px; }
hr { border-color: var(--primary-gray); margin: 30px 0; }
img { border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.6); transition: transform 0.3s ease; }
img:hover { transform: scale(1.05); }
</style>
""", unsafe_allow_html=True)

def validate_session():
    if "user_email" not in st.session_state:
        st.warning("Please login to access your dashboard.")
        st.stop()
    return st.session_state["user_email"]

def star_rating_component(label, current_value=0, max_stars=5, movie_id=None, user_email=None):
    st.markdown("<div class='star-rating'>", unsafe_allow_html=True)
    st.markdown(f"**{label}**")
    cols = st.columns(max_stars + 1)
    for i in range(max_stars):
        star_display = "★" if i < current_value else "☆"
        if cols[i].button(star_display, key=f"star_{movie_id}_{i}_{user_email}"):
            new_rating = i + 1
            res_rate = RatingService.add_or_update_rating(user_email, movie_id, new_rating)
            if res_rate["success"]:
                st.success("Rating saved!")
                st.rerun()
            else:
                st.error(res_rate["error"])
    if current_value > 0:
        cols[max_stars].markdown(f"**{current_value}/5**")
    st.markdown("</div>", unsafe_allow_html=True)
    return current_value

def movie_card(movie, user_email, section_prefix=""):
    with st.container():
        st.markdown("<div class='movie-card'>", unsafe_allow_html=True)
        col1, col2 = st.columns([1, 3])
        with col1:
            if movie.get("poster_path"):
                st.image(movie.get("poster_path"), width=150)
        with col2:
            st.markdown(f"### {movie['title']}")
            rating_col1, rating_col2, rating_col3 = st.columns([1, 1, 2])
            with rating_col1:
                avg_rating = movie.get('avg_rating', movie.get('vote_average', 0))
                st.markdown(f"{avg_rating}/10")
            with rating_col2:
                release_date = movie.get('release_date')
                if release_date:
                    year = release_date.year if hasattr(release_date, 'year') else str(release_date)[:4]
                    st.markdown(year)
            with rating_col3:
                genres_value = movie.get('genres')
                if genres_value:
                    genres_short = genres_value[:30] + "..." if len(genres_value) > 30 else genres_value
                    st.markdown(genres_short)
            overview = movie.get('overview')
            if overview:
                overview_short = overview[:150] + "..." if len(overview) > 150 else overview
                st.markdown(f"<p style='color: #B3B3B3; margin: 10px 0;'>{overview_short}</p>", unsafe_allow_html=True)
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                user_ratings = RatingService.get_user_ratings(user_email)
                existing = next((r["rating"] for r in user_ratings.get("data", []) if r["movieId"] == movie["movieId"]), 0)
                star_rating_component("Your Rating:", int(existing), movie_id=movie['movieId'], user_email=user_email)
            with btn_col2:
                if st.button("Add to Watchlist", key=f"add_{section_prefix}_{movie['movieId']}_{user_email}"):
                    res = WatchlistService.add_to_watchlist(user_email, movie["movieId"], status="not_watched")
                    if res["success"]:
                        st.success("Added to Watchlist!")
                    else:
                        st.error(res["error"])
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("---")

def header_and_stats(user_email):
    st.markdown("<h1 style='text-align: center; margin-bottom: 2rem;'>Your Pixel Experience</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; font-size: 1.2rem; color: #B3B3B3;'>Welcome back, <span style='color: #E50914; font-weight: 700;'>{user_email.split('@')[0]}</span></p>", unsafe_allow_html=True)
    ratings = RatingService.get_user_ratings(user_email)
    watchlist = WatchlistService.get_user_watchlist(user_email)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Ratings Given", len(ratings.get("data", [])))
    with col2:
        st.metric("Watchlist", len(watchlist.get("data", [])))
    with col3:
        if ratings.get("data"):
            avg_rating = sum(r["rating"] for r in ratings["data"]) / len(ratings["data"])
            st.metric("Avg Rating", f"{avg_rating:.1f}/5")
        else:
            st.metric("Avg Rating", "0/5")
    with col4:
        watched_count = len([w for w in watchlist.get("data", []) if w.get("status") == "watched"])
        st.metric("Watched", watched_count)

def trending_section(user_email):
    st.markdown("<h2>Trending Now</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #B3B3B3; margin-bottom: 20px;'>Hot picks everyone's watching</p>", unsafe_allow_html=True)
    res = RecommendationService.get_trending_movies(k=6)
    if res["success"] and res["data"]:
        for movie in res["data"]:
            movie_card(movie, user_email, "trend")
    else:
        st.warning("Could not load trending movies.")

def personalized_recs_section(user_email):
    st.markdown("<h2>Recommended For You</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #B3B3B3; margin-bottom: 20px;'>Based on your viewing history and ratings</p>", unsafe_allow_html=True)
    if "rec_limit" not in st.session_state:
        st.session_state.rec_limit = 8
    limit = st.slider("Number of recommendations", 3, 20, st.session_state.rec_limit, key="rec_slider")
    st.session_state.rec_limit = limit
    res = RecommendationService.get_recommendations_for_user(user_email, k=limit)
    if res["success"] and res["data"]:
        for movie in res["data"]:
            movie_card(movie, user_email, "rec")
    else:
        st.info("Rate a few movies to get personalized recommendations!")

def because_you_watched(user_email):
    st.markdown("<h2>Because You Watched...</h2>", unsafe_allow_html=True)
    top_movies = RatingService.get_user_ratings(user_email)
    if not top_movies["success"] or not top_movies["data"]:
        st.info("Rate some movies to see personalized recommendations based on your favorites!")
        return
    sorted_ratings = sorted(top_movies["data"], key=lambda x: x["rating"], reverse=True)
    if not sorted_ratings:
        st.info("Start rating movies to get recommendations!")
        return
    top_movie = sorted_ratings[0]
    movie_details = MovieService.get_movie_details(top_movie['movieId'])
    if movie_details["success"] and movie_details["data"]:
        movie_title = movie_details['data']['title']
        st.markdown(f"<p style='color: #B3B3B3; margin-bottom: 20px;'>Since you loved <span style='color: #E50914; font-weight: 700;'>{movie_title}</span>, you might enjoy these:</p>", unsafe_allow_html=True)
        res = RecommendationService.get_similar_movies(top_movie["movieId"], k=8)
        if res["success"] and res["data"]:
            for movie in res["data"]:
                movie_card(movie, user_email, "similar")
        else:
            st.warning("No similar movies found at the moment.")
    else:
        st.warning("Could not load movie details.")

def genre_explorer(user_email):
    st.markdown("<h2>Explore by Genre</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #B3B3B3; margin-bottom: 20px;'>Browse movies by your favorite genres</p>", unsafe_allow_html=True)
    genres = ["Action", "Comedy", "Drama", "Romance", "Thriller", "Sci-Fi", "Animation", "Horror", "Fantasy"]
    col1, col2 = st.columns([2, 1])
    with col1:
        selected = st.selectbox("Select a Genre", genres, key="genre_select")
    with col2:
        search_btn = st.button("Show Movies", key="genre_button", use_container_width=True)
    if search_btn:
        st.session_state.current_genre = selected
        st.session_state.show_genre_results = True
    if st.session_state.get("show_genre_results") and st.session_state.get("current_genre"):
        st.markdown(f"<h3>Results for: {st.session_state.current_genre}</h3>", unsafe_allow_html=True)
        res = RecommendationService.get_popular_movies_by_genre(st.session_state.current_genre, k=10)
        if res["success"] and res["data"]:
            for movie in res["data"]:
                movie_card(movie, user_email, "genre")
        else:
            st.warning(f"No movies found in {st.session_state.current_genre} genre.")

def search_movies_section(user_email):
    st.markdown("<h2>Search Movies</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #B3B3B3; margin-bottom: 20px;'>Find your favorite movies</p>", unsafe_allow_html=True)
    if "search_keyword" not in st.session_state:
        st.session_state.search_keyword = ""
    if "search_results" not in st.session_state:
        st.session_state.search_results = None
    col1, col2 = st.columns([3, 1])
    with col1:
        keyword = st.text_input("Enter movie title:",
                                value=st.session_state.search_keyword,
                                key="search_input",
                                placeholder="e.g., Inception, Avatar, Titanic...")
    with col2:
        search_btn = st.button("Search", key="search_button", use_container_width=True)
    if search_btn and keyword:
        st.session_state.search_keyword = keyword
        with st.spinner("Searching..."):
            res = MovieService.search_movies(keyword)
            st.session_state.search_results = res
    if st.session_state.search_results:
        res = st.session_state.search_results
        if res["success"] and res["data"]:
            st.success(f"Found {len(res['data'])} movies")
            for movie in res["data"]:
                movie_card(movie, user_email, "search")
        else:
            st.warning("No results found. Try a different search term.")

def watchlist_section(user_email):
    st.markdown("<h2>My Watchlist</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #B3B3B3; margin-bottom: 20px;'>Manage your saved movies</p>", unsafe_allow_html=True)
    menu = st.radio("Choose Action:", ["View Watchlist", "Add Movie", "Remove Movie"], horizontal=True)
    if menu == "View Watchlist":
        res = WatchlistService.get_user_watchlist(user_email)
        if res["success"] and res["data"]:
            st.success(f"You have {len(res['data'])} movies in your watchlist")
            for movie in res["data"]:
                st.markdown("<div class='movie-card'>", unsafe_allow_html=True)
                col1, col2 = st.columns([1, 3])
                with col1:
                    if movie.get("poster_path"):
                        st.image(movie.get("poster_path"), width=150)
                with col2:
                    st.markdown(f"### {movie['title']}")
                    st.markdown(f"{movie.get('genres', 'N/A')}")
                    status = movie['status']
                    badge_class = "badge-watched" if status == "watched" else "badge-unwatched"
                    badge_text = "WATCHED" if status == "watched" else "TO WATCH"
                    st.markdown(f"<span class='badge {badge_class}'>{badge_text}</span>", unsafe_allow_html=True)
                    st.markdown(f"<p style='color: #B3B3B3;'>Added: {movie.get('added_at', 'N/A')}</p>", unsafe_allow_html=True)
                    col2a, col2b = st.columns(2)
                    with col2a:
                        new_status = st.selectbox("Update status", ["watched", "not_watched"],
                                                 index=0 if movie["status"] == "watched" else 1,
                                                 key=f"status_{movie['movieId']}")
                        if st.button("Update", key=f"update_{movie['movieId']}"):
                            res_update = WatchlistService.update_watch_status(user_email, movie["movieId"], new_status)
                            if res_update["success"]:
                                st.success("Status updated!")
                                st.rerun()
                    with col2b:
                        if st.button("Remove", key=f"remove_{movie['movieId']}"):
                            res_remove = WatchlistService.remove_from_watchlist(user_email, movie["movieId"])
                            if res_remove["success"]:
                                st.success("Movie removed!")
                                st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("---")
        else:
            st.info("Your watchlist is empty. Start adding movies!")
    elif menu == "Add Movie":
        movie_id = st.number_input("Enter Movie ID", min_value=1, step=1)
        status = st.selectbox("Status", ["not_watched", "watched"])
        if st.button("Add to Watchlist", use_container_width=True):
            res = WatchlistService.add_to_watchlist(user_email, movie_id, status)
            if res["success"]:
                st.success("Added to your watchlist!")
            else:
                st.error(res["error"])
    elif menu == "Remove Movie":
        movie_id = st.number_input("Enter Movie ID to Remove", min_value=1, step=1)
        if st.button("Remove from Watchlist", use_container_width=True):
            res = WatchlistService.remove_from_watchlist(user_email, movie_id)
            if res["success"]:
                st.success("Removed successfully!")
            else:
                st.error(res["error"])

def insights_section(user_email):
    st.markdown("<h2>Your Insights</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #B3B3B3; margin-bottom: 20px;'>Your viewing statistics and preferences</p>", unsafe_allow_html=True)
    res = RatingService.get_user_ratings(user_email)
    if res["success"] and res["data"]:
        ratings = [r["rating"] for r in res["data"]]
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("Total Ratings", len(ratings))
        with col2: st.metric("Average Rating", f"{sum(ratings)/len(ratings):.2f}/5")
        with col3: st.metric("Highest Rating", f"{max(ratings)}/5")
        with col4: st.metric("Lowest Rating", f"{min(ratings)}/5")
        st.markdown("---")
        st.markdown("### Rating Distribution")
        st.bar_chart(ratings)
    else:
        st.info("No rating data yet. Start rating movies to see your insights!")

def profile_section(user_email):
    st.markdown("<h2>Edit Profile</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #B3B3B3; margin-bottom: 20px;'>Update your account information</p>", unsafe_allow_html=True)
    with st.form("profile_form"):
        new_name = st.text_input("New Name", placeholder="Enter your full name")
        new_password = st.text_input("New Password", type="password", placeholder="Enter new password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm new password")
        submit = st.form_submit_button("Save Changes", use_container_width=True)
        if submit:
            if new_password and new_password != confirm_password:
                st.error("Passwords do not match!")
            else:
                res = UserService.update_user(
                    email=user_email,
                    new_name=new_name if new_name else None,
                    new_password=new_password if new_password else None
                )
                if res["success"]:
                    st.success("Profile updated successfully!")
                else:
                    st.error(f"{res['error']}")

def user_dashboard():
    user_email = validate_session()
    st.sidebar.markdown("<h2 style='color: #E50914; text-align: center;'>Pixel</h2>", unsafe_allow_html=True)
    st.sidebar.markdown("<p style='text-align: center; color: #B3B3B3; font-size: 0.9rem;'>Movie Recommendation System</p>", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    menu = st.sidebar.radio(
        "Navigate",
        [
            "Home",
            "For You",
            "Because You Watched",
            "Browse Genres",
            "Search",
            "Watchlist",
            "Insights",
            "Profile"
        ],
    )
    if menu == "Home":
        header_and_stats(user_email)
        st.markdown("---")
        trending_section(user_email)
    elif menu == "For You":
        personalized_recs_section(user_email)
    elif menu == "Because You Watched":
        because_you_watched(user_email)
    elif menu == "Browse Genres":
        genre_explorer(user_email)
    elif menu == "Search":
        search_movies_section(user_email)
    elif menu == "Watchlist":
        watchlist_section(user_email)
    elif menu == "Insights":
        insights_section(user_email)
    elif menu == "Profile":
        profile_section(user_email)
