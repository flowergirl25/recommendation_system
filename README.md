# 🎬 Movie Recommendation System

A comprehensive movie recommendation platform built with Python, featuring multiple recommendation algorithms, user management, and an intuitive web interface powered by Streamlit.

## 🌟 Features

### Core Functionality
- **Multi-Algorithm Recommendations**: Content-based, collaborative filtering, and hybrid approaches
- **User Authentication & Authorization**: Secure login/registration with role-based access control
- **Movie Management**: Complete CRUD operations for movies with poster integration
- **Rating System**: User ratings with comprehensive analytics
- **Watchlist Management**: Personal movie watchlists with status tracking
- **Admin Dashboard**: Administrative controls and system analytics

### Recommendation Engines
- **Personalized Recommendations**: Based on user rating history and preferences
- **Content-Based Filtering**: Using movie features (genres, cast, crew, keywords)
- **Collaborative Filtering**: Item-item similarity matrix for user behavior analysis
- **Genre-Based Recommendations**: Targeted suggestions by movie genres
- **Trending & Popular Movies**: Real-time trending and popularity-based suggestions

### Analytics & Insights
- Rating distribution analysis
- User activity tracking
- Movie popularity metrics
- Recommendation performance evaluation

## 🏗️ Architecture

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

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MySQL 5.7+
- TMDB API Key (for movie posters)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd movie_recommendation_system
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Set up the database**
   ```bash
   python setup_database.py
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

6. **Access the application**
   - Open your browser and navigate to the Streamlit URL (typically `http://localhost:8501`)

## ⚙️ Configuration

### Environment Variables (.env)
```env
# TMDB API Configuration
TMDB_API_KEY=your_tmdb_api_key_here

# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=movie_recommendation_db

# Development Settings
DEV_MODE=True
DEFAULT_ADMIN_EMAIL=admin@example.com
DEFAULT_ADMIN_PASSWORD=secure_password
```

### Database Setup
The system uses MySQL with the following main tables:
- `users`: User accounts and profiles
- `movies`: Movie catalog with metadata
- `ratings`: User movie ratings
- `watchlist`: User watchlists and viewing status

## 🤖 Machine Learning Models

### Content-Based Filtering
- **Features**: Genres, cast, crew, keywords, overview
- **Similarity**: Cosine similarity on TF-IDF vectors
- **Model Files**: `cosine_sim_improved.pkl`, `X_content_improved.npz`

### Collaborative Filtering
- **Approach**: Item-item collaborative filtering
- **Similarity**: Pearson correlation coefficient
- **Model Files**: `item_similarity.pkl`

### Model Evaluation
- **Metrics**: Precision@K, Recall@K, RMSE, MAE
- **Evaluation Script**: `recommend_model/scripts/evaluate_models.py`

## 📊 Data Pipeline

### Data Sources
- **MovieLens Dataset**: User ratings and movie metadata
- **TMDB Dataset**: Extended movie information and posters
- **Custom Data**: User-generated content and preferences

### Data Processing
1. **Raw Data Ingestion**: CSV files in `recommend_model/data/raw/`
2. **Data Cleaning**: Preprocessing scripts and notebooks
3. **Feature Engineering**: Content-based feature extraction
4. **Model Training**: Similarity matrix computation
5. **Model Serialization**: Pickle files for production use

## 🧪 Testing

Run the comprehensive test suite:
```bash
# Run all tests
pytest app_test/

# Run specific test modules
pytest app_test/test_models.py
pytest app_test/test_auth.py
pytest app_test/test_validators.py

# Run with coverage
pytest --cov=app app_test/
```

### Test Coverage
- **Models**: CRUD operations, data validation
- **Authentication**: Login, registration, session management
- **Validators**: Input validation and sanitization
- **Templates**: UI component functionality

## 🔐 Security Features

- **Password Hashing**: bcrypt for secure password storage
- **Session Management**: Secure user session handling
- **Input Validation**: Comprehensive input sanitization
- **Role-Based Access**: Admin and user role separation
- **SQL Injection Prevention**: Parameterized queries

## 📈 Performance Optimization

- **Database Indexing**: Optimized queries with proper indexing
- **Caching**: Model and similarity matrix caching
- **Batch Processing**: Bulk operations for large datasets
- **Lazy Loading**: On-demand model loading

## 🎯 API Endpoints

The system provides internal APIs through the view layer:
- **Authentication**: Login, logout, registration
- **Movies**: Search, CRUD operations, recommendations
- **Ratings**: Add, update, delete ratings
- **Watchlist**: Manage user watchlists
- **Analytics**: System metrics and insights

## 🔧 Development

### Code Structure
- **MVC Pattern**: Clear separation of concerns
- **Service Layer**: Business logic abstraction
- **Repository Pattern**: Data access layer
- **Decorator Pattern**: Logging and validation

### Logging
- **Configuration**: `app/config/logging_config.py`
- **Decorator**: `app/utils/logging_decorator.py`
- **Log Files**: `logs/app.log`

### Adding New Features
1. Create model in `app/models/`
2. Add business logic in `app/view/`
3. Create UI template in `app/templates/`
4. Add validation in `app/validators/`
5. Write tests in `app_test/`

## 📋 Requirements

### Core Dependencies
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

### Development Dependencies
```
pytest>=6.2.0
pytest-cov>=3.0.0
jupyter>=1.0.0
```

## 🚀 Deployment

### Production Checklist
- [ ] Set `DEV_MODE=False` in environment
- [ ] Configure production database
- [ ] Set up proper logging
- [ ] Configure reverse proxy (nginx)
- [ ] Set up SSL certificates
- [ ] Configure monitoring and alerts

### Docker Deployment
```dockerfile
# Dockerfile example
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "main.py"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Write comprehensive tests
- Update documentation
- Use meaningful commit messages

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **MovieLens**: For providing the movie ratings dataset
- **TMDB**: For movie metadata and poster images
- **Streamlit**: For the excellent web framework
- **scikit-learn**: For machine learning utilities

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review existing issues and discussions

## 🔄 Version History

- **v1.0.0**: Initial release with core functionality
- **v1.1.0**: Added collaborative filtering
- **v1.2.0**: Enhanced UI and admin features
- **v1.3.0**: Performance optimizations and testing

---

**Built with ❤️ by [Your Name]**