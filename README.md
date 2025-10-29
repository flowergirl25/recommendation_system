# Movie Recommendation System

This is a movie recommendation platform I built using Python. It includes several recommendation algorithms, user authentication, and a web interface using Streamlit.

## Features

The system includes several key features:

- Multiple recommendation algorithms (content-based, collaborative filtering, hybrid)
- User authentication with role-based access (admin/user)
- Movie database with CRUD operations and poster images
- User rating system with analytics
- Personal watchlists with viewing status
- Admin dashboard for system management

The recommendation engine works in several ways:
- Personalized suggestions based on your rating history
- Content-based filtering using movie metadata (genres, cast, crew)
- Collaborative filtering that finds similar users and movies
- Genre-specific recommendations
- Trending and popular movie lists

I've also included analytics features like rating distributions, user activity tracking, and recommendation performance metrics.

## Project Structure

```
movie_recommendation_system/
├── app/                          # Main application package
│   ├── auth/                     # Authentication & authorization
│   ├── config/                   # Database & logging configuration
│   ├── controller/               # Main application controller
│   ├── models/                   # Data models (User, Movie, Rating, Watchlist)
│   ├── templates/                # UI templates for different views
│   ├── utils/                    # Utility functions and decorators
│   ├── validators/               # Input validation modules
│   └── view/                     # Business logic layer
├── recommend_model/              # ML recommendation engine
│   ├── data/                     # Raw and processed datasets
│   ├── notebooks/                # Jupyter notebooks for EDA
│   ├── scripts/                  # Model training and evaluation
│   └── trained_models/           # Serialized ML models
├── app_test/                     # Comprehensive test suite
└── logs/                         # Application logs
```

## Getting Started

### What You'll Need
- Python 3.8 or higher
- MySQL 5.7 or higher
- TMDB API key (for fetching movie posters)

### Installation Steps

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd movie_recommendation_system
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your environment variables by copying the example file:
   ```bash
   cp .env.example .env
   ```
   Then edit the .env file with your database credentials and TMDB API key.

4. Initialize the database:
   ```bash
   python setup_database.py
   ```

5. Start the application:
   ```bash
   python main.py
   ```

6. Open your browser and go to `http://localhost:8501` to use the app.

## Configuration

You'll need to set up these environment variables in your .env file:

```env
# Get this from TMDB website
TMDB_API_KEY=your_api_key_here

# Your MySQL database settings
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=movie_recommendation_db

# Development mode settings
DEV_MODE=True
DEFAULT_ADMIN_EMAIL=admin@example.com
DEFAULT_ADMIN_PASSWORD=secure_password
```

The application uses MySQL with these main tables:
- `users` - stores user accounts and profiles
- `movies` - contains the movie catalog with metadata
- `ratings` - tracks user movie ratings
- `watchlist` - manages user watchlists and viewing status

## How the Recommendations Work

I implemented two main recommendation approaches:

**Content-Based Filtering**
This method analyzes movie features like genres, cast, crew, and plot summaries. It uses TF-IDF vectorization and cosine similarity to find movies with similar characteristics. The trained models are saved as `cosine_sim_improved.pkl` and `X_content_improved.npz`.

**Collaborative Filtering**
This approach looks at user behavior patterns using item-item collaborative filtering with Pearson correlation. It finds movies that users with similar tastes have enjoyed. The similarity matrix is stored in `item_similarity.pkl`.

**Model Performance**
I evaluate the models using standard metrics like Precision@K, Recall@K, RMSE, and MAE. You can run the evaluation script at `recommend_model/scripts/evaluate_models.py` to see how well the models perform.

## Data Processing

The system uses data from several sources:
- MovieLens dataset for user ratings and basic movie info
- TMDB API for additional movie details and poster images
- User-generated ratings and watchlist data

The data processing pipeline works like this:
1. Raw data is stored in CSV files under `recommend_model/data/raw/`
2. Data cleaning and preprocessing using Python scripts and Jupyter notebooks
3. Feature extraction for content-based recommendations
4. Training similarity matrices for both content-based and collaborative filtering
5. Saving trained models as pickle files for the web application to use

## Testing

I've included a comprehensive test suite. To run the tests:

```bash
# Run all tests
pytest app_test/

# Test specific components
pytest app_test/test_models.py
pytest app_test/test_auth.py
pytest app_test/test_validators.py

# Check test coverage
pytest --cov=app app_test/
```

The tests cover:
- Database models and CRUD operations
- User authentication and session management
- Input validation and data sanitization
- UI template functionality

## Security

Security measures I've implemented:
- Password hashing using bcrypt
- Secure session management
- Input validation and sanitization
- Role-based access control (admin vs regular users)
- SQL injection prevention through parameterized queries

## Performance

Performance optimizations include:
- Database indexing for faster queries
- Caching of similarity matrices and models
- Batch processing for handling large datasets
- Lazy loading of models to reduce startup time

## Internal APIs

The application has internal APIs for:
- User authentication (login, logout, registration)
- Movie operations (search, add, edit, delete, recommendations)
- Rating management (add, update, delete ratings)
- Watchlist functionality
- Analytics and system metrics

## Development Notes

The code follows these patterns:
- MVC architecture for clear separation of concerns
- Service layer for business logic
- Repository pattern for data access
- Decorator pattern for logging and validation

Logging is configured in `app/config/logging_config.py` with a decorator in `app/utils/logging_decorator.py`. Logs are written to `logs/app.log`.

To add new features:
1. Create the data model in `app/models/`
2. Add business logic in `app/view/`
3. Create UI templates in `app/templates/`
4. Add input validation in `app/validators/`
5. Write tests in `app_test/`

## Dependencies

Main packages used:
```
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
```

For development:
```
pytest>=6.2.0
pytest-cov>=3.0.0
jupyter>=1.0.0
```

## Deployment

For production deployment:
- Set `DEV_MODE=False` in your environment
- Configure a production database
- Set up proper logging
- Use a reverse proxy like nginx
- Configure SSL certificates
- Set up monitoring and alerts

Here's a basic Dockerfile:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "main.py"]
```

## Contributing

If you'd like to contribute:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Make your changes and commit them
4. Push to your branch
5. Open a Pull Request

Please follow PEP 8 style guidelines, write tests for new features, and update documentation as needed.

## License

This project is licensed under the MIT License.

## Acknowledgments

Thanks to:
- MovieLens for the movie ratings dataset
- TMDB for movie metadata and poster images
- The Streamlit team for their excellent framework
- scikit-learn for machine learning tools

## Support

If you have questions or run into issues:
- Check the existing documentation
- Look through the GitHub issues
- Create a new issue if needed

## Version History

- v1.0.0: Initial release with basic functionality
- v1.1.0: Added collaborative filtering
- v1.2.0: Improved UI and admin features
- v1.3.0: Performance improvements and comprehensive testing