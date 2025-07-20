# FastAPI Production App with Multiple MySQL Databases

A production-ready FastAPI application with support for multiple MySQL databases for different purposes (main application, analytics, and logs).

## Features

- **Multiple MySQL Databases**: Separate databases for main application, analytics, and logs
- **Database Connection Pooling**: Optimized connection management with configurable pool settings
- **Analytics Tracking**: User activity and item view tracking
- **Comprehensive Logging**: Application and API request logging with different log levels
- **RESTful API**: Clean API design with proper error handling
- **Production Ready**: Includes security, CORS, and performance optimizations

## Database Architecture

### 1. Main Database (`mono_api_main`)
- **Purpose**: Core application data
- **Models**: Items, Users, etc.
- **Base Class**: `BaseModel`

### 2. Analytics Database (`mono_api_analytics`)
- **Purpose**: User behavior tracking and analytics
- **Models**: UserActivity, ItemView
- **Base Class**: `AnalyticsBaseModel`

### 3. Logs Database (`mono_api_logs`)
- **Purpose**: Application and API logging
- **Models**: ApplicationLog, APILog
- **Base Class**: `LogsBaseModel`

## Prerequisites

- Python 3.8+
- MySQL 8.0+
- pip (Python package manager)

## Installation

### Quick Start (Recommended)

**For macOS/Linux:**
```bash
# Clone the repository
git clone <repository-url>
cd mono-api

# Run the quick start script (does everything automatically)
./quick_start.sh
```

**For Windows:**
```bash
# Clone the repository
git clone <repository-url>
cd mono-api

# Run the setup script
setup_venv.bat

# Then run the application
uvicorn app.main:app --reload
```

### Manual Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd mono-api
   ```

2. **Set up virtual environment**
   ```bash
   # macOS/Linux
   ./setup_venv.sh
   
   # Windows
   setup_venv.bat
   ```

3. **Activate virtual environment**
   ```bash
   # macOS/Linux
   source venv/bin/activate
   
   # Windows
   venv\Scripts\activate.bat
   ```

4. **Set up MySQL databases**
   ```sql
   -- Connect to MySQL as root or privileged user
   CREATE DATABASE mono_api_main;
   CREATE DATABASE mono_api_analytics;
   CREATE DATABASE mono_api_logs;
   
   -- Create user (optional, for better security)
   CREATE USER 'mono_api_user'@'localhost' IDENTIFIED BY 'your_secure_password';
   GRANT ALL PRIVILEGES ON mono_api_main.* TO 'mono_api_user'@'localhost';
   GRANT ALL PRIVILEGES ON mono_api_analytics.* TO 'mono_api_user'@'localhost';
   GRANT ALL PRIVILEGES ON mono_api_logs.* TO 'mono_api_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

5. **Configure environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your MySQL credentials
   ```

6. **Initialize databases**
   ```bash
   python -m app.db.init_db
   ```

7. **Test database connections**
   ```bash
   python test_connections.py
   ```

## Configuration

### Environment Variables

Copy `env.example` to `.env` and configure:

```env
# MySQL Database Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password_here
MYSQL_DATABASE=mono_api_main

# Analytics Database
MYSQL_ANALYTICS_HOST=localhost
MYSQL_ANALYTICS_PORT=3306
MYSQL_ANALYTICS_USER=root
MYSQL_ANALYTICS_PASSWORD=your_password_here
MYSQL_ANALYTICS_DATABASE=mono_api_analytics

# Logs Database
MYSQL_LOGS_HOST=localhost
MYSQL_LOGS_PORT=3306
MYSQL_LOGS_USER=root
MYSQL_LOGS_PASSWORD=your_password_here
MYSQL_LOGS_DATABASE=mono_api_logs

# Database Pool Settings
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
```

## Usage

### Available Scripts

The project includes several convenience scripts to make development easier:

| Script | Purpose | Platform |
|--------|---------|----------|
| `quick_start.sh` | Complete setup and run application | macOS/Linux |
| `setup_venv.sh` | Create and setup virtual environment | macOS/Linux |
| `activate_venv.sh` | Activate virtual environment | macOS/Linux |
| `setup_venv.bat` | Create and setup virtual environment | Windows |
| `activate_venv.bat` | Activate virtual environment | Windows |
| `test_connections.py` | Test all database connections | All |

### Running the Application

**Quick Start (macOS/Linux):**
```bash
./quick_start.sh
```

**Manual Start:**
```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate.bat  # Windows

