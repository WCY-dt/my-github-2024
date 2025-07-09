"""
Utility decorators for the application.
"""

import functools
import logging
from flask import session, redirect, url_for, jsonify


def require_auth(f):
    """Decorator to require authentication for routes."""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'access_token' not in session:
            if hasattr(f, '__name__') and f.__name__ in ['load']:
                return jsonify({"redirect_url": url_for("auth.index")})
            return redirect(url_for('auth.index'))
        return f(*args, **kwargs)
    return decorated_function


def log_errors(f):
    """Decorator to log errors in routes."""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logging.error(f"Error in {f.__name__}: {e}")
            raise
    return decorated_function
