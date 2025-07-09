"""
Module for generating context data for GitHub statistics.

Functions:
    get_context(username: str, token: str, year: int, time_zone: str) -> dict:
        Generate context data for the given year from the provided data.
"""

import calendar
import logging
import re
from datetime import datetime, timedelta
from itertools import groupby

import pytz

from utils.logging_config import setup_logging
from utils.fetch_data import get_github_info

setup_logging()


def _parse_time(time_str: str, timezone: pytz.BaseTzInfo) -> str:
    """
    Parse the time string to the timezone.

    Args:
        time_str (str): The time string.
        timezone (pytz.BaseTzInfo): The timezone.

    Returns:
        str: The time string in the timezone.
    """
    result = None
    try:
        result = (
            datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%SZ")
            .replace(tzinfo=pytz.UTC)
            .astimezone(timezone)
            .isoformat()
        )
    except ValueError as e:
        logging.error("Failed to parse time: %s", e)
        logging.error("Time: %s", time_str)
        result = datetime(2000, 1, 1).isoformat()
    except pytz.UnknownTimeZoneError as e:
        logging.error("Unknown timezone: %s", e)
        result = datetime(2000, 1, 1).isoformat()

    return result


def _get_commit_type(message: str) -> str:
    """
    Get the type of the commit message based on the conventional commit types.

    Args:
        message (str): The commit message.

    Returns:
        str: The type of the commit message, including "feat", "fix", "docs", "style", "refactor",
             "test", "chore", "perf", "build", "revert", "ci", and "others".
    """
    commit_type = re.split(r"[:(!/\s]", message)[0].lower()
    conventional_types = {
        "feat": ["feature", "feat", "features", "feats"],
        "fix": ["fix"],
        "docs": ["docs", "doc", "documentation"],
        "style": ["style", "styles"],
        "refactor": ["refactor", "refactors", "refact"],
        "test": ["test", "tests"],
        "chore": ["chore", "chores"],
        "perf": ["perf", "performance"],
        "build": ["build", "builds"],
        "revert": ["revert"],
        "ci": ["ci", "cicd", "pipeline", "pipelines", "cd"],
    }
    for key, value in conventional_types.items():
        if commit_type in value:
            return key
    for key, value in conventional_types.items():
        for v in value:
            if v in message:
                return key
    return "others"


