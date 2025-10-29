# Movie Recommendation System

This is a movie recommendation platform built using Python with a collaborative filtering recommendation engine. It includes user authentication, movie database management, user ratings, and a user-friendly web interface built with Streamlit.

## Features

- Collaborative filtering-based recommendation system leveraging user ratings and similarity metrics
- User authentication with role-based access control (admin and regular users)
- Comprehensive movie database with CRUD operations and poster images sourced via TMDB API
- User rating system with detailed analytics and reporting
- Personal watchlists with viewing status tracking
- Admin dashboard for managing users, movies, and system usage

## How Recommendations Work

The core recommendation algorithm is item-item collaborative filtering using Pearson correlation. It identifies movies liked by similar users and recommends these to the current user. Additional recommendation lists include trending movies and genre-specific suggestions based on aggregated user activity.

## Project Structure

movie_recommendation_system/
├── app/ # Main application package
│ ├── auth/ # Authentication and authorization
│ ├── config/ # Database and logging configurations
│ ├── controller/ # Application controllers
│ ├── models/ # Data models (User, Movie, Rating, Watchlist)
│ ├── templates/ # UI templates for views
│ ├── utils/ # Utility functions and decorators
│ ├── validators/ # Input validators
│ └── view/ # Business logic
├── recommend_model/ # ML recommendation engine
│ ├── data/ # Raw and processed datasets
│ ├── notebooks/ # Jupyter notebooks for exploration
│ ├── scripts/ # Model training and evaluation scripts
│ └── trained_models/ # Serialized models
├── app_test/ # Test suite
└── logs/ # Application logs


## Requirements

- Python 3.8 or higher
- MySQL 5.7 or higher
- TMDB API key (to fetch movie posters)

## Installation

1. Clone the repository:
git clone <repository-url>
cd movie_recommendation_system


2. Install dependencies:
pip install -r requirements.txt

3. Setup environment variables:
cp .env.example .env
Edit `.env` with your MySQL credentials and TMDB API key.

4. Initialize the MySQL database:
python setup_database.py

5. Launch the app:
python main.py

6. Access the app at: `http://localhost:8501`

## Configuration

Edit your `.env` file to include:

TMDB_API_KEY=your_api_key_here
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=movie_recommendation_db

DEV_MODE=True
DEFAULT_ADMIN_EMAIL=admin@example.com
DEFAULT_ADMIN_PASSWORD=secure_passwo

## Testing

Run tests using pytest:

pytest app_test/
pytest app_test/test_models.py
pytest app_test/test_auth.py
pytest app_test/test_validators.py
pytest --cov=app app_test/

## Security

- Passwords hashed with bcrypt
- Role-based access control
- Secure session management
- SQL injection prevention via parameterized queries
- Input validation and sanitization

## Performance

- Database indexing
- Model and similarity data caching
- Batch processing for model updates
- Lazy model loading to reduce startup time

## Dependencies

numpy>=1.21.0
pandas>=1.3.0
scikit-learn>=1.0.0
streamlit>=1.28.0
pymysql>=1.0.0
bcrypt>=3.2.0
python-dotenv>=0.19.0
scipy>=1.7.0
matplotlib>=3.5.0
seaborn>=0.11.0
requests>=2.26.0

Dev dependencies:

pytest>=6.2.0
pytest-cov>=3.0.0
jupyter>=1.0.0

## Deployment

- Set `DEV_MODE=False` for production
- Use production-grade database servers
- Setup logging and monitoring
- Use a reverse proxy (e.g., nginx) with HTTPS

Example Dockerfile:

FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "main.py"]

## Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes
4. Push to your branch
5. Open a pull request

Follow PEP 8 style guidelines and write tests for new features.
