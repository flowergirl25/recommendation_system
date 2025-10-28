import streamlit as st
from app.view.rating import RatingService  # fixed import (services, not service)

# Add or update rating view
def add_or_update_rating_view():
    st.subheader("Rate a Movie")

    movieId = st.number_input("Enter Movie ID", min_value=1, step=1)
    watched = st.radio("Have you watched this movie?", ["Yes", "No"], index=1)

    if watched == "Yes":
        rating = st.slider("Your Rating", min_value=0.0, max_value=5.0, step=0.5)
        if st.button("Submit Rating"):
            user_email = st.session_state.get("user_email")
            if not user_email:
                st.error("You must be logged in to rate movies.")
            else:
                res = RatingService.add_or_update_rating(user_email, movieId, rating)
                if res["success"]:
                    st.success(res["message"])
                else:
                    st.error(res["error"])
    else:
        st.info("You can only rate movies after watching them.")

# Delete rating view
def delete_rating_view():
    st.subheader("Delete Your Rating")

    movieId = st.number_input("Enter Movie ID to delete rating", min_value=1, step=1)

    if st.button("Delete Rating"):
        user_email = st.session_state.get("user_email")
        if not user_email:
            st.error("You must be logged in.")
        else:
            res = RatingService.delete_rating(user_email, movieId)
            if res["success"]:
                st.success(res["message"])
            else:
                st.error(res["error"])

# User ratings view
def user_ratings_view():
    st.subheader("My Ratings")
    user_email = st.session_state.get("user_email")
    if not user_email:
        st.error("You must be logged in.")
        return

    res = RatingService.get_user_ratings(user_email)
    if res["success"] and res["data"]:
        for r in res["data"]:
            st.write(f"Movie ID: {r['movieId']} | Rating: {r['rating']} | Timestamp: {r['timestamp']}")
    else:
        st.info("You have not rated any movies yet.")

# Admin ratings view
def admin_ratings_view():
    st.subheader("Admin: Manage Ratings")

    action = st.selectbox("Choose action", ["View All Ratings", "Delete Rating by ID"])

    if action == "View All Ratings":
        res = RatingService.get_all_ratings()
        if res["success"] and res["data"]:
            for r in res["data"]:
                st.write(f"ID: {r['rating_id']} | User: {r['user_email']} | Movie: {r['movieId']} | Rating: {r['rating']}")
        else:
            st.warning("No ratings found.")

    elif action == "Delete Rating by ID":
        rating_id = st.number_input("Enter Rating ID", min_value=1, step=1)
        if st.button("Delete Rating (Admin)"):
            res = RatingService.delete_rating_by_admin(rating_id)
            if res["success"]:
                st.success(res["message"])
            else:
                st.error(res["error"])
