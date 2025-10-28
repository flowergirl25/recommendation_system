import pandas as pd
import numpy as np
import pickle
import pymysql
from app.config.db_connection import connecting_db
from app.models.movies_data import Movie
from app.models.ratings_data import Rating
import datetime


class RecommendationService:
    _similarity_matrix = None 

    @staticmethod
    def _load_similarity_matrix():
        """Load and cache collaborative filtering similarity matrix."""
        if RecommendationService._similarity_matrix is None:
            with open(r"D:\movie_recommendation_system\recommend_model\trained_models\item_similarity.pkl", "rb") as f:
                RecommendationService._similarity_matrix = pickle.load(f)
        return RecommendationService._similarity_matrix

    @staticmethod
    def _fetch_movie_details(movieIds):
        """Fetch movies from DB for given list of IDs."""
        movies = []
        for mid in movieIds:
            res = Movie.fetch_by_id(mid)
            if res["success"] and res["data"]:
                movie = res["data"]
                if "movieId" in movie:
                    try:
                        movie["movieId"] = int(movie["movieId"])
                    except Exception:
                        pass
                movies.append(movie)
        return movies

    @staticmethod
    def get_recommendations_for_user(user_email, k=10):
        """
        Generate personalized recommendations for a user.
        Uses collaborative filtering (item-item similarity).
        Fallback: popular movies for new users.
        """
        conn = None
        try:
            conn = connecting_db()
            cursor = conn.cursor(pymysql.cursors.DictCursor)

            #check if user exists
            cursor.execute("SELECT email FROM users WHERE email=%s", (user_email,))


            #get all ratings by user
            cursor.execute("SELECT movieId, rating FROM ratings WHERE user_email=%s", (user_email,))
            user_ratings = cursor.fetchall()
            if not user_ratings or len(user_ratings) < 3:
                #cold start or few ratings
                return RecommendationService.get_popular_movies(k=k)

            similarity_matrix = RecommendationService._load_similarity_matrix()
            user_df = pd.DataFrame(user_ratings)

            #Predict unseen movies
            movie_scores = {}
            for _, row in user_df.iterrows():
                movieId, rating = row["movieId"], row["rating"]
                
                try:
                    if movieId in similarity_matrix.index:
                        sims = similarity_matrix[movieId].dropna()
                        for sim_movie, sim_score in sims.items():
                            if sim_movie not in user_df["movieId"].values:
                                movie_scores[sim_movie] = movie_scores.get(sim_movie, 0) + sim_score * rating
                except Exception:
                    # skip movies not present in similarity matrix
                    continue

            if not movie_scores:
                return RecommendationService.get_popular_movies(k=k)

            #Sort by score and fetch details
            top_movies = sorted(movie_scores.items(), key=lambda x: x[1], reverse=True)[:k]
            movieIds = [m[0] for m in top_movies]

            return {"success": True, "data": RecommendationService._fetch_movie_details(movieIds)}

        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            if conn:
                conn.close()

    @staticmethod
    def get_similar_movies(movieId, k=10):
        """Return top K similar movies using similarity matrix."""
        try:
            similarity_matrix = RecommendationService._load_similarity_matrix()
            if movieId not in similarity_matrix.index:
                return {"success": False, "error": "Movie not found in similarity model"}

            similar_movies = similarity_matrix[movieId].sort_values(ascending=False).head(k).index.tolist()
            data = RecommendationService._fetch_movie_details(similar_movies)
            return {"success": True, "data": data}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def get_popular_movies(k=10):
        """Fetch top movies based on weighted popularity score (IMDB formula)."""
        conn = None
        try:
            conn = connecting_db()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute("SELECT * FROM movies WHERE is_active=TRUE")
            movies = cursor.fetchall()

            if not movies:
                return {"success": False, "error": "No movies found"}

            df = pd.DataFrame(movies)

            # ensure numeric movieId
            if "movieId" in df.columns:
                try:
                    df["movieId"] = df["movieId"].astype(int)
                except Exception:
                    pass

            # fill missing numerical fields if any
            if "vote_average" not in df.columns:
                df["vote_average"] = 0.0
            if "vote_count" not in df.columns:
                df["vote_count"] = 0

            C = df["vote_average"].mean() if not df["vote_average"].isna().all() else 0
            m = df["vote_count"].quantile(0.80) if "vote_count" in df.columns else 0
            # avoid division by zero
            def pop_score(x):
                try:
                    return ((x["vote_count"] / (x["vote_count"] + m) * x["vote_average"]) +
                            (m / (m + x["vote_count"]) * C))
                except Exception:
                    return 0

            df["popularity_score"] = df.apply(pop_score, axis=1)
            top_movies = df.sort_values("popularity_score", ascending=False).head(k)

            # ensure records have expected types (esp. movieId)
            results = top_movies.to_dict(orient="records")
            for r in results:
                if "movieId" in r:
                    try:
                        r["movieId"] = int(r["movieId"])
                    except Exception:
                        pass
            return {"success": True, "data": results}

        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            if conn:
                conn.close()

    @staticmethod
    def get_trending_movies(k=10):
        """
        Fetch trending movies — recent releases.
        Fallback: use popularity score if release_date invalid/missing.
        """
        conn = None
        try:
            conn = connecting_db()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute("SELECT * FROM movies WHERE is_active=TRUE")
            movies = cursor.fetchall()

            df = pd.DataFrame(movies)
            # Fallback if release_date is missing
            if "release_date" not in df.columns or df["release_date"].isna().all():
                return RecommendationService.get_popular_movies(k=k)

            # Handle missing/invalid dates
            def safe_date(x):
                try:
                    return pd.to_datetime(x)
                except Exception:
                    return pd.NaT

            df["release_date"] = df["release_date"].apply(safe_date)
            df = df.dropna(subset=["release_date"])
            if df.empty:
                return RecommendationService.get_popular_movies(k=k)

            # ensure numeric movieId
            if "movieId" in df.columns:
                try:
                    df["movieId"] = df["movieId"].astype(int)
                except Exception:
                    pass

            df = df.sort_values("release_date", ascending=False)
            results = df.head(k).to_dict(orient="records")
            for r in results:
                if "movieId" in r:
                    try:
                        r["movieId"] = int(r["movieId"])
                    except Exception:
                        pass
            return {"success": True, "data": results}

        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            if conn:
                conn.close()

    #genre-based recommendations
    @staticmethod
    def get_recommendations_by_genre(user_email, genre, k=10):
        """Recommend movies within a specific genre (filtering collaborative results)."""
        recs = RecommendationService.get_recommendations_for_user(user_email, k=50)
        if not recs["success"]:
            return recs

        filtered = [m for m in recs["data"] if genre.lower() in (m.get("genres") or "").lower()]
        return {"success": True, "data": filtered[:k]}

    @staticmethod
    def get_popular_movies_by_genre(genre, k=10):
        """Fetch popular movies only within a given genre."""
        conn = None
        try:
            conn = connecting_db()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            query = """
                SELECT * FROM movies 
                WHERE is_active=TRUE AND genres LIKE %s
            """
            cursor.execute(query, (f"%{genre}%",))
            movies = cursor.fetchall()
            if not movies:
                return {"success": False, "error": "No movies found for this genre"}

            df = pd.DataFrame(movies)
            if "movieId" in df.columns:
                try:
                    df["movieId"] = df["movieId"].astype(int)
                except Exception:
                    pass

            C = df["vote_average"].mean() if "vote_average" in df.columns else 0
            m = df["vote_count"].quantile(0.80) if "vote_count" in df.columns else 0
            def pop_score(x):
                try:
                    return ((x["vote_count"] / (x["vote_count"] + m) * x["vote_average"]) +
                            (m / (m + x["vote_count"]) * C))
                except Exception:
                    return 0

            df["popularity_score"] = df.apply(pop_score, axis=1)
            top_movies = df.sort_values("popularity_score", ascending=False).head(k)
            results = top_movies.to_dict(orient="records")
            for r in results:
                if "movieId" in r:
                    try:
                        r["movieId"] = int(r["movieId"])
                    except Exception:
                        pass
            return {"success": True, "data": results}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            if conn:
                conn.close()

    #admin analytics features
    @staticmethod
    def get_user_rating_history(user_email):
        """Fetch all movies rated by a user (for admin/user dashboard)."""
        conn = None
        try:
            conn = connecting_db()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            query = """
                SELECT r.movieId, m.title, r.rating, m.genres, m.release_date
                FROM ratings r
                JOIN users u ON r.user_email = u.email
                JOIN movies m ON r.movieId = m.movieId
                WHERE u.email = %s
                ORDER BY r.rating DESC
            """
            cursor.execute(query, (user_email,))
            rows = cursor.fetchall()
            return {"success": True, "data": rows}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            if conn:
                conn.close()

    @staticmethod
    def get_top_rated_movies(k=10):
        """Return top-rated movies globally (avg rating)."""
        conn = None
        try:
            conn = connecting_db()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            query = """
                SELECT m.movieId, m.title, AVG(r.rating) as avg_rating, COUNT(r.rating) as total_ratings
                FROM ratings r
                JOIN movies m ON r.movieId = m.movieId
                GROUP BY m.movieId, m.title
                HAVING total_ratings > 5
                ORDER BY avg_rating DESC
                LIMIT %s
            """
            cursor.execute(query, (k,))
            return {"success": True, "data": cursor.fetchall()}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            if conn:
                conn.close()

    @staticmethod
    def get_most_active_users(k=10):
        """Return users who rated the most movies."""
        conn = None
        try:
            conn = connecting_db()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            query = """
                SELECT u.email, COUNT(r.rating) as rating_count
                FROM ratings r
                JOIN users u ON r.user_email = u.email
                GROUP BY u.email
                ORDER BY rating_count DESC
                LIMIT %s
            """
            cursor.execute(query, (k,))
            return {"success": True, "data": cursor.fetchall()}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            if conn:
                conn.close()

    @staticmethod
    def get_rating_distribution():
        """Return distribution of all ratings (for histogram in dashboard)."""
        conn = None
        try:
            conn = connecting_db()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute("SELECT rating, COUNT(*) as count FROM ratings GROUP BY rating ORDER BY rating ASC")
            return {"success": True, "data": cursor.fetchall()}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            if conn:
                conn.close()
