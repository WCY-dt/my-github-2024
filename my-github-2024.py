"""
This module provides a Flask application for GitHub data fetching and display.
"""

import json
import logging
import os
import threading
from datetime import datetime

import requests
from dotenv import load_dotenv
from flask import (Flask, jsonify, redirect, render_template, request,
                   send_from_directory, session, url_for)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_

from log.logging_config import setup_logging
from util.context import get_context

setup_logging()

app = Flask(__name__)


def app_preparation():
    """
    Function to prepare the application.
    """
    app.secret_key = os.urandom(24)

    load_dotenv()
    app.config["CLIENT_ID"] = os.getenv("CLIENT_ID")
    app.config["CLIENT_SECRET"] = os.getenv("CLIENT_SECRET")

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///my-github-2024.db"

    if logging.getLogger("requests"):
        logging.getLogger("requests").setLevel(logging.ERROR)


app_preparation()


db = SQLAlchemy(app)


class RequestedUser(db.Model):
    """
    Model for requested GitHub users.
    """

    username = db.Column(db.String(80), primary_key=True, nullable=False)
    year = db.Column(db.Integer, primary_key=True, nullable=False)


class UserContext(db.Model):
    """
    Model for storing user context data.
    """

    username = db.Column(db.String(80), primary_key=True, nullable=False)
    year = db.Column(db.Integer, primary_key=True, nullable=False)
    context = db.Column(db.Text, nullable=False)


def db_preparation():
    """
    Function to prepare the database.
    """
    with app.app_context():
        db.create_all()
        missing_users = (
            db.session.query(RequestedUser)
            .outerjoin(
                UserContext,
                (RequestedUser.username == UserContext.username)
                & (RequestedUser.year == UserContext.year),
            )
            .filter(UserContext.username.is_(None))
            .all()
        )
        for user in missing_users:
            logging.info("Missing user: %s", user.username)
            db.session.query(RequestedUser).filter_by(
                username=user.username, year=user.year
            ).delete()
        db.session.commit()


db_preparation()


@app.before_request
def before_request():
    """
    Function to handle actions before each request.
    """
    if (
        request.endpoint not in ("status", "index", "login", "callback", "static")
        and "access_token" not in session
    ):
        return redirect(url_for("index"))

    if request.endpoint not in (
        "status",
        "index",
        "login",
        "callback",
        "dashboard",
        "load",
        "wait",
        "display",
        "static",
    ):
        return redirect(url_for("index"))

    return None


@app.route("/status", methods=["GET"])
def status():
    """
    Endpoint to check the status of the application.
    """
    return jsonify({"status": "ok"}), 200


@app.route("/", methods=["GET"])
def index():
    """
    Endpoint for the index page.
    """
    if session.get("access_token"):
        return redirect(url_for("dashboard"))
    return render_template("login.html")


@app.route("/login", methods=["GET"])
def login():
    """
    Endpoint for the login page.
    """
    if session.get("access_token"):
        return redirect(url_for("dashboard"))
    github_authorize_url = "https://github.com/login/oauth/authorize"
    return redirect(
        f"{github_authorize_url}?client_id={app.config['CLIENT_ID']}&scope=repo,read:org"
    )


@app.route("/callback", methods=["GET"])
def callback():
    """
    Endpoint for the GitHub OAuth callback.
    """
    if "code" not in request.args:
        return redirect(url_for("index"))

    code = request.args.get("code")

    if not code:
        return redirect(url_for("index"))

    try:
        token_response = requests.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": app.config["CLIENT_ID"],
                "client_secret": app.config["CLIENT_SECRET"],
                "code": code,
            },
            timeout=10,
        )
        token_json = token_response.json()
        access_token = token_json.get("access_token")
    except requests.exceptions.RequestException as e:
        logging.error("Error getting access token: %s", e)
        return redirect(url_for("index"))

    if not access_token:
        return redirect(url_for("index"))
    session["access_token"] = access_token
    return redirect(url_for("dashboard"))


@app.route("/dashboard", methods=["GET"])
def dashboard():
    """
    Endpoint for the dashboard page.
    """
    if not session.get("access_token"):
        return redirect(url_for("index"))

    access_token = session.get("access_token")
    headers = {"Authorization": f"bearer {access_token}"}
    logging.info("access_token: %s", access_token)
    user_response = requests.get(
        "https://api.github.com/user", headers=headers, timeout=10
    )
    user_data = user_response.json()

    username = user_data.get("login")
    session["username"] = username

    current_year = datetime.now().year

    return render_template(
        "dashboard.html",
        user=user_data,
        access_token=access_token,
        current_year=current_year,
    )


