from app.models.watchlist_data import Watchlist


class WatchlistService:

    # user features
    @staticmethod
    def add_to_watchlist(user_email: str, movieId: int, status: str = "not_watched"):
        """Add a movie to the user’s watchlist."""
        try:
            watch = Watchlist(user_email, movieId, status=status)
            return watch.save()
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def remove_from_watchlist(user_email: str, movieId: int):
        """Remove a movie from the user’s watchlist."""
        return Watchlist.remove_from_watchlist(user_email, movieId)

    @staticmethod
    def get_user_watchlist(user_email: str):
        """Fetch all movies in a user’s watchlist with details."""
        return Watchlist.fetch_user_watchlist(user_email)

    @staticmethod
    def update_watch_status(user_email: str, movieId: int, status: str):
        """Update 'watched' / 'not_watched' status for a movie."""
        return Watchlist.update_status(user_email, movieId, status)

    # admin features
    @staticmethod
    def get_all_watchlists():
        """Admin: Fetch all watchlists with user + movie details."""
        return Watchlist.fetch_all()
