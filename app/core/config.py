"""
Configuration settings using Pydantic Settings.
Loads configuration from environment variables and .env file.
"""
from typing import List, Optional, Dict
from pydantic import validator
from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # MySQL Database Configuration
    # Primary Database (Main application database)
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "a3227240"
    MYSQL_DATABASE: str = "mono_api_main"
    
    # Secondary Database (Analytics/Reporting)
    MYSQL_ANALYTICS_HOST: str = "localhost"
    MYSQL_ANALYTICS_PORT: int = 3306
    MYSQL_ANALYTICS_USER: str = "root"
    MYSQL_ANALYTICS_PASSWORD: str = "a3227240"
    MYSQL_ANALYTICS_DATABASE: str = "mono_api_analytics"
    
    # Third Database (Logs/Audit)
    MYSQL_LOGS_HOST: str = "localhost"
    MYSQL_LOGS_PORT: int = 3306
    MYSQL_LOGS_USER: str = "root"
    MYSQL_LOGS_PASSWORD: str = "a3227240"
    MYSQL_LOGS_DATABASE: str = "mono_api_logs"
    
    # Database Pool Settings
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600
    
    # Legacy SQLite support (fallback)
    DATABASE_URL: str = "sqlite:///./app.db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "FastAPI Production App"
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    def get_mysql_url(self, database_type: str = "main") -> str:
        """Generate MySQL connection URL for different databases."""
        if database_type == "main":
            return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
        elif database_type == "analytics":
            return f"mysql+pymysql://{self.MYSQL_ANALYTICS_USER}:{self.MYSQL_ANALYTICS_PASSWORD}@{self.MYSQL_ANALYTICS_HOST}:{self.MYSQL_ANALYTICS_PORT}/{self.MYSQL_ANALYTICS_DATABASE}"
        elif database_type == "logs":
            return f"mysql+pymysql://{self.MYSQL_LOGS_USER}:{self.MYSQL_LOGS_PASSWORD}@{self.MYSQL_LOGS_HOST}:{self.MYSQL_LOGS_PORT}/{self.MYSQL_LOGS_DATABASE}"
        else:
            raise ValueError(f"Unknown database type: {database_type}")
    
    def get_database_config(self) -> Dict[str, str]:
        """Get all database configurations."""
        return {
            "main": self.get_mysql_url("main"),
            "analytics": self.get_mysql_url("analytics"),
            "logs": self.get_mysql_url("logs")
        }
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings() 