import pytest
from app.validators.user_validator import validate_email, validate_password
from app.validators.movie_validator import (
    validate_title, validate_genres, validate_release_date,
    validate_runtime, validate_popularity, validate_vote_average,
    validate_vote_count, validate_language, validate_poster_path
)
from app.validators.ratings_validators import validate_rating_value  
from app.validators.watchlist_validators import validate_user_email, validate_movie_id 

def test_validate_email():
    assert validate_email("user@gmail.com")
    assert validate_email("user@yahoo.com")
    assert validate_email("user@outlook.com")
    assert not validate_email("invalidemail.com")
    assert not validate_email("user@invaliddomain.xyz")

def test_validate_password():
    assert validate_password("Valid123!")
    assert not validate_password("short")
    assert not validate_password("nouppercase1!")
    assert not validate_password("NOLOWERCASE1!")
    assert not validate_password("NoSpecial123")

def test_validate_title():
    assert validate_title("Inception")
    assert not validate_title("")

def test_validate_genres():
    assert validate_genres("Drama,Action")
    assert validate_genres("")

def test_validate_release_date():
    assert validate_release_date("2020-01-01")
    assert not validate_release_date("3000-01-01")
    assert not validate_release_date("invalid-date")

def test_validate_runtime():
    assert validate_runtime(120)
    assert not validate_runtime(-10)

def test_validate_popularity():
    assert validate_popularity(5.5)
    assert not validate_popularity(-1)

def test_validate_vote_average():
    assert validate_vote_average(8.5)
    assert not validate_vote_average(11)

def test_validate_vote_count():
    assert validate_vote_count(100)
    assert not validate_vote_count(-5)

def test_validate_language():
    assert validate_language("en")
    assert not validate_language("english")

def test_validate_poster_path():
    assert validate_poster_path("https://example.com/poster.jpg")
    assert validate_poster_path("")
    assert not validate_poster_path("invalid-url")

def test_validate_rating_value():  # Changed function name
    # Test according to ratings_validators.py: rating must be 0.5-5.0
    assert validate_rating_value(5.0)
    assert validate_rating_value(0.5)
    assert validate_rating_value(2.5)
    assert not validate_rating_value(-1)
    assert not validate_rating_value(0.4)  # Below 0.5
    assert not validate_rating_value(5.1)  # Above 5.0
    assert not validate_rating_value(None)

def test_validate_watchlist_user_email():  # Split into separate tests
    # Test according to watchlist_validators.py: basic email check
    assert validate_user_email("user@gmail.com")
    assert validate_user_email("test@example.org")
    assert not validate_user_email("")
    assert not validate_user_email("invalid-email")
    assert not validate_user_email("no-at-symbol.com")

def test_validate_watchlist_movie_id():  # Split into separate tests
    # Test according to watchlist_validators.py: positive integer
    assert validate_movie_id(1)
    assert validate_movie_id(100)
    assert not validate_movie_id(0)
    assert not validate_movie_id(-1)
    assert not validate_movie_id("1")  # String instead of int