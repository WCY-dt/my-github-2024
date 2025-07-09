"""
Main application routes.
"""

import json
import logging
from datetime import datetime
from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for, current_app

from services.database_service import DatabaseService
from services.github_service import GitHubService
from services.data_service import DataService

main_bp = Blueprint('main', __name__)


@main_bp.route("/dashboard", methods=["GET"])
def dashboard():
    """Endpoint for the dashboard page."""
    if not session.get("access_token"):
        return redirect(url_for("auth.index"))

    access_token = session.get("access_token")
    user_data = GitHubService.get_user_info(access_token)
    
    if not user_data:
        return redirect(url_for("auth.index"))

    username = user_data.get("login")
    session["username"] = username
    current_year = datetime.now().year

    return render_template(
        "dashboard.html",
        user=user_data,
        access_token=access_token,
        current_year=current_year,
        project_year=current_app.config['PROJECT_YEAR'],
        star_repo=current_app.config['STAR_REPO']
    )


@main_bp.route("/load", methods=["POST"])
def load():
    """Endpoint to load user data."""
    data = request.json

    access_token = str(data.get("access_token"))
    username = str(data.get("username"))
    timezone = str(data.get("timezone"))
    year = int(data.get("year"))

    # Validate request data
    if not DataService.validate_request_data(access_token, username, timezone, year):
        return jsonify({"redirect_url": url_for("auth.index")})

    # Update session
    session["access_token"] = access_token
    session["username"] = username
    session["timezone"] = timezone
    session["year"] = year

    # Check if context already exists
    if DatabaseService.get_user_context(username, year):
        return jsonify({"redirect_url": url_for("main.display", year=year)})

    # Check if request is already in progress
    if DatabaseService.get_requested_user(username, year):
        return jsonify({"redirect_url": url_for("main.wait", year=year)})

    # Add to requested users
    if not DatabaseService.add_requested_user(username, year):
        return jsonify({"redirect_url": url_for("auth.index")})

    # Start data processing in background
    DataService.process_user_data(username, access_token, year, timezone)

    return jsonify({"redirect_url": url_for("main.wait", year=year)})


@main_bp.route("/wait/<path:year>", methods=["GET"])
def wait(year):
    """Endpoint for the wait page."""
    if not session.get("access_token"):
        return redirect(url_for("auth.index"))

    username = session.get("username")

    # Check if processing is complete
    if DatabaseService.get_user_context(username, int(year)):
        return redirect(url_for("main.display", year=year))

    # Check if request exists
    if DatabaseService.get_requested_user(username, int(year)):
        return render_template("wait.html", year=year, project_year=current_app.config['PROJECT_YEAR'])

    return redirect(url_for("main.dashboard"))


@main_bp.route("/display/<path:year>", methods=["GET"])
def display(year):
    """Endpoint for the display page."""
    if not session.get("access_token"):
        return redirect(url_for("auth.index"))

    username = session.get("username")
    user_context = DatabaseService.get_user_context(username, int(year))

    logging.info("Display user context: %s", username)

    if user_context:
        return render_template(
            "template.html", 
            context=json.loads(user_context.context),
            project_year=current_app.config['PROJECT_YEAR'],
            star_repo=current_app.config['STAR_REPO']
        )

    # If no context but request exists, redirect to wait
    if DatabaseService.get_requested_user(username, int(year)):
        return redirect(url_for("main.wait", year=year))

    return redirect(url_for("main.dashboard"))
