from app.models.movies_data import Movie
from app.models.ratings_data import Rating
import statistics


class MovieService:

    #attach average rating
    @staticmethod
    def _attach_avg_rating(movie: dict) -> dict:
        """Attach average rating (from ratings table, fallback to vote_average)."""
        ratings = Rating.fetch_movie_ratings(movie["movieId"])
        if ratings["success"] and ratings["data"]:
            movie["avg_rating"] = round(statistics.mean(r["rating"] for r in ratings["data"]), 2)
        else:
            movie["avg_rating"] = movie.get("vote_average") or 0
        return movie

    #user features
    @staticmethod
    def search_movies(keyword: str):
        """Search movies by title (with rating aggregation)."""
        res = Movie.search_by_title(keyword)
        if not res["success"]:
            return {"success": False, "error": res["error"]}

        movies = [MovieService._attach_avg_rating(m) for m in res["data"]]
        return {"success": True, "data": movies}

    @staticmethod
    def get_movie_details(movieId: int):
        """Fetch a single movie with ratings included."""
        res = Movie.fetch_by_id(movieId)
        if not res["success"]:
            return {"success": False, "error": res["error"]}
        if not res["data"]:
            return {"success": False, "error": "Movie not found"}

        movie = MovieService._attach_avg_rating(res["data"])
        return {"success": True, "data": movie}

    @staticmethod
    def list_movies(limit=50, offset=0):
        """Fetch all movies with pagination, including avg rating."""
        res = Movie.fetch_all(limit=limit, offset=offset)
        if not res["success"]:
            return {"success": False, "error": res["error"]}

        movies = [MovieService._attach_avg_rating(m) for m in res["data"]]
        return {"success": True, "data": movies}

    @staticmethod
    def get_movies_by_genre(genre: str, limit=20, offset=0):
        """Browse movies by genre (with rating aggregation)."""
        res = Movie.fetch_by_genre(genre, limit=limit, offset=offset)
        if not res["success"]:
            return {"success": False, "error": res["error"]}

        movies = [MovieService._attach_avg_rating(m) for m in res["data"]]
        return {"success": True, "data": movies}

    #admin features
    @staticmethod
    def add_movie(**kwargs):
        """Admin: Add new movie."""
        return Movie.add_movie(**kwargs)

    @staticmethod
    def update_movie(movieId, **kwargs):
        """Admin: Update existing movie."""
        return Movie.update_movie(movieId, **kwargs)

    @staticmethod
    def deactivate_movie(movieId):
        """Admin: Soft delete movie."""
        return Movie.deactivate(movieId)

    @staticmethod
    def activate_movie(movieId):
        """Admin: Reactivate movie."""
        return Movie.activate(movieId)

    @staticmethod
    def delete_movie(movieId):
        """Admin: Permanently delete movie."""
        return Movie.delete_movie(movieId)
