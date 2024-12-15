import requests
from datetime import datetime
from typing import Dict, List, Tuple, Any
import urllib.parse
import pytz

URL = str
JSON = Dict[str, Any] | List[Dict[str, Any]]


def _parse_time(time: str, timezone: str) -> str:
    return (
        datetime.strptime(time, "%Y-%m-%dT%H:%M:%SZ")
        .replace(tzinfo=pytz.UTC)
        .astimezone(timezone)
        .isoformat()
    )


def _paginate(func: callable) -> callable:
    def wrapper(username: str, url: URL, token: str, timezone: str) -> JSON:
        results = []
        while url:
            data, res = func(username, url, token, timezone)
            if data:
                results.extend(data)
            links = res.headers.get("Link")
            if links:
                next_url = None
                for link in links.split(","):
                    if 'rel="next"' in link:
                        next_url = link[link.find("<") + 1 : link.find(">")]
                        break
                url = next_url
            else:
                url = None
        return results

    return wrapper


def _get_response(
    url: URL,
    token: str,
    per_page: int = 100,
    accept: str = "application/vnd.github.v3+json",
) -> requests.Response:
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": accept,
    }

    parsed_url = urllib.parse.urlparse(url)
    query_params = urllib.parse.parse_qs(parsed_url.query)
    query_params["per_page"] = str(per_page)
    new_query_string = urllib.parse.urlencode(query_params, doseq=True)
    url = urllib.parse.urlunparse(parsed_url._replace(query=new_query_string))

    print(f"Fetching data from {url}...")

    response = requests.get(url, headers=headers)
    if response.status_code == 409:  # Empty repository
        return response

    response.raise_for_status()

    return response


def get_github_info(username: str, token: str, timezone: str) -> JSON:
    user_url = f"https://api.github.com/users/{username}"
    response = _get_response(user_url, token)
    data = response.json()

    created_time = (
        datetime.now() - datetime.strptime(data.get("created_at"), "%Y-%m-%dT%H:%M:%SZ")
    ).days

    isssues_url = f"https://api.github.com/search/issues?q=author:{username}+type:issue"
    issues_details = _get_user_issues(
        username=username, url=isssues_url, token=token, timezone=timezone
    )

    prs_url = f"https://api.github.com/search/issues?q=author:{username}+type:pr"
    prs_details = _get_user_prs(
        username=username, url=prs_url, token=token, timezone=timezone
    )

    repos_url = f"https://api.github.com/user/repos"
    repos_details = _get_user_repos(
        username=username, url=repos_url, token=token, timezone=timezone
    )

    stars_url = data.get("starred_url").replace("{/owner}{/repo}", "")
    stars_details = _get_user_stars(
        username=username, url=stars_url, token=token, timezone=timezone
    )

    return {
        "account_info": {
            "url": data.get("html_url"),
            "name": data.get("name"),
            "username": data.get("login"),
            "avatar": data.get("avatar_url"),
            "bio": data.get("bio"),
            "followers_num": data.get("followers"),
            "following_num": data.get("following"),
            "created_time": created_time,
        },
        "issues_details": issues_details,
        "prs_details": prs_details,
        "repos_details": repos_details,
        "stars_details": stars_details,
    }


@_paginate
def _get_user_issues(
    username: str, issues_url: URL, token: str, timezone: str
) -> Tuple[JSON, requests.Response]:
    response = _get_response(issues_url, token)
    if response.status_code == 409:
        return [], response
    issues = response.json().get("items")

    issues_details = []

    for issue in issues:
        created_time = _parse_time(issue.get("created_at"), timezone)

        issues_details.append(
            {
                "url": issue.get("html_url"),
                "title": issue.get("title"),
                "body": issue.get("body"),
                "state": issue.get("state"),
                "created_time": created_time,
            }
        )

    return issues_details, response


@_paginate
def _get_user_prs(
    username: str, prs_url: URL, token: str, timezone: str
) -> Tuple[JSON, requests.Response]:
    response = _get_response(prs_url, token)
    if response.status_code == 409:
        return [], response
    prs = response.json().get("items")

    prs_details = []

    for pr in prs:
        created_time = _parse_time(pr.get("created_at"), timezone)

        if pr.get("pull_request").get("merged_at"):
            merged = True
            merged_time = _parse_time(pr.get("pull_request").get("merged_at"), timezone)
        else:
            merged = False
            merged_time = None

        prs_details.append(
            {
                "url": pr.get("html_url"),
                "title": pr.get("title"),
                "body": pr.get("body"),
                "state": pr.get("state"),
                "created_time": created_time,
                "merged": merged,
                "merged_time": merged_time,
            }
        )

    return prs_details, response


@_paginate
def _get_user_stars(
    username: str, stars_url: URL, token: str, timezone: str
) -> Tuple[JSON, requests.Response]:
    response = _get_response(
        stars_url, token, accept="application/vnd.github.v3.star+json"
    )
    if response.status_code == 409:
        return [], response
    stars = response.json()

    stars_details = []

    for star in stars:
        starred_time = _parse_time(star.get("starred_at"), timezone)

        stars_details.append(
            {
                "url": star.get("repo").get("html_url"),
                "name": star.get("repo").get("full_name"),
                "created_time": starred_time,
            }
        )

    return stars_details, response


@_paginate
def _get_user_repos(
    username: str, repos_url: URL, token: str, timezone: str
) -> Tuple[JSON, requests.Response]:
    response = _get_response(repos_url, token)
    if response.status_code == 409:
        return [], response
    repos = response.json()

    repos_details = []

    for repo in repos:
        if repo.get("fork"):
            continue

        language_url = repo.get("languages_url")
        languages_details = _get_user_repo_languages(
            language_url, token=token, timezone=timezone
        )

        commits_url = repo.get("commits_url").replace("{/sha}", "")
        commits_details = _get_user_commits(
            username=username, url=commits_url, token=token, timezone=timezone
        )

        repos_details.append(
            {
                "url": repo.get("html_url"),
                "name": repo.get("name"),
                "description": repo.get("description"),
                "created_time": repo.get("created_at"),
                "stargazers_num": repo.get("stargazers_count"),
                "forks_num": repo.get("forks_count"),
                "languages_num": languages_details,
                "commits_details": commits_details,
            }
        )

    return repos_details, response


def _get_user_repo_languages(language_url: URL, token: str, timezone: str) -> JSON:
    response = _get_response(language_url, token)
    response.raise_for_status()
    languages_details = response.json()

    return languages_details


@_paginate
def _get_user_commits(
    username: str, commits_url: URL, token: str, timezone: str
) -> Tuple[JSON, requests.Response]:
    response = _get_response(commits_url, token)
    if response.status_code == 409:
        return [], response
    response.raise_for_status()
    commits = response.json()

    commits_details = []

    for commit in commits:
        # print(json.dumps(commit, indent=4))
        committer = None
        try:
            committer = commit.get("committer").get("login")
        except:
            committer = commit.get("commit").get("committer").get("name")
        if committer == username:
            commit_message = commit.get("commit").get("message")

            commit_time = _parse_time(
                commit.get("commit").get("committer").get("date"), timezone
            )

            commits_details.append(
                {
                    "message": commit_message,
                    "created_time": commit_time,
                }
            )

    return commits_details, response
