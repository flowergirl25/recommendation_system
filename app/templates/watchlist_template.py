import streamlit as st
from app.view.watchlist_view import WatchlistService
from app.view.movie_view import MovieService


# -------------------- Helper --------------------
def validate_session():
    """Ensure the user is logged in before performing any watchlist action."""
    if "user_email" not in st.session_state:
        st.warning("⚠️ Please login to access your watchlist.")
        st.stop()
    return st.session_state["user_email"]


# -------------------- Main User Watchlist --------------------
def user_watchlist_view():
    """Unified view for managing user watchlist."""
    st.subheader("🎬 My Watchlist Manager")

    user_email = validate_session()

    menu = st.radio(
        "Choose Action:",
        ["📄 View My Watchlist", "➕ Add Movie", "🔄 Update Status", "🗑️ Remove Movie"],
        horizontal=True,
    )

    # -------------------- View Watchlist --------------------
    if menu == "📄 View My Watchlist":
        res = WatchlistService.get_user_watchlist(user_email)
        if res["success"] and res["data"]:
            st.success(f"Found {len(res['data'])} movies in your watchlist.")
            for movie in res["data"]:
                st.image(movie.get("poster_path"), width=120)
                st.write(f"🎬 **{movie['title']}** ({movie.get('genres', 'N/A')})")
                st.write(f"📌 **Status:** {'✅ Watched' if movie['status'] == 'watched' else '🕒 To Watch'}")
                st.write(f"🕒 **Added:** {movie.get('added_at', 'N/A')}")
                st.markdown("---")

                # 🔄 Update status directly here
                new_status = st.selectbox(
                    f"Change status for '{movie['title']}'",
                    ["watched", "not_watched"],
                    index=0 if movie["status"] == "watched" else 1,
                    key=f"status_{movie['movieId']}",
                )
                if st.button(f"Update '{movie['title']}'", key=f"update_{movie['movieId']}"):
                    res_update = WatchlistService.update_watch_status(user_email, movie["movieId"], new_status)
                    if res_update["success"]:
                        st.success("✅ Status updated successfully!")
                    else:
                        st.error(res_update["error"])

                # 🗑️ Remove button
                if st.button(f"Remove '{movie['title']}'", key=f"remove_{movie['movieId']}"):
                    res_remove = WatchlistService.remove_from_watchlist(user_email, movie["movieId"])
                    if res_remove["success"]:
                        st.success("🗑️ Movie removed from watchlist!")
                        st.rerun()
                    else:
                        st.error(res_remove["error"])
                st.markdown("---")
        else:
            st.info("You have no movies in your watchlist yet.")

    # -------------------- Add to Watchlist --------------------
    elif menu == "➕ Add Movie":
        movie_id = st.number_input("🎥 Enter Movie ID", min_value=1, step=1)
        status = st.selectbox("📌 Status", ["not_watched", "watched"])

        if st.button("Add Movie to Watchlist"):
            res = WatchlistService.add_to_watchlist(user_email, movie_id, status)
            if res["success"]:
                st.success("✅ Movie added to your watchlist!")
            else:
                st.error(res["error"])

    # -------------------- Update Watch Status --------------------
    elif menu == "🔄 Update Status":
        movie_id = st.number_input("🎬 Enter Movie ID", min_value=1, step=1)
        new_status = st.selectbox("New Status", ["watched", "not_watched"])
        if st.button("Update Status"):
            res = WatchlistService.update_watch_status(user_email, movie_id, new_status)
            if res["success"]:
                st.success("✅ Watch status updated!")
            else:
                st.error(res["error"])

    # -------------------- Remove Movie --------------------
    elif menu == "🗑️ Remove Movie":
        movie_id = st.number_input("Enter Movie ID to Remove", min_value=1, step=1)
        if st.button("Remove Movie"):
            res = WatchlistService.remove_from_watchlist(user_email, movie_id)
            if res["success"]:
                st.success("🗑️ Movie removed successfully!")
            else:
                st.error(res["error"])


# -------------------- Admin Watchlist --------------------
def admin_watchlist_view():
    """Admin dashboard: view all user watchlists."""
    st.subheader("🛠️ Admin: View All Watchlists")

    if st.button("Fetch All Watchlists"):
        res = WatchlistService.get_all_watchlists()
        if res["success"] and res["data"]:
            st.success(f"Found {len(res['data'])} entries in total.")
            for wl in res["data"]:
                st.write(
                    f"👤 {wl['user_email']} | 🎬 {wl['title']} | 📌 {wl['status']} | 🕒 {wl['added_at']}"
                )
        else:
            st.warning("No watchlist entries found.")