# Run the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### API Documentation

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

## API Endpoints

### Main Application (Items)
- `GET /api/v1/items` - List items
- `POST /api/v1/items` - Create item
- `GET /api/v1/items/{item_id}` - Get item
- `PUT /api/v1/items/{item_id}` - Update item
- `DELETE /api/v1/items/{item_id}` - Delete item

### Analytics
- `POST /api/v1/analytics/user-activity` - Log user activity
- `POST /api/v1/analytics/item-view` - Log item view
- `GET /api/v1/analytics/user-activities` - Get user activities
- `GET /api/v1/analytics/item-views` - Get item views
- `GET /api/v1/analytics/popular-items` - Get popular items
- `GET /api/v1/analytics/stats/summary` - Get analytics summary

## Code Structure

```
mono-api/
├── app/
│   ├── api/v1/
│   │   ├── routers/
│   │   │   ├── items.py          # Main application endpoints
│   │   │   └── analytics.py      # Analytics endpoints
│   │   └── schemas/
│   ├── core/
│   │   └── config.py             # Configuration with multi-DB support
│   ├── db/
│   │   ├── base.py               # Multiple base classes
│   │   ├── session.py            # Multi-DB session management
│   │   └── init_db.py            # Database initialization
│   ├── models/
│   │   ├── item.py               # Main database models
│   │   ├── analytics.py          # Analytics database models
│   │   └── logs.py               # Logs database models
│   ├── services/
│   │   ├── item_service.py       # Main application service
│   │   ├── analytics_service.py  # Analytics service
│   │   └── logging_service.py    # Logging service
│   └── main.py                   # FastAPI application
├── requirements.txt              # Dependencies
├── env.example                   # Environment variables template
└── README.md                     # This file
```

## Database Usage Examples

### Using Different Databases in Services

```python
from app.db.session import get_main_db, get_analytics_db, get_logs_db
from app.services.analytics_service import AnalyticsService
from app.services.logging_service import LoggingService

# Main database operations
with next(get_main_db()) as db:
    # Work with main database
    pass

# Analytics database operations
AnalyticsService.log_user_activity(user_id=1, action="view_item")

# Logs database operations
LoggingService.log_application_event(
    level=LogLevel.INFO,
    message="User logged in",
    logger_name="auth"
)
```

### Creating Models for Different Databases

```python
# Main database model
from app.db.base import BaseModel

class User(BaseModel):
    __tablename__ = "users"
    # ... fields

# Analytics database model
from app.db.base import AnalyticsBaseModel

class UserActivity(AnalyticsBaseModel):
    __tablename__ = "user_activities"
    # ... fields

# Logs database model
from app.db.base import LogsBaseModel

class ApplicationLog(LogsBaseModel):
    __tablename__ = "application_logs"
    # ... fields
```

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
```

## Development

### Adding New Models

1. **Choose the appropriate base class**:
   - `BaseModel` for main application data
   - `AnalyticsBaseModel` for analytics data
   - `LogsBaseModel` for logging data

2. **Create the model file** in `app/models/`

3. **Import in `app/models/__init__.py`**

4. **Update database initialization** in `app/db/init_db.py`

### Adding New Services

1. **Create service file** in `app/services/`
2. **Use appropriate database session**:
   - `get_main_db()` for main database
   - `get_analytics_db()` for analytics database
   - `get_logs_db()` for logs database

### Adding New API Endpoints

1. **Create router file** in `app/api/v1/routers/`
2. **Import in `app/api/v1/__init__.py`**
3. **Use appropriate database dependency**

## Production Deployment

### Docker Setup

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables for Production

```env
# Production database settings
MYSQL_HOST=your-production-mysql-host
MYSQL_PASSWORD=your-secure-production-password
MYSQL_ANALYTICS_HOST=your-analytics-mysql-host
MYSQL_LOGS_HOST=your-logs-mysql-host

# Security
SECRET_KEY=your-very-secure-production-secret-key

# Performance
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check MySQL service is running
   - Verify credentials in `.env`
   - Ensure databases exist

2. **Import Errors**
   - Activate virtual environment
   - Install dependencies: `pip install -r requirements.txt`

3. **Permission Errors**
   - Check MySQL user privileges
   - Ensure user has access to all three databases

### Logs

- Application logs are stored in the logs database
- Check `ApplicationLog` and `APILog` tables for debugging
- Use `LoggingService` to add custom logging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License. 