"""
GitHub service for handling GitHub API operations.
"""

import logging
import requests
from config.config import Config


class GitHubService:
    """Service for GitHub API operations."""
    
    @staticmethod
    def get_access_token(code: str) -> str:
        """Exchange authorization code for access token."""
        try:
            token_response = requests.post(
                Config.GITHUB_TOKEN_URL,
                headers={"Accept": "application/json"},
                data={
                    "client_id": Config.CLIENT_ID,
                    "client_secret": Config.CLIENT_SECRET,
                    "code": code,
                },
                timeout=Config.REQUEST_TIMEOUT,
            )
            token_json = token_response.json()
            return token_json.get("access_token")
        except requests.exceptions.RequestException as e:
            logging.error("Error getting access token: %s", e)
            return None
    
    @staticmethod
    def get_user_info(access_token: str) -> dict:
        """Get user information from GitHub API."""
        try:
            headers = {"Authorization": f"bearer {access_token}"}
            user_response = requests.get(
                f"{Config.GITHUB_API_BASE_URL}/user", 
                headers=headers, 
                timeout=Config.REQUEST_TIMEOUT
            )
            return user_response.json()
        except requests.exceptions.RequestException as e:
            logging.error("Error getting user info: %s", e)
            return {}
    
    @staticmethod
    def star_repository(access_token: str) -> bool:
        """Star the repository."""
        try:
            star_response = requests.put(
                f"{Config.GITHUB_API_BASE_URL}/user/starred/{Config.STAR_REPO}",
                headers={
                    "Authorization": f"token {access_token}",
                    "Accept": "application/vnd.github.v3+json",
                },
                timeout=Config.REQUEST_TIMEOUT,
            )
            if star_response.status_code == 204:
                logging.info("Successfully starred %s", Config.STAR_REPO)
                return True
            else:
                logging.error(
                    "Failed to star %s: %s", Config.STAR_REPO, star_response.json()
                )
                return False
        except requests.exceptions.RequestException as e:
            logging.error("Error starring repository: %s", e)
            return False
