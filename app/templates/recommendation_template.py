import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from app.view.recommendation_view import RecommendationService

def recommendation_view(user_email):
    """Display all recommendation sections for the logged-in user."""
    st.title("Movie Recommendations")

    # Personalized Recommendations
    st.subheader("Recommended for You")
    recs = RecommendationService.get_recommendations_for_user(user_email, k=8)
    if recs["success"] and recs["data"]:
        cols = st.columns(4)
        for i, movie in enumerate(recs["data"]):
            with cols[i % 4]:
                st.image(movie.get("poster_path"), width=130)
                st.caption(movie['title'])
                st.write(f"Average Rating: {movie.get('vote_average', 0)}")
    else:
        st.info(recs.get("error", "No personalized recommendations available."))

    st.markdown("---")

    # Similar Movies Section
    st.subheader("Find Similar Movies")
    movie_id = st.text_input("Enter Movie ID")
    if st.button("Get Similar Movies"):
        if movie_id.strip():
            sim = RecommendationService.get_similar_movies(int(movie_id), k=6)
            if sim["success"] and sim["data"]:
                cols = st.columns(3)
                for i, m in enumerate(sim["data"]):
                    with cols[i % 3]:
                        st.image(m.get("poster_path"), width=120)
                        st.caption(m["title"])
            else:
                st.info(sim.get("error", "No similar movies found."))
        else:
            st.warning("Please enter a valid movie ID.")

    st.markdown("---")

    # Popular Movies Section
    st.subheader("Popular Picks")
    popular = RecommendationService.get_popular_movies(k=8)
    if popular["success"] and popular["data"]:
        cols = st.columns(4)
        for i, m in enumerate(popular["data"]):
            with cols[i % 4]:
                st.image(m.get("poster_path"), width=130)
                st.caption(m['title'])
                st.write(f"Average Rating: {m.get('vote_average', 0)}")
    else:
        st.info(popular.get("error", "No popular movies found."))

    st.markdown("---")

    # Trending Movies Section
    st.subheader("Trending Now")
    trending = RecommendationService.get_trending_movies(k=8)
    if trending["success"] and trending["data"]:
        cols = st.columns(4)
        for i, m in enumerate(trending["data"]):
            with cols[i % 4]:
                st.image(m.get("poster_path"), width=130)
                st.caption(f"{m['title']} ({m.get('release_date', 'N/A')})")
    else:
        st.info(trending.get("error", "No trending movies found."))

    st.markdown("---")

    # Genre-Based Recommendation Section
    st.subheader("Genre-Based Recommendations")
    genre = st.selectbox(
        "Choose a genre:",
        ["Action", "Comedy", "Drama", "Romance", "Thriller", "Sci-Fi", "Horror", "Animation", "Fantasy"]
    )
    if st.button("Show Genre Recommendations"):
        genre_recs = RecommendationService.get_recommendations_by_genre(user_email, genre, k=8)
        if genre_recs["success"] and genre_recs["data"]:
            cols = st.columns(4)
            for i, m in enumerate(genre_recs["data"]):
                with cols[i % 4]:
                    st.image(m.get("poster_path"), width=130)
                    st.caption(m['title'])
                    st.write(f"Average Rating: {m.get('vote_average', 0)}")
        else:
            st.info(genre_recs.get("error", f"No movies found for genre: {genre}."))

    st.markdown("---")

    # Analytics Dashboard (Admin Only)
    st.subheader("Analytics Dashboard (Admin Only)")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Top Rated Movies**")
        top = RecommendationService.get_top_rated_movies(k=5)
        if top["success"]:
            for t in top["data"]:
                st.write(f"{t['title']} — Average Rating: {round(t['avg_rating'], 2)}   ({t['total_ratings']} ratings)")
        else:
            st.warning(top.get("error", "Unable to get top rated movies."))

    with col2:
        st.markdown("**Most Active Users**")
        active = RecommendationService.get_most_active_users(k=5)
        if active["success"]:
            for a in active["data"]:
                st.write(f"{a['email']} — {a['rating_count']} ratings")
        else:
            st.warning(active.get("error", "Unable to get most active users."))

    st.markdown("---")

    st.markdown("**Rating Distribution**")
    dist = RecommendationService.get_rating_distribution()
    if dist["success"] and dist["data"]:
        df = pd.DataFrame(dist["data"])
        fig, ax = plt.subplots()
        ax.bar(df["rating"], df["count"])
        ax.set_xlabel("Rating")
        ax.set_ylabel("Count")
        ax.set_title("Rating Distribution")
        st.pyplot(fig)
    else:
        st.info("No rating data available for distribution.")
