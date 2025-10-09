from app.config.db_connection import connecting_db
import pandas as pd
import pymysql.cursors
from app.utils.logging_decorator import log_call

class Movie:
    # Table setup
    @staticmethod
    def create_table():
        """Create movies table if not exists."""
        try:
            conn = connecting_db()
            cursor = conn.cursor()
            sql = """
            CREATE TABLE IF NOT EXISTS movies (
                movieId INT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                genres VARCHAR(255),
                overview TEXT,
                release_date DATE,
                runtime INT,
                popularity FLOAT,
                vote_average FLOAT,
                vote_count INT,
                language VARCHAR(10) DEFAULT 'en',
                poster_path VARCHAR(500),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """
            cursor.execute(sql)
            conn.commit()
            return {"success": True, "message": "Movies table ready in database"}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    # Bulk insert
    @staticmethod
    def bulk_insert_from_csv(csv_path):
        """Insert multiple movies from CSV; use in setup only."""
        try:
            df = pd.read_csv(csv_path)
            conn = connecting_db()
            cursor = conn.cursor()

            sql = """
            INSERT INTO movies (
                movieId, title, genres, overview, release_date, runtime,
                popularity, vote_average, vote_count, language,
                poster_path, is_active, created_at, updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE, NOW(), NOW())
            """
            for _, row in df.iterrows():
                poster = row.get("poster_path") if pd.notna(row.get("poster_path")) else "https://via.placeholder.com/500x750?text=No+Image"
                cursor.execute(sql, (
                    row.get("movieId"),
                    row.get("title"), row.get("genres"), row.get("overview"), row.get("release_date"), row.get("runtime"),
                    row.get("popularity"), row.get("vote_average"), row.get("vote_count"),
                    row.get("original_language", "en"), poster,
                ))

            conn.commit()
            return {"success": True, "message": f"{len(df)} movies inserted from {csv_path}"}
        except Exception as e:
            conn.rollback()
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    # User CRUD
    @staticmethod
    @log_call(log_args=True, log_result=False)
    def fetch_all(active_only=True, limit=50, offset=0):
        """Fetch all movies (optionally only active). Supports pagination."""
        try:
            conn = connecting_db()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            query = "SELECT * FROM movies"
            if active_only:
                query += " WHERE is_active=TRUE"
            query += " LIMIT %s OFFSET %s"
            cursor.execute(query, (limit, offset))
            movies = cursor.fetchall()
            return {"success": True, "data": movies}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    @staticmethod
    @log_call(log_args=True, log_result=False)
    def fetch_by_id(movie_id):
        """Fetch a movie by ID (MovieLens ID)."""
        try:
            conn = connecting_db()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute("SELECT * FROM movies WHERE movieId=%s", (movie_id,))
            movie = cursor.fetchone()
            return {"success": True, "data": movie}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    @staticmethod
    @log_call(log_args=True, log_result=False)
    def search_by_title(keyword):
        """Search active movies by partial title match."""
        try:
            conn = connecting_db()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            query = "SELECT * FROM movies WHERE title LIKE %s AND is_active=TRUE"
            cursor.execute(query, (f"%{keyword}%",))
            results = cursor.fetchall()
            return {"success": True, "data": results}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    @staticmethod
    @log_call(log_args=True, log_result=False)
    def fetch_by_genre(genre: str, limit=20, offset=0, active_only=True):
        """Fetch movies filtered by genre (supports pagination)."""
        try:
            conn = connecting_db()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            query = "SELECT * FROM movies WHERE genres LIKE %s"
            if active_only:
                query += " AND is_active=TRUE"
            query += " LIMIT %s OFFSET %s"
            cursor.execute(query, (f"%{genre}%", limit, offset))
            movies = cursor.fetchall()
            return {"success": True, "data": movies}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()


    # Admin CRUD
    @staticmethod
    def add_movie(movieId, title, genres=None, overview=None, release_date=None, runtime=None,
                  popularity=None, vote_average=None, vote_count=None,
                  language="en", poster_path=None):
        """Add a single movie manually (admin use)."""
        try:
            conn = connecting_db()
            cursor = conn.cursor()
            if not poster_path:
                poster_path = "https://via.placeholder.com/500x750?text=No+Image"
            sql = """
            INSERT INTO movies (
                movieId, title, genres, overview, release_date, runtime,
                popularity, vote_average, vote_count, language,
                poster_path, is_active, created_at, updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE, NOW(), NOW())
            """
            cursor.execute(sql, (
                movieId, title, genres, overview, release_date, runtime,
                popularity, vote_average, vote_count,
                language, poster_path,
            ))
            conn.commit()
            return {"success": True, "message": f"Movie '{title}' added successfully"}
        except Exception as e:
            conn.rollback()
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    @staticmethod
    def update_movie(movie_id, **kwargs):
        """Update details of an existing movie."""
        if not kwargs:
            return {"success": False, "error": "No fields provided for update"}
        allowed_fields = {
            "title", "genres", "overview", "release_date", "runtime",
            "popularity", "vote_average", "vote_count", "language", "poster_path"
        }
        updates = []
        values = []
        for key, value in kwargs.items():
            if key in allowed_fields:
                updates.append(f"{key}=%s")
                values.append(value)
        if not updates:
            return {"success": False, "error": "No valid fields provided for update"}
        updates.append("updated_at=NOW()")
        values.append(movie_id)
        sql = f"UPDATE movies SET {', '.join(updates)} WHERE movieId=%s"
        try:
            conn = connecting_db()
            cursor = conn.cursor()
            cursor.execute(sql, tuple(values))
            conn.commit()
            return {"success": True, "message": f"Movie {movie_id} updated successfully"}
        except Exception as e:
            conn.rollback()
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    @staticmethod
    def deactivate(movie_id):
        """Soft delete: mark a movie as inactive."""
        try:
            conn = connecting_db()
            cursor = conn.cursor()
            cursor.execute("UPDATE movies SET is_active=FALSE WHERE movieId=%s", (movie_id,))
            conn.commit()
            return {"success": True, "message": f"Movie {movie_id} deactivated"}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    @staticmethod
    def activate(movie_id):
        """Reactivate a previously deactivated movie."""
        try:
            conn = connecting_db()
            cursor = conn.cursor()
            cursor.execute("UPDATE movies SET is_active=TRUE WHERE movieId=%s", (movie_id,))
            conn.commit()
            return {"success": True, "message": f"Movie {movie_id} reactivated"}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    @staticmethod
    def delete_movie(movie_id):
        """Permanently delete a movie from DB."""
        try:
            conn = connecting_db()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM movies WHERE movieId=%s", (movie_id,))
            conn.commit()
            return {"success": True, "message": f"Movie {movie_id} permanently deleted"}
        except Exception as e:
            conn.rollback()
            return {"success": False, "error": str(e)}
        finally:
            conn.close()
