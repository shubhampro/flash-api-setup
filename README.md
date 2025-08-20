# FastAPI Multi-App Project

A FastAPI project with multiple applications (API v1, API v2, and Admin) and shared components.

## Project Structure

```
repo/
├─ apps/
│  ├─ api/
│  │  ├─ v1/
│  │  │  ├─ routers/
│  │  │  │  ├─ users.py
│  │  │  │  └─ auth.py
│  │  │  └─ schemas/
│  │  │     ├─ user_in.py
│  │  │     └─ user_out.py
│  │  ├─ v2/
│  │  │  ├─ routers/
│  │  │  │  └─ users.py
│  │  │  └─ schemas/
│  │  │     └─ user_out.py
│  │  └─ app.py
│  └─ admin/
│     ├─ routers/
│     │  └─ users.py
│     └─ app.py
├─ shared/
│  ├─ core/
│  │  ├─ config.py
│  │  ├─ errors.py
│  │  └─ security.py
│  ├─ db/
│  │  ├─ base.py
│  │  ├─ session.py
│  │  ├─ models/
│  │  │  └─ user.py
│  │  └─ repositories/
│  │     └─ user_repo.py
│  └─ services/
│     └─ user_service.py
├─ migrations/
├─ tests/
│  └─ test_users_v1.py
├─ main.py
├─ requirements.txt
├─ config.env
└─ init_db.py
```

## Features

- **Multi-App Architecture**: Separate apps for API v1, API v2, and Admin
- **Shared Components**: Common database models, services, and utilities
- **JWT Authentication**: Secure token-based authentication
- **Database Abstraction**: SQLAlchemy ORM with repository pattern
- **Input Validation**: Pydantic schemas for request/response validation
- **Error Handling**: Custom exception classes and HTTP error responses
- **Testing**: Pytest-based test suite

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd mono-api
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp config.env .env
# Edit .env with your configuration
```

5. Initialize the database:
```bash
python init_db.py
```

## Running the Application

Start the main application:
```bash
python main.py
```

Or use uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### API v1 (`/api/v1`)
- `POST /users/` - Create user
- `GET /users/` - Get all users
- `GET /users/{user_id}` - Get user by ID
- `PUT /users/{user_id}` - Update user
- `DELETE /users/{user_id}` - Delete user
- `POST /users/login` - User login
- `GET /auth/me` - Get current user info
- `POST /auth/verify` - Verify JWT token
- `POST /auth/refresh` - Refresh access token

### API v2 (`/api/v2`)
- `GET /users/` - Get all users (enhanced)
- `GET /users/{user_id}` - Get user by ID (enhanced)
- `GET /users/me/profile` - Get current user profile

### Admin (`/admin`)
- `GET /users/` - Get all users (admin only)
- `GET /users/{user_id}` - Get user by ID (admin only)
- `PUT /users/{user_id}` - Update user (admin only)
- `DELETE /users/{user_id}` - Delete user (admin only)
- `POST /users/{user_id}/activate` - Activate user
- `POST /users/{user_id}/deactivate` - Deactivate user
- `POST /users/{user_id}/make-admin` - Grant admin privileges
- `POST /users/{user_id}/remove-admin` - Remove admin privileges

## Authentication

The application uses JWT tokens for authentication. To access protected endpoints:

1. Login with user credentials:
```bash
POST /api/v1/users/login
{
    "email": "user@example.com",
    "password": "password123"
}
```

2. Use the returned access token in the Authorization header:
```
Authorization: Bearer <access_token>
```

## Database

The application uses SQLite by default (configurable via `DATABASE_URL`). The database includes:

- **Users table**: User accounts with authentication and profile information
- **Repository pattern**: Clean separation between data access and business logic
- **Service layer**: Business logic and validation

## Testing

Run the test suite:
```bash
pytest tests/
```

## Configuration

Key configuration options in `config.env`:

- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: JWT signing key
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time
- `ENVIRONMENT`: Application environment (development/production)
- `DEBUG`: Debug mode flag

## Development

### Adding New Endpoints

1. Create schemas in the appropriate `schemas/` directory
2. Add router logic in the appropriate `routers/` directory
3. Include the router in the corresponding `app.py` file

### Adding New Models

1. Create the model in `shared/db/models/`
2. Add repository methods in `shared/db/repositories/`
3. Add service methods in `shared/services/`

### Database Migrations

For production use, consider using Alembic for database migrations:

```bash
alembic init migrations
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Security Considerations

- Change the default `SECRET_KEY` in production
- Use strong passwords and consider password policies
- Implement rate limiting for authentication endpoints
- Use HTTPS in production
- Consider implementing refresh token rotation

## License

This project is licensed under the MIT License.
