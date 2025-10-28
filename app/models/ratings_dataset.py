"""
Handles bulk loading of demo ratings dataset for recommendations.

"""

from app.config.db_connection import connecting_db
import pandas as pd

class DemoRating:
    # Table setup
    @staticmethod
    def create_tables():
        """Create demo_users and demo_ratings tables."""
        try:
            conn = connecting_db()
            cursor = conn.cursor()
            sql_users = """
            CREATE TABLE IF NOT EXISTS demo_users (
                user_id INT PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            sql_ratings = """
            CREATE TABLE IF NOT EXISTS demo_ratings (
                rating_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                movie_id INT NOT NULL,
                rating FLOAT NOT NULL CHECK (rating >= 0.0 AND rating <= 5.0),
                timestamp TIMESTAMP,
                FOREIGN KEY (movie_id) REFERENCES movies(movie_id) ON DELETE CASCADE
            )
            """
            cursor.execute(sql_users)
            cursor.execute(sql_ratings)
            conn.commit()
            return {"success": True, "message": "Demo tables ready in database"}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    # Bulk insert
    @staticmethod
    def bulk_insert_from_csv(csv_path):
        """Insert demo ratings from CSV (one-time setup)."""
        try:
            df = pd.read_csv(csv_path)
            conn = connecting_db()
            cursor = conn.cursor()
            sql_user = "INSERT IGNORE INTO demo_users (user_id) VALUES (%s)"
            sql_rating = """
            INSERT INTO demo_ratings (user_id, movie_id, rating, timestamp)
            VALUES (%s, %s, %s, %s)
            """
            inserted = 0
            for _, row in df.iterrows():
                if not (0.0 <= float(row["rating"]) <= 5.0):
                    continue
                cursor.execute(sql_user, (int(row["userId"]),))
                cursor.execute(sql_rating, (
                    int(row["userId"]),
                    int(row["movieId"]),
                    float(row["rating"]),
                    row["datetime"],
                ))
                inserted += 1
            conn.commit()
            return {"success": True, "message": f"{inserted} demo ratings inserted"}
        except Exception as e:
            conn.rollback()
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    # Admin CRUD
    @staticmethod
    def fetch_all(limit=None, offset=0):
        """Admin fetch all demo ratings with optional pagination."""
        try:
            conn = connecting_db()
            cursor = conn.cursor()
            sql = "SELECT * FROM demo_ratings"
            if limit:
                sql += " LIMIT %s OFFSET %s"
                cursor.execute(sql, (limit, offset))
            else:
                cursor.execute(sql)
            rows = cursor.fetchall()
            return {"success": True, "data": rows}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

