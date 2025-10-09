# setup_database.py
import os, bcrypt
from dotenv import load_dotenv

load_dotenv()

from app.models.users_data import User
from app.models.movies_data import Movie
from app.models.ratings_data import Rating
from app.models.watchlist_data import Watchlist
from app.config.db_connection import connecting_db


DEV_MODE = os.getenv("DEV_MODE", "False").lower() == "true"
ADMIN_EMAIL = os.getenv("DEFAULT_ADMIN_EMAIL")
ADMIN_PW = os.getenv("DEFAULT_ADMIN_PASSWORD")
MOVIES_CSV = "recommend_model/data/processed/movies_with_posters_withId.csv" 
DEMO_RATINGS_CSV = "recommend_model/data/processed/ratings_final_fixed.csv"

def setup_database():
    print("Creating tables...")
    User.create_table()
    Movie.create_table()
    Rating.create_table()
    Watchlist.create_table()
   

    # create default admin (DEV only)
    if DEV_MODE and ADMIN_EMAIL and ADMIN_PW:
        if not User.fetch_by_email(ADMIN_EMAIL):
            hashed = bcrypt.hashpw(ADMIN_PW.encode(), bcrypt.gensalt()).decode()
            admin = User(name="Rakshita Vishwakarma", email=ADMIN_EMAIL, password=hashed, role="admin")
            admin.save()
            print(f"Admin created: {ADMIN_EMAIL}")
        else:
            print("Admin already exists, skipping.")

        # Bulk insert movies (only if CSV exists)
        if os.path.exists(MOVIES_CSV):
            print("Bulk inserting movies (may take a while)...")
            Movie.bulk_insert_from_csv(MOVIES_CSV)
            print("Movies inserted.")
        else:
            print("Movies CSV not found, skipping movie bulk insert.")

    
if __name__ == "__main__":
    setup_database()
