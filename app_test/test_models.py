import pytest
import os
from datetime import datetime
from app.models.users_data import User
from app.models.movies_data import Movie
from app.models.ratings_data import Rating
from app.models.watchlist_data import Watchlist


# Test fixtures with unique identifiers to avoid conflicts
@pytest.fixture(scope="function")  # Changed to function scope to avoid conflicts
def sample_user():
    """Create a unique test user for each test"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return User(
        name="Test User",
        email=f"testuser_{timestamp}@example.com",  # Unique email
        password="hashed_pwd",
        role="user"
    )

@pytest.fixture(scope="function")  # Changed to function scope
def sample_movie():
    """Create a unique test movie for each test"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return {
        "title": f"Test Movie {timestamp}",  # Unique title
        "genres": "Drama",
        "overview": "Overview of test movie",
        "release_date": "2025-01-01",
        "runtime": 120,
        "popularity": 9.0,
        "vote_average": 8.5,
        "vote_count": 100,
        "language": "en",
        "poster_path": "https://via.placeholder.com/500x750?text=Test"
    }

def test_user_crud(sample_user):
    """Test user CRUD operations with proper cleanup"""
    try:
        # Check if user already exists and clean up
        existing_user = User.fetch_by_email(sample_user.email)
        if existing_user:
            User.deactivate(sample_user.email)  # Cleanup existing user
            
        # Test save (create)
        sample_user.save()
        user = User.fetch_by_email(sample_user.email)
        assert user is not None, "User should be created"
        assert user["email"] == sample_user.email, "Email should match"
        
        # Test update
        User.update_profile(sample_user.email, name="Updated User")
        updated = User.fetch_by_email(sample_user.email)
        assert updated["name"] == "Updated User", "Name should be updated"
        
        # Test deactivate
        User.deactivate(sample_user.email)
        deactivated = User.fetch_by_email(sample_user.email)
        assert deactivated["is_active"] == 0, "User should be deactivated"
        
        # Test reactivate
        User.activate(sample_user.email)
        reactivated = User.fetch_by_email(sample_user.email)
        assert reactivated["is_active"] == 1, "User should be reactivated"
        
    finally:
        # Cleanup: deactivate the test user
        try:
            User.deactivate(sample_user.email)
        except:
            pass  # Ignore cleanup errors

def test_movie_crud(sample_movie):
    """Test movie CRUD operations with proper error handling"""
    movie_id = None
    try:
        # Test add movie
        add_result = Movie.add_movie(**sample_movie)
        assert add_result["success"], f"Failed to add movie: {add_result.get('error')}"
        
        # Search for the created movie
        movies = Movie.search_by_title(sample_movie["title"])
        assert movies["success"], f"Failed to search movies: {movies.get('error')}"
        assert len(movies["data"]) > 0, "No movies found in search results"
        
        movie_id = movies["data"][0]["movie_id"]
        
        # Test update movie
        update_result = Movie.update_movie(movie_id, title="Updated Movie Title")
        assert update_result["success"], f"Failed to update movie: {update_result.get('error')}"
        
        # Fetch updated movie - Fix: Access data properly
        updated_result = Movie.fetch_by_id(movie_id)
        assert updated_result["success"], f"Failed to fetch movie: {updated_result.get('error')}"
        assert updated_result["data"] is not None, "Movie data should not be None"
        # Fix: Access title from data dict
        assert updated_result["data"]["title"] == "Updated Movie Title", f"Title not updated correctly: {updated_result['data']['title']}"
        
        # Test deactivate
        deactivate_result = Movie.deactivate(movie_id)
        assert deactivate_result["success"], f"Failed to deactivate movie: {deactivate_result.get('error')}"
        
        inactive_result = Movie.fetch_by_id(movie_id)
        assert inactive_result["success"], f"Failed to fetch inactive movie: {inactive_result.get('error')}"
        assert inactive_result["data"]["is_active"] == 0, "Movie should be deactivated"
        
        # Test reactivate
        activate_result = Movie.activate(movie_id)
        assert activate_result["success"], f"Failed to reactivate movie: {activate_result.get('error')}"
        
        active_result = Movie.fetch_by_id(movie_id)
        assert active_result["success"], f"Failed to fetch reactivated movie: {active_result.get('error')}"
        assert active_result["data"]["is_active"] == 1, "Movie should be reactivated"
        
    finally:
        # Cleanup: delete the test movie
        if movie_id:
            try:
                Movie.delete_movie(movie_id)
            except:
                pass  # Ignore cleanup errors