def get_context(username: str, token: str, year: int, time_zone: str) -> dict:
    """
    Generate context data for the given year from the provided data.

    Args:
        username (str): The GitHub username.
        token (str): The GitHub access token.
        year (int): The year to generate the context data.
        time_zone (str): The timezone.

    Returns:
        dict: The context data.
    """
    data = get_github_info(username, token, year)

    commit_type = [
        _get_commit_type(commit["message"])
        for _, detail in data["repo"].items()
        for commit in detail["commits"]
    ]
    commit_type_num = {k: commit_type.count(k) for k in set(commit_type)}
    if "others" in commit_type_num:
        commit_type_num.pop("others", None)

    commit_time = [
        datetime.fromisoformat(
            _parse_time(commit["committedDate"], pytz.timezone(time_zone))
        ).hour
        for _, detail in data["repo"].items()
        for commit in detail["commits"]
    ]
    commit_time_num = [0] * 24
    for hour in commit_time:
        commit_time_num[hour] += 1

    new_repos = [
        detail
        for _, detail in data["repo"].items()
        if datetime.fromisoformat(
            _parse_time(detail["createdAt"], pytz.timezone(time_zone))
        ).year
        == year
    ]
    language_in_new_repos = [
        language for repo in new_repos for language in repo["languages"]
    ]
    language_in_new_repos_count = {
        k: language_in_new_repos.count(k) for k in set(language_in_new_repos)
    }

    pattern = (
        r"https://private-avatars\.githubusercontent\.com/u/(\d+)\?[^&]+&[^&]+&v=(\d+)"
    )
    replacement = r"https://avatars.githubusercontent.com/u/\1?v=\2"

    # Avatar URL
    avatar = re.sub(pattern, replacement, data["basic"]["avatar_url"])
    # Username
    name = username
    if data["basic"]["name"]:
        name = data["basic"]["name"]
    # Days since account creation
    created_time = (
        (
            (
                datetime.now()
                - datetime.strptime(data["basic"]["created_time"], "%Y-%m-%dT%H:%M:%SZ")
            ).days
            + 99
        )
        // 100
        * 100
    )
    # Number of followers
    followers_num = data["basic"]["follower"]
    # Number of following
    following_num = data["basic"]["following"]
    # Number of stargazers
    stars_num = sum(detail["stargazerCount"] for _, detail in data["repo"].items())

    # Number of activities in each day
    commits_per_day = data["contribution"]["contribution"]
    # Number of days with activities
    commits_days_num = len([x for x in commits_per_day if x > 0])
    # Longest active streak
    longest_commit_streak = max(
        (len(list(g)) for k, g in groupby(commits_per_day, key=lambda x: x > 0) if k),
        default=0,
    )
    # Longest inactive streak
    longest_commit_break = max(
        (len(list(g)) for k, g in groupby(commits_per_day, key=lambda x: x == 0) if k),
        default=0,
    )
    # Maximum number of activities in a day
    max_commits_per_day = max(commits_per_day)

    days_in_month = [calendar.monthrange(year, month)[1] for month in range(1, 13)]
    # Number of activities in each month
    commits_per_month = [
        sum(commits_per_day[sum(days_in_month[:i]) : sum(days_in_month[: i + 1])])
        for i in range(12)
    ]
    # Most active month
    most_active_month = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ][commits_per_month.index(max(commits_per_month))]

    days_in_year = 366 if calendar.isleap(year) else 365
    # Number of activities in each weekday
    commits_per_weekday = [0] * 7
    for i in range(days_in_year):
        commits_per_weekday[
            (datetime(year, 1, 1) + timedelta(days=i)).weekday()
        ] += commits_per_day[i]
    # Most active weekday
    most_active_weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][
        commits_per_weekday.index(max(commits_per_weekday))
    ]

    # Number of activities in each hour
    commits_per_hour = commit_time_num
    # Most active hour
    most_active_hour = [f"{i}:00" for i in range(24)][
        commits_per_hour.index(max(commits_per_hour))
    ]

    # Number of commits
    commits_num = data["contribution"]["commit_num"]
    # Number of issues
    issues_num = data["contribution"]["issue_num"]
    # Number of pull requests
    prs_num = data["contribution"]["pr_num"]

    # Number of repositories
    repos_num = len(data["repo"])
    # Top 3 most committed repositories
    top_3_most_committed_repos = sorted(
        [
            {"name": repo, "num": len(detail["commits"])}
            for repo, detail in data["repo"].items()
        ],
        key=lambda x: x["num"],
        reverse=True,
    )[: min(3, repos_num)]

    # Number of languages used in new repositories
    languages_num = len(set(language_in_new_repos))
    # Top 3 languages used in new repositories
    top_3_languages_used_in_new_repos = sorted(
        [{"name": k, "num": v} for k, v in language_in_new_repos_count.items()],
        key=lambda x: x["num"],
        reverse=True,
    )[: min(3, languages_num)]

    # Number of conventional commits
    conventional_commits_num = sum(commit_type_num.values())
    # Top 3 conventional commit types
    top_3_conventional_commit_types = sorted(
        [{"name": k, "num": v} for k, v in commit_type_num.items()],
        key=lambda x: x["num"],
        reverse=True,
    )[: min(3, len(commit_type_num))]

    return {
        "avatar": avatar,
        "year": year,
        "username": username,
        "name": name,
        "created_time": created_time,
        "followers_num": followers_num,
        "following_num": following_num,
        "stars_num": stars_num,
        "commits_per_day": commits_per_day,
        "commits_days_num": commits_days_num,
        "longest_commit_streak": longest_commit_streak,
        "longest_commit_break": longest_commit_break,
        "max_commits_per_day": max_commits_per_day,
        "commits_per_month": commits_per_month,
        "most_active_month": most_active_month,
        "commits_per_weekday": commits_per_weekday,
        "most_active_weekday": most_active_weekday,
        "commits_per_hour": commits_per_hour,
        "most_active_hour": most_active_hour,
        "commits_num": commits_num,
        "issues_num": issues_num,
        "prs_num": prs_num,
        "repos_num": repos_num,
        "top_3_most_committed_repos": top_3_most_committed_repos,
        "languages_num": languages_num,
        "top_3_languages_used_in_new_repos": top_3_languages_used_in_new_repos,
        "conventional_commits_num": conventional_commits_num,
        "top_3_conventional_commit_types": top_3_conventional_commit_types,
    }
