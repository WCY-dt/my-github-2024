"""
API routes for status and health checks.
"""

from datetime import datetime
from flask import Blueprint, jsonify

api_bp = Blueprint('api', __name__)


@api_bp.route("/status", methods=["GET"])
def status():
    """Endpoint to check the status of the application."""
    return jsonify({"status": "ok"}), 200


@api_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint for Docker."""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})


@api_bp.route("/debug/routes", methods=["GET"])
def debug_routes():
    """Debug endpoint to show all routes."""
    from flask import current_app
    routes = []
    for rule in current_app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'rule': str(rule)
        })
    return jsonify(routes)