def test_rating_crud(sample_user, sample_movie):
    """Test rating CRUD operations with dependencies"""
    movie_id = None
    try:
        # First ensure user exists
        sample_user.save()
        
        # Add movie first
        add_result = Movie.add_movie(**sample_movie)
        assert add_result["success"], f"Failed to add movie: {add_result.get('error')}"
        
        # Get the movie ID
        movies = Movie.search_by_title(sample_movie["title"])
        assert movies["success"] and len(movies["data"]) > 0, "Movie should be found"
        movie_id = movies["data"][0]["movie_id"]
        
        # Test create rating
        rating = Rating(user_email=sample_user.email, movie_id=movie_id, rating=4.0)
        res1 = rating.save()
        assert res1["success"], f"Failed to save rating: {res1.get('error')}"
        
        # Test update rating (save again with different rating)
        rating.rating = 5.0
        res2 = rating.save()
        assert res2["success"], f"Failed to update rating: {res2.get('error')}"
        
        # Test fetch user ratings
        user_ratings = Rating.fetch_user_ratings(sample_user.email)
        assert user_ratings["success"], f"Failed to fetch user ratings: {user_ratings.get('error')}"
        assert len(user_ratings["data"]) > 0, "Should have user ratings"
        
        # Test fetch movie ratings
        movie_ratings = Rating.fetch_movie_ratings(movie_id)
        assert movie_ratings["success"], f"Failed to fetch movie ratings: {movie_ratings.get('error')}"
        assert len(movie_ratings["data"]) > 0, "Should have movie ratings"
        
        # Test delete rating
        res3 = rating.delete()
        assert res3["success"], f"Failed to delete rating: {res3.get('error')}"
        
    finally:
        # Cleanup
        if movie_id:
            try:
                Movie.delete_movie(movie_id)
            except:
                pass
        try:
            User.deactivate(sample_user.email)
        except:
            pass

def test_watchlist_crud(sample_user, sample_movie):
    """Test watchlist CRUD operations with dependencies"""
    movie_id = None
    try:
        # First ensure user exists
        sample_user.save()
        
        # Add movie first
        add_result = Movie.add_movie(**sample_movie)
        assert add_result["success"], f"Failed to add movie: {add_result.get('error')}"
        
        # Get the movie ID
        movies = Movie.search_by_title(sample_movie["title"])
        assert movies["success"] and len(movies["data"]) > 0, "Movie should be found"
        movie_id = movies["data"][0]["movie_id"]
        
        # Test add to watchlist
        watch = Watchlist(user_email=sample_user.email, movie_id=movie_id)
        res1 = watch.save()
        assert res1["success"], f"Failed to save watchlist: {res1.get('error')}"
        
        # Test fetch user watchlist
        results = Watchlist.fetch_user_watchlist(sample_user.email)
        assert results["success"], f"Failed to fetch user watchlist: {results.get('error')}"
        assert len(results["data"]) > 0, "Should have watchlist entries"
        
        # Test update status
        status_result = Watchlist.update_status(sample_user.email, movie_id, "watched")
        assert status_result["success"], f"Failed to update status: {status_result.get('error')}"
        
        # Test remove from watchlist
        res2 = Watchlist.remove_from_watchlist(sample_user.email, movie_id)
        assert res2["success"], f"Failed to remove from watchlist: {res2.get('error')}"
        
        # Test admin fetch all watchlists
        all_watchlists = Watchlist.fetch_all()
        assert all_watchlists["success"], f"Failed to fetch all watchlists: {all_watchlists.get('error')}"
        
    finally:
        # Cleanup
        if movie_id:
            try:
                Movie.delete_movie(movie_id)
            except:
                pass
        try:
            User.deactivate(sample_user.email)
        except:
            pass



def test_table_creation():
    """Test that all tables can be created successfully"""
    # Test users table creation
    User.create_table()  # This prints but doesn't return anything
    
    # Test movies table creation
    movies_result = Movie.create_table()
    assert movies_result["success"], f"Failed to create movies table: {movies_result.get('error')}"
    
    # Test ratings table creation
    ratings_result = Rating.create_table()
    assert ratings_result["success"], f"Failed to create ratings table: {ratings_result.get('error')}"
    
    # Test watchlist table creation
    watchlist_result = Watchlist.create_table()
    assert watchlist_result["success"], f"Failed to create watchlist table: {watchlist_result.get('error')}"
    
    