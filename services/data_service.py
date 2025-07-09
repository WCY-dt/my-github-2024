"""
Data processing service for handling GitHub data fetching and processing.
"""

import json
import logging
import threading
from datetime import datetime
from flask import current_app

from utils.context import get_context
from services.database_service import DatabaseService
from services.github_service import GitHubService


class DataService:
    """Service for data processing operations."""
    
    @staticmethod
    def process_user_data(username: str, access_token: str, year: int, timezone: str):
        """Process user data in a background thread."""
        # Get the current app instance before starting the thread
        app = current_app._get_current_object()
        
        def fetch_data():
            with app.app_context():
                try:
                    # Fetch GitHub context data
                    context = get_context(username, access_token, year, timezone)
                    logging.info("Context of %s: %s", username, json.dumps(context))
                    
                    # Save context to database
                    DatabaseService.add_user_context(
                        username, year, json.dumps(context)
                    )
                    
                except Exception as e:
                    logging.error("Error fetching data: %s", e)
                
                # Star the repository
                GitHubService.star_repository(access_token)
        
        fetch_thread = threading.Thread(target=fetch_data)
        fetch_thread.start()
    
    @staticmethod
    def validate_year(year: int) -> bool:
        """Validate if the year is within acceptable range."""
        current_year = datetime.now().year
        return 2008 <= year <= current_year
    
    @staticmethod
    def validate_request_data(access_token: str, username: str, timezone: str, year: int) -> bool:
        """Validate request data."""
        return (
            all([access_token, username, timezone, year]) and
            DataService.validate_year(year)
        )
