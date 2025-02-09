"""
This module provides functions to fetch GitHub data using the GitHub GraphQL API.

Functions:
    get_github_info(username: str, token: str, year: int) -> dict:
        Get the GitHub information for the given year.
"""

import logging

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from log.logging_config import setup_logging

setup_logging()


@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=64))
def _graphql_query(query: str, variables: dict, token: str) -> dict:
    url = "https://api.github.com/graphql"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    response = requests.post(
        url, json={"query": query, "variables": variables}, headers=headers, timeout=10
    )
    response.raise_for_status()
    return response.json()["data"]


def _get_basic(user_name: str, token: str) -> dict:
    query = """
    query($username: String!) {
        user(login: $username) {
            id
            name
            avatarUrl
            followers {
                totalCount
            }
            following {
                totalCount
            }
            createdAt
        }
    }
    """

    variables = {
        "username": user_name,
    }

    result = _graphql_query(query, variables, token)["user"]

    return {
        "id": result["id"],
        "name": result["name"],
        "avatar_url": result["avatarUrl"],
        "follower": result["followers"]["totalCount"],
        "following": result["following"]["totalCount"],
        "created_time": result["createdAt"],
    }


def _get_repo(
    user_name: str, user_id: str, token: str, year: int, interval: int
) -> dict:

    query = """
    query($username: String!, $id: ID!, $since: GitTimestamp!, $until: GitTimestamp!, $after: String) {
        user(login: $username) {
            repositories(first: %d, after: $after) {
                nodes {
                    name
                    stargazerCount
                    forkCount
                    isPrivate
                    isFork
                    createdAt
                    languages(first: 100) {
                        nodes {
                            name
                        }
                    }
                    defaultBranchRef {
                        target {
                            ... on Commit {
                                history(first: 100, since: $since, until: $until, author: {id: $id}) {
                                    nodes {
                                        message
                                        committedDate
                                    }
                                    pageInfo{
                                        hasNextPage
                                        startCursor
                                        endCursor
                                    }
                                }
                            }
                        }
                    }
                }
                pageInfo{
                    hasNextPage
                    startCursor
                    endCursor
                }
            }
        }
    }
    """ % (
        interval
    )

    start_time = f"{year}-01-01T00:00:00Z"
    end_time = f"{year}-12-31T23:59:59Z"

    variables = {
        "username": user_name,
        "id": user_id,
        "since": start_time,
        "until": end_time,
        "after": None,
    }

    all_repos = {}

    while True:
        result = _graphql_query(query, variables, token)

        user = result.get("user")
        if not user:
            raise ValueError("`user` not in result")

        repositories = user.get("repositories")
        if not repositories:
            raise ValueError("`repositories` not in result")

        nodes = repositories.get("nodes")
        if not nodes:
            nodes = []

        if not nodes:
            break

        for repo in nodes:
            repo_name = repo.get("name")
            if not repo_name:
                raise ValueError("`name` not in repo")

            default_branch_ref = repo.get("defaultBranchRef")
            if not default_branch_ref:
                continue

            history = default_branch_ref.get("target").get("history")
            if not history:
                raise ValueError("`history` not in repo['defaultBranchRef']['target']")

            nodes = history.get("nodes")
            if not nodes:
                nodes = []

            commits = nodes

            page_info = history.get("pageInfo")

            has_next_page = page_info.get("hasNextPage")
            if has_next_page:
                end_cursor = page_info.get("endCursor")
                if not end_cursor:
                    raise ValueError(
                        "`endCursor` not in repo['defaultBranchRef']['target']"
                        "['history']['pageInfo']"
                    )

                commit_after = end_cursor

                while True:
                    tryTimes = 0
                    commit_result = None
                    while tryTimes < 3:
                        try:
                            commit_result = _get_commit(
                                user_name, user_id, token, year, repo_name, commit_after
                            )

                            commit_user = commit_result.get("user")
                            if not commit_user:
                                raise ValueError("`user` not in commit_result")

                            repository = commit_user.get("repository")
                            if not repository:
                                logging.error("`repository` not in commit_user")
                                commit_result = None
                                break

                            default_branch_ref = repository.get("defaultBranchRef")
                            if not default_branch_ref:
                                raise ValueError("`defaultBranchRef` not in repository")

                            if commit_result["user"]["repository"]["defaultBranchRef"][
                                "target"
                            ]["history"]:
                                break
                        except Exception as e:
                            logging.error(
                                "Unexpected error: Failed to get commit info: %s.",
                                e,
                            )
                            tryTimes += 1

                    if not commit_result:
                        break

                    commit_result = commit_result["user"]["repository"][
                        "defaultBranchRef"
                    ]["target"]["history"]

                    if commit_result["nodes"]:
                        commits.extend(commit_result["nodes"])

                    if not commit_result["pageInfo"]["hasNextPage"]:
                        break

                    commit_after = commit_result["pageInfo"]["endCursor"]

            languages = []
            try:
                if repo.get("languages").get("nodes"):
                    languages = [lang["name"] for lang in repo["languages"]["nodes"]]
            except Exception as e:
                logging.error(
                    "Unexpected error: Failed to get languages info: %s.",
                    e,
                )

            all_repos[repo_name] = {
                "stargazerCount": repo["stargazerCount"],
                "forkCount": repo["forkCount"],
                "isPrivate": repo["isPrivate"],
                "isFork": repo["isFork"],
                "createdAt": repo["createdAt"],
                "languages": languages,
                "commits": commits,
            }

        if not result["user"]["repositories"]["pageInfo"]["hasNextPage"]:
            break

        variables["after"] = result["user"]["repositories"]["pageInfo"]["endCursor"]

    return all_repos


