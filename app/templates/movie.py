import streamlit as st
from app.view.movie import MovieService
from app.view.recommendation import RecommendationService
from app.view.rating import RatingService
from app.view.watchlist import WatchlistService

# Star rating component
def star_rating_component(label, current_value=0, max_stars=5, key_prefix="rating"):
    st.markdown(f"**{label}**")
    cols = st.columns(max_stars)
    selected = st.session_state.get(key_prefix, current_value)

    for i in range(max_stars):
        if cols[i].button("★" if i < selected else "☆", key=f"{key_prefix}_{i}"):
            selected = i + 1
            st.session_state[key_prefix] = selected

    return st.session_state.get(key_prefix, current_value)

# Watchlist button
def add_to_watchlist_button(user_email, movie):
    if st.button(f"Add '{movie['title']}' to Watchlist", key=f"add_{movie['movieId']}_{user_email}"):
        res = WatchlistService.add_to_watchlist(user_email, movie["movieId"], status="not_watched")
        if res["success"]:
            st.success("Added to Watchlist!")
        else:
            st.error(res["error"])

# Search movies view
def search_movies_view():
    st.subheader("Search Movies")
    keyword = st.text_input("Enter movie title")

    if st.button("Search"):
        res = MovieService.search_movies(keyword)
        if res["success"] and res["data"]:
            user_email = st.session_state.get("user_email")
            for movie in res["data"]:
                st.image(movie.get("poster_path"), width=120)
                st.write(movie['title'])
                st.write(f"Avg Rating: {movie.get('avg_rating', 0)}")
                st.write(f"Release Date: {movie.get('release_date', 'N/A')}")
                if user_email:
                    user_ratings = RatingService.get_user_ratings(user_email)
                    existing = next((r["rating"] for r in user_ratings.get("data", [])
                                    if r["movieId"] == movie["movieId"]), 0)
                    new_rating = star_rating_component(
                        f"Rate '{movie['title']}'",
                        int(existing),
                        key_prefix=f"search_{movie['movieId']}_{user_email}",
                    )
                    if new_rating and new_rating != int(existing):
                        res_rate = RatingService.add_or_update_rating(user_email, movie["movieId"], new_rating)
                        if res_rate["success"]:
                            st.success("Rating saved!")
                        else:
                            st.error(res_rate["error"])
                    add_to_watchlist_button(user_email, movie)
                else:
                    st.info("Login to rate or add to watchlist.")
                st.markdown("---")
        else:
            st.warning(res.get("error", "No movies found."))

# Movie details view
def movie_details_view():
    st.subheader("Movie Details")
    movieId = st.number_input("Enter movie ID", min_value=1, step=1)

    if st.button("Get Details"):
        res = MovieService.get_movie_details(movieId)
        if res["success"]:
            movie = res["data"]
            user_email = st.session_state.get("user_email")
            st.image(movie.get("poster_path"), width=150)
            st.write(f"**Title:** {movie['title']}")
            st.write(f"**Average Rating:** {movie.get('avg_rating', 0)}")
            st.write(f"**Release Date:** {movie.get('release_date', 'N/A')}")
            st.write(f"**Overview:** {movie.get('overview', 'No overview available.')}")
            st.markdown("---")
            st.subheader("Rate This Movie")
            if user_email:
                user_ratings = RatingService.get_user_ratings(user_email)
                existing = next((r["rating"] for r in user_ratings.get("data", [])
                                 if r["movieId"] == movie["movieId"]), 0)
                new_rating = star_rating_component(
                    "Your Rating:",
                    int(existing),
                    key_prefix=f"details_{movie['movieId']}_{user_email}",
                )
                if new_rating and new_rating != int(existing):
                    res_rate = RatingService.add_or_update_rating(user_email, movie["movieId"], new_rating)
                    if res_rate["success"]:
                        st.success("Rating updated!")
                    else:
                        st.error(res_rate["error"])
                add_to_watchlist_button(user_email, movie)
            else:
                st.info("Please login to rate or add to watchlist.")

            st.markdown("---")
            st.subheader("Similar Movies")
            sim = RecommendationService.get_similar_movies(movie["movieId"], k=6)
            if sim["success"] and sim["data"]:
                cols = st.columns(3)
                for i, sm in enumerate(sim["data"]):
                    with cols[i % 3]:
                        st.image(sm.get("poster_path"), width=120)
                        st.caption(sm["title"])
            else:
                st.info(sim.get("error", "No similar movies found."))
        else:
            st.error(res.get("error", "Movie not found."))

    st.markdown("---")
    if st.button("Go to Recommendation Page"):
        st.switch_page("app/templates/recommendation_template.py")

# List movies view
def list_movies_view():
    st.subheader("All Movies")
    limit = st.slider("Movies per page", min_value=5, max_value=50, value=10)
    offset = st.number_input("Offset", min_value=0, step=limit)

    if st.button("Load Movies"):
        res = MovieService.list_movies(limit=limit, offset=offset)
        if res["success"] and res["data"]:
            user_email = st.session_state.get("user_email")
            for movie in res["data"]:
                st.image(movie.get("poster_path"), width=120)
                st.write(f"{movie['title']}  Avg Rating: {movie.get('avg_rating', 0)}")
                if user_email:
                    add_to_watchlist_button(user_email, movie)
                st.markdown("---")
        else:
            st.warning(res.get("error", "No movies found."))

# Browse by genre view
def browse_movies_by_genre_view():
    st.subheader("Browse Movies by Genre")
    genres = ["Action", "Comedy", "Drama", "Romance", "Thriller", "Sci-Fi", "Animation", "Horror", "Fantasy"]
    selected = st.selectbox("Choose a Genre", genres)

    if st.button("Show Movies"):
        res = MovieService.get_movies_by_genre(selected, limit=20)
        if res["success"] and res["data"]:
            user_email = st.session_state.get("user_email")
            for movie in res["data"]:
                st.image(movie.get("poster_path"), width=120)
                st.write(f"{movie['title']}  Avg Rating: {movie.get('avg_rating', 0)}")
                st.write(f"Genres: {movie.get('genres', 'N/A')}")
                if user_email:
                    add_to_watchlist_button(user_email, movie)
                st.markdown("---")
        else:
            st.warning(f"No movies found for genre: {selected}")

# Admin movie management view
def admin_movie_view():
    st.subheader("Admin: Manage Movies")
    action = st.selectbox("Choose action", ["Add", "Update", "Deactivate", "Activate", "Delete"])

    if action == "Add":
        with st.form("add_movie_form"):
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
            field = st.text_input("Field to update (e.g. title, overview)")
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
                st.success(res["message"])
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

    elif action == "Delete":
        movieId = st.number_input("Movie ID", min_value=1, step=1)
        if st.button("Delete Movie"):
            res = MovieService.delete_movie(movieId)
            if res["success"]:
                st.success(res["message"])
            else:
                st.error(res["error"])
