from util import Github
from generator.fetch import fetch_github
from generator.context import get_context
from log.logging_config import setup_logging

from flask import (
    Flask,
    request,
    redirect,
    session,
    url_for,
    render_template,
    send_from_directory,
    jsonify,
    Response,
    stream_with_context,
)
import requests
from dotenv import load_dotenv
import os
import logging


app = Flask(__name__)

secret_key = os.urandom(24)
app.secret_key = secret_key

load_dotenv()
app.config['CLIENT_ID'] = os.getenv("CLIENT_ID")
app.config['CLIENT_SECRET'] = os.getenv("CLIENT_SECRET")

setup_logging()


@app.before_request
def before_request():
    if (
        request.endpoint not in ("index", "login", "callback", "static")
        and "access_token" not in session
    ):
        return redirect(url_for("index"))


@app.route("/")
def index():
    return render_template("login.html")


@app.route("/login")
def login():
    github_authorize_url = "https://github.com/login/oauth/authorize"
    return redirect(
        f"{github_authorize_url}?client_id={app.config['CLIENT_ID']}&scope=repo,read:org"
    )


@app.route("/callback")
def callback():
    code = request.args.get("code")
    token_response = requests.post(
        "https://github.com/login/oauth/access_token",
        headers={"Accept": "application/json"},
        data={
            "client_id": app.config["CLIENT_ID"],
            "client_secret": app.config["CLIENT_SECRET"],
            "code": code,
        },
    )
    token_json = token_response.json()
    access_token = token_json.get("access_token")
    session["access_token"] = access_token
    return redirect(url_for("dashboard"))


@app.route("/dashboard")
def dashboard():
    access_token = session.get("access_token")
    headers = {"Authorization": f"bearer {access_token}"}
    logging.info(f"access_token: {access_token}")
    user_response = requests.get("https://api.github.com/user", headers=headers)
    user_data = user_response.json()
    return render_template("dashboard.html", user=user_data, access_token=access_token)


@app.route("/load", methods=["POST"])
def load():
    data = request.json

    access_token = data.get("access_token")
    username = data.get("username")
    timezone = data.get("timezone")
    year = int(data.get("year"))

    session["access_token"] = access_token
    session["username"] = username
    session["timezone"] = timezone
    session["year"] = year

    return jsonify({"redirect_url": url_for("display", year=year)})


@app.route("/display")
def display():
    def generate():
        with app.app_context():
            access_token = session.get("access_token")
            username = session.get("username")
            timezone = session.get("timezone")
            year = session.get("year")

            if not all([access_token, username, timezone, year]):
                yield redirect(url_for("index"))

            yield "Processing, please wait..."

            github = Github(access_token, username, timezone)
            result, result_new_repo = fetch_github(github, year, skip_fetch=False)

            if result is None or result_new_repo is None:
                logging.info(f"data: {result}")
                logging.info(f"data_new_repo: {result_new_repo}")
                logging.error("Error fetching data from GitHub")
                yield "Error fetching data from GitHub", 500

            context = get_context(year, result, result_new_repo)

            yield render_template("template.html", context=context)

    return Response(stream_with_context(generate()), content_type="text/html")


@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory("static", filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)