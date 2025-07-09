"""
Configuration module for the application.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration class."""
    
    # Application constants - year configuration
    PROJECT_YEAR = "2024"
    MIN_YEAR = 2008
    CURRENT_YEAR = 2024
    
    SECRET_KEY = os.urandom(24)
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    SQLALCHEMY_DATABASE_URI = f"sqlite:///my-github-{PROJECT_YEAR}.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # GitHub API URLs
    GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
    GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
    GITHUB_API_BASE_URL = "https://api.github.com"
    GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"
    
    # Application constants
    STAR_REPO = f"WCY-dt/my-github-{PROJECT_YEAR}"
    
    # Request timeout
    REQUEST_TIMEOUT = 10


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    # Enable template auto-reload for development
    TEMPLATES_AUTO_RELOAD = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
