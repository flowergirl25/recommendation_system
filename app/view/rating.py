from app.models.ratings_data import Rating


class RatingService:

    #user features
    @staticmethod
    def add_or_update_rating(user_email: str, movieId: int, rating: float):
        """Add or update a rating for a movie by a user."""
        try:
            rating_obj = Rating(user_email=user_email, movieId=movieId, rating=rating)
            return rating_obj.save()
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def delete_rating(user_email: str, movieId: int):
        """Delete a user's rating for a movie."""
        try:
            rating_obj = Rating(user_email=user_email, movieId=movieId, rating=0)  # rating ignored
            return rating_obj.delete()
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def get_user_movie_rating(user_email, movieId):
        """Get user's specific rating for a movie."""
        return Rating.fetch_user_movie_rating(user_email, movieId)


    @staticmethod
    def get_user_ratings(user_email: str):
        """Fetch all ratings by a user."""
        return Rating.fetch_user_ratings(user_email)

    @staticmethod
    def get_movie_ratings(movieId: int):
        """Fetch all ratings for a movie."""
        return Rating.fetch_movie_ratings(movieId)

    #admin features
    @staticmethod
    def get_all_ratings():
        """Admin: Fetch all ratings in DB."""
        return Rating.fetch_all()

    @staticmethod
    def delete_rating_by_admin(rating_id: int):
        """Admin: Delete rating by ID."""
        return Rating.delete_by_admin(rating_id)
