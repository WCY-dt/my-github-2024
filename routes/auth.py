"""
Authentication routes.
"""

import logging
from flask import Blueprint, redirect, render_template, request, session, url_for, current_app
from services.github_service import GitHubService
from config.config import Config

auth_bp = Blueprint('auth', __name__)


@auth_bp.route("/", methods=["GET"])
def index():
    """Endpoint for the index page."""
    if session.get("access_token"):
        return redirect(url_for("main.dashboard"))
    return render_template("login.html", project_year=current_app.config['PROJECT_YEAR'], star_repo=current_app.config['STAR_REPO'])


@auth_bp.route("/login", methods=["GET"])
def login():
    """Endpoint for the login page."""
    if session.get("access_token"):
        return redirect(url_for("main.dashboard"))
    
    return redirect(
        f"{Config.GITHUB_AUTHORIZE_URL}?client_id={Config.CLIENT_ID}&scope=repo,read:org"
    )


@auth_bp.route("/callback", methods=["GET"])
def callback():
    """Endpoint for the GitHub OAuth callback."""
    if "code" not in request.args:
        return redirect(url_for("auth.index"))

    code = request.args.get("code")
    if not code:
        return redirect(url_for("auth.index"))

    access_token = GitHubService.get_access_token(code)
    if not access_token:
        return redirect(url_for("auth.index"))
    
    session["access_token"] = access_token
    return redirect(url_for("main.dashboard"))