@app.route("/load", methods=["POST"])
def load():
    """
    Endpoint to load user data.
    """
    data = request.json

    access_token = str(data.get("access_token"))
    username = str(data.get("username"))
    timezone = str(data.get("timezone"))
    year = int(data.get("year"))

    current_year = int(datetime.now().year)

    if (not all([access_token, username, timezone, year])) or year < 2008 or year > current_year:
        return jsonify({"redirect_url": url_for("index")})

    session["access_token"] = access_token
    session["username"] = username
    session["timezone"] = timezone
    session["year"] = year

    if UserContext.query.filter(
        and_(UserContext.username == username, UserContext.year == year)
    ).first():
        return jsonify({"redirect_url": url_for("display", year=year)})

    if RequestedUser.query.filter(
        and_(RequestedUser.username == username, RequestedUser.year == year)
    ).first():
        return jsonify({"redirect_url": url_for("wait", year=year)})

    try:
        requested_user = RequestedUser(username=username, year=year)
        db.session.add(requested_user)
        db.session.commit()
    except Exception as e:
        logging.error("Error saving requested user: %s", e)

    if not all([username, access_token, year, timezone]):
        return jsonify({"redirect_url": url_for("index")})

    def fetch_data():
        with app.app_context():
            try:
                context = get_context(username, access_token, year, timezone)

                logging.info("Context of %s: %s", username, json.dumps(context))

                user_context = UserContext(
                    username=username, context=json.dumps(context), year=year
                )
                db.session.add(user_context)
                db.session.commit()
            except Exception as e:
                logging.error("Error fetching data: %s", e)

        # Star the repository
        try:
            star_response = requests.put(
                "https://api.github.com/user/starred/WCY-dt/my-github-2024",
                headers={
                    "Authorization": f"token {access_token}",
                    "Accept": "application/vnd.github.v3+json",
                },
                timeout=10,
            )
            if star_response.status_code == 204:
                logging.info("Successfully starred WCY-dt/my-github-2024")
            else:
                logging.error(
                    "Failed to star WCY-dt/my-github-2024: %s", star_response.json()
                )
        except requests.exceptions.RequestException as e:
            logging.error("Error starring repository: %s", e)

    fetch_thread = threading.Thread(target=fetch_data)
    fetch_thread.start()

    return jsonify({"redirect_url": url_for("wait", year=year)})


@app.route("/wait/<path:year>", methods=["GET"])
def wait(year):
    """
    Endpoint for the wait page.
    """
    if not session.get("access_token"):
        return redirect(url_for("index"))

    username = session.get("username")

    if UserContext.query.filter(
        and_(UserContext.username == username, UserContext.year == int(year))
    ).first():
        return redirect(url_for("display", year=year))

    if RequestedUser.query.filter(
        and_(RequestedUser.username == username, RequestedUser.year == int(year))
    ).first():
        return render_template("wait.html", year=year)

    return render_template("dashboard.html")


@app.route("/display/<path:year>", methods=["GET"])
def display(year):
    """
    Endpoint for the display page.
    """
    if not session.get("access_token"):
        return redirect(url_for("index"))

    username = session.get("username")
    user_context = UserContext.query.filter(
        and_(UserContext.username == username, UserContext.year == int(year))
    ).first()

    logging.info("Display user context: %s", username)

    if user_context:
        return render_template(
            "template.html", context=json.loads(user_context.context)
        )

    if RequestedUser.query.filter(
        and_(RequestedUser.username == username, RequestedUser.year == int(year))
    ).first():
        return redirect(url_for("wait", year=year))

    return redirect(url_for("dashboard"))


@app.route("/health", methods=["GET"])
def health_check():
    """
    Health check endpoint for Docker.
    """
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})


@app.route("/static/<path:filename>", methods=["GET"])
def static_files(filename):
    """
    Endpoint to serve static files.
    """
    return send_from_directory("static", filename)


if __name__ == "__main__":
    # app.run(host="0.0.0.0", port=5000, debug=True)
    app.run(host="0.0.0.0", port=5000)
