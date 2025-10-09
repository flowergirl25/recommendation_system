from datetime import datetime
from app.config.db_connection import connecting_db
import pymysql.cursors

class Watchlist:
    def __init__(self, user_email, movieId, status="not_watched", added_at=None):
        """Initialize Watchlist entry with user email, movie ID, status, and timestamp."""
        self.user_email = user_email
        self.movieId = movieId
        self.status = status
        self.added_at = added_at if added_at else datetime.now()

    # Table setup
    @staticmethod
    def create_table():
        """Create watchlist table if not exists."""
        try:
            conn = connecting_db()
            cursor = conn.cursor()
            sql = """
            CREATE TABLE IF NOT EXISTS watchlist (
                watchlist_id INT AUTO_INCREMENT PRIMARY KEY,
                user_email VARCHAR(100) NOT NULL,
                movieId INT NOT NULL,
                status ENUM('watched', 'not_watched') DEFAULT 'not_watched',
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE,
                FOREIGN KEY (movieId) REFERENCES movies(movieId) ON DELETE CASCADE,
                UNIQUE (user_email, movieId)  -- prevents duplicates
            )
            """
            cursor.execute(sql)
            conn.commit()
            return {"success": True, "message": "Watchlist table ready in database"}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    # User CRUD
    def save(self):
        """Add movie to user's watchlist, preventing duplicates."""
        try:
            conn = connecting_db()
            cursor = conn.cursor()
            sql = """
            INSERT IGNORE INTO watchlist (user_email, movieId, status, added_at)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (self.user_email, self.movieId, self.status, self.added_at))
            conn.commit()
            return {
                "success": True,
                "message": f"Movie {self.movieId} added to watchlist for {self.user_email} ({self.status})",
            }
        except Exception as e:
            conn.rollback()
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    @staticmethod
    def update_status(user_email, movieId, status):
        """Update watch status for a movie in user's watchlist."""
        try:
            conn = connecting_db()
            cursor = conn.cursor()
            sql = """
            UPDATE watchlist
            SET status=%s, added_at=NOW()
            WHERE user_email=%s AND movieId=%s
            """
            cursor.execute(sql, (status, user_email, movieId))
            conn.commit()
            return {
                "success": True,
                "message": f"Status updated to '{status}' for movie {movieId} (user {user_email})",
            }
        except Exception as e:
            conn.rollback()
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    @staticmethod
    def remove_from_watchlist(user_email, movieId):
        """Remove movie from user's watchlist."""
        try:
            conn = connecting_db()
            cursor = conn.cursor()
            sql = "DELETE FROM watchlist WHERE user_email=%s AND movieId=%s"
            cursor.execute(sql, (user_email, movieId))
            conn.commit()
            return {
                "success": True,
                "message": f"Movie {movieId} removed from watchlist for {user_email}",
            }
        except Exception as e:
            conn.rollback()
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    @staticmethod
    def fetch_user_watchlist(user_email):
        """Get all movies in user's watchlist with movie details + status."""
        try:
            conn = connecting_db()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            sql = """
            SELECT w.watchlist_id, w.status, w.added_at,
                   m.movieId, m.title, m.genres, m.poster_path
            FROM watchlist w
            JOIN movies m ON w.movieId = m.movieId
            WHERE w.user_email=%s
            ORDER BY w.added_at DESC
            """
            cursor.execute(sql, (user_email,))
            results = cursor.fetchall()
            return {"success": True, "data": results}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    # Admin CRUD
    @staticmethod
    def fetch_all():
        """Admin: fetch all watchlists with user + movie details."""
        try:
            conn = connecting_db()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            sql = """
            SELECT w.watchlist_id, w.user_email, w.status, w.added_at,
                   m.movieId, m.title, m.genres, m.poster_path
            FROM watchlist w
            JOIN movies m ON w.movieId = m.movieId
            ORDER BY w.added_at DESC
            """
            cursor.execute(sql)
            results = cursor.fetchall()
            return {"success": True, "data": results}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()