def _get_commit(
    user_name: str, user_id: str, token: str, year: int, repo_name: str, after: str
) -> dict:
    query = """
    query($username: String!, $id: ID!, $since: GitTimestamp!, $until: GitTimestamp!, $repo_name: String!, $after: String) {
        user(login: $username) {
            repository(name: $repo_name) {
                defaultBranchRef {
                    target {
                        ... on Commit {
                            history(first: 100, since: $since, until: $until, author: {id: $id}, after: $after) {
                                nodes {
                                    message
                                    committedDate
                                }
                                pageInfo{
                                    hasNextPage
                                    startCursor
                                    endCursor
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    """

    start_time = f"{year}-01-01T00:00:00Z"
    end_time = f"{year}-12-31T23:59:59Z"

    variables = {
        "username": user_name,
        "id": user_id,
        "since": start_time,
        "until": end_time,
        "repo_name": repo_name,
        "after": after,
    }

    return _graphql_query(query, variables, token)


def _get_contribution(user_name: str, token: str, year: int) -> dict:
    query = """
    query($username: String!, $from: DateTime!, $to: DateTime!) {
        user(login: $username) {
            contributionsCollection(from: $from, to: $to) {
                totalPullRequestContributions
                totalIssueContributions
                totalCommitContributions
                contributionCalendar {
                    totalContributions
                    weeks {
                        contributionDays {
                            contributionCount
                        }
                    }
                }
            }
        }
    }
    """

    start_time = f"{year}-01-01T00:00:00Z"
    end_time = f"{year}-12-31T23:59:59Z"

    variables = {
        "username": user_name,
        "from": start_time,
        "to": end_time,
    }

    result = _graphql_query(query, variables, token)["user"]["contributionsCollection"]

    pr_num = result["totalPullRequestContributions"]
    issue_num = result["totalIssueContributions"]
    commit_num = result["totalCommitContributions"]

    result_calendar = result["contributionCalendar"]

    contribution_num = result_calendar["totalContributions"]
    contribution = [
        day["contributionCount"]
        for week in result_calendar["weeks"]
        for day in week["contributionDays"]
    ]

    return {
        "pr_num": pr_num,
        "issue_num": issue_num,
        "commit_num": commit_num,
        "contribution_num": contribution_num,
        "contribution": contribution,
    }


def get_github_info(username: str, token: str, year: int) -> dict:
    """
    Get the GitHub information for the given year.

    Args:
        username (str): The GitHub username.
        token (str): The GitHub access token.
        year (int): The year to get the information.

    Returns:
        dict: The GitHub information.
    """

    logging.info("Processing basic info: username=%s", username)
    basic_info = _get_basic(username, token)
    if not basic_info["id"]:
        raise ValueError("Failed to get user id")

    user_id = basic_info["id"]

    interval = 10
    repo_info = None
    while not repo_info:
        try:
            logging.info(
                "Processing repo: username=%s, interval=%d", username, interval
            )
            repo_info = _get_repo(username, user_id, token, year, interval)
            if repo_info:
                break
        except Exception as e:
            logging.error(
                "Unexpected error: Failed to get repo info: %s. Trying to decrease the interval.",
                e,
            )
            interval = interval // 2

            if interval < 1:
                raise ValueError("Failed to get repo info") from e
        else:
            logging.error(
                "Unexpected error: Failed to get repo info. Trying to decrease the interval."
            )
            interval = interval // 2

            if interval < 1:
                raise ValueError("Failed to get repo info") from e

    logging.info("Processing contribution: username=%s", username)
    contribution_info = _get_contribution(username, token, year)

    return {
        "basic": basic_info,
        "repo": repo_info,
        "contribution": contribution_info,
    }
