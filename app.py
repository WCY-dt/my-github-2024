"""
Application factory and initialization.
"""

import logging
from flask import Flask, redirect, request, session, url_for

from config.config import config
from models.models import db
from services.database_service import DatabaseService
from routes.auth import auth_bp
from routes.main import main_bp
from routes.api import api_bp
from utils.logging_config import setup_logging
from utils.error_handlers import register_error_handlers


def create_app(config_name='default'):
    """Create Flask application with the given configuration."""
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize logging
    setup_logging()
    
    # Disable requests logging
    if logging.getLogger("requests"):
        logging.getLogger("requests").setLevel(logging.ERROR)
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Initialize database tables
    with app.app_context():
        DatabaseService.init_db()
    
    # Add before request handler
    @app.before_request
    def before_request():
        """Function to handle actions before each request."""
        # Skip processing for static files and favicon
        if request.endpoint == 'static' or request.path.startswith('/static/') or request.path == '/favicon.ico':
            return None
            
        protected_endpoints = {
            "main.dashboard", "main.load", "main.wait", "main.display"
        }
        public_endpoints = {
            "api.status", "api.health_check", "api.debug_routes", "auth.index", "auth.login", "auth.callback"
        }
        
        # Log current request for debugging
        logging.debug(f"Request endpoint: {request.endpoint}, path: {request.path}")
        
        # Allow access to public endpoints
        if request.endpoint in public_endpoints:
            return None
        
        # Redirect to index if not authenticated and accessing protected endpoint
        if (request.endpoint in protected_endpoints and 
            "access_token" not in session):
            return redirect(url_for("auth.index"))
        
        # Redirect unknown endpoints to index
        if request.endpoint not in (public_endpoints | protected_endpoints):
            logging.warning(f"Unknown endpoint accessed: {request.endpoint}")
            return redirect(url_for("auth.index"))
        
        return None
    
    return app
