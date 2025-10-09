from datetime import datetime
from app.config.db_connection import connecting_db
import pymysql.cursors
from app.utils.logging_decorator import log_call

class Rating:
    def __init__(self, user_email, movieId, rating, timestamp=None):
        """Initialize Rating; rating must be 0.0 to 5.0."""
        if not (0.0 <= rating <= 5.0):
            raise ValueError("Rating must be between 0.0 and 5.0")
        self.user_email = user_email
        self.movieId = movieId
        self.rating = rating
        self.timestamp = timestamp if timestamp else datetime.now()

    # Table setup
    @staticmethod
    def create_table():
        """Create ratings table if not exists."""
        try:
            conn = connecting_db()
            cursor = conn.cursor()
            sql = """
            CREATE TABLE IF NOT EXISTS ratings (
                rating_id INT AUTO_INCREMENT PRIMARY KEY,
                user_email VARCHAR(100) NOT NULL,
                movieId INT NOT NULL,
                rating FLOAT NOT NULL CHECK (rating >= 0.0 AND rating <= 5.0),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE,
                FOREIGN KEY (movieId) REFERENCES movies(movieId) ON DELETE CASCADE
            )
            """
            cursor.execute(sql)
            conn.commit()
            return {"success": True, "message": "Ratings table ready in database"}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    # User CRUD
    def save(self):
        """Insert or update a rating."""
        try:
            conn = connecting_db()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute(
                "SELECT rating_id FROM ratings WHERE user_email=%s AND movieId=%s",
                (self.user_email, self.movieId),
            )
            existing = cursor.fetchone()
            if existing:
                sql = """
                UPDATE ratings
                SET rating=%s, timestamp=%s
                WHERE rating_id=%s
                """
                cursor.execute(sql, (self.rating, self.timestamp, existing["rating_id"]))
                conn.commit()
                return {"success": True, "message": "Rating updated successfully"}
            else:
                sql = """
                INSERT INTO ratings (user_email, movieId, rating, timestamp)
                VALUES (%s, %s, %s, %s)
                """
                cursor.execute(sql, (self.user_email, self.movieId, self.rating, self.timestamp))
                conn.commit()
                return {"success": True, "message": "New rating added successfully"}
        except Exception as e:
            conn.rollback()
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    @staticmethod
    @log_call(log_args=True, log_result=False)
    def fetch_user_ratings(user_email):
        """Fetch all ratings by a specific user."""
        try:
            conn = connecting_db()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute("SELECT * FROM ratings WHERE user_email=%s", (user_email,))
            return {"success": True, "data": cursor.fetchall()}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    @staticmethod
    @log_call(log_args=True, log_result=False)
    def fetch_movie_ratings(movieId):
        """Fetch all ratings for a specific movie."""
        try:
            conn = connecting_db()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute("SELECT * FROM ratings WHERE movieId=%s", (movieId,))
            return {"success": True, "data": cursor.fetchall()}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    @staticmethod
    @log_call(log_args=True, log_result=False)
    def fetch_user_movie_rating(user_email, movieId):
        """Fetch a user's rating for a specific movie."""
        try:
            conn = connecting_db()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute(
                "SELECT rating FROM ratings WHERE user_email=%s AND movieId=%s",
                (user_email, movieId)
            )
            result = cursor.fetchone()
            return {"success": True, "data": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()


    def delete(self):
        """User deletes their own rating."""
        try:
            conn = connecting_db()
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM ratings WHERE user_email=%s AND movieId=%s",
                (self.user_email, self.movieId),
            )
            conn.commit()
            return {"success": True, "message": "Rating deleted successfully"}
        except Exception as e:
            conn.rollback()
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    # Admin CRUD
    @staticmethod
    def fetch_all():
        """Admin fetch all ratings."""
        try:
            conn = connecting_db()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute("SELECT * FROM ratings")
            return {"success": True, "data": cursor.fetchall()}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    @staticmethod
    def delete_by_admin(rating_id):
        """Admin deletes a rating by ID."""
        try:
            conn = connecting_db()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM ratings WHERE rating_id=%s", (rating_id,))
            conn.commit()
            return {"success": True, "message": f"Rating {rating_id} deleted by admin"}
        except Exception as e:
            conn.rollback()
            return {"success": False, "error": str(e)}
        finally:
            conn.close()
