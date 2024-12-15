import re
from datetime import datetime, timedelta


def _get_commit_type(message: str) -> str:
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


def commits_number(data):
    commits_number = 0
    for repo in data["repos_details"]:
        repo["commits_num"] = len(repo["commits_details"])
        commits_number += len(repo["commits_details"])

    data["commits_num"] = commits_number

    return data


def commits_types_number(data):
    commits_types = {}
    for repo in data["repos_details"]:
        repo_commits_types = {}
        for commit in repo["commits_details"]:
            commit_type = _get_commit_type(commit["message"])

            if commit_type in repo_commits_types:
                repo_commits_types[commit_type] += 1
            else:
                repo_commits_types[commit_type] = 1

        repo["commits_types_num"] = repo_commits_types

        for key, value in repo_commits_types.items():
            if key in commits_types:
                commits_types[key] += value
            else:
                commits_types[key] = value

    data["commits_types_num"] = commits_types

    return data


def commits_monthly_number(data):
    commits_monthly = {}
    for repo in data["repos_details"]:
        repo_commits_monthly = {}
        for commit in repo["commits_details"]:
            commit_month = datetime.fromisoformat(commit["created_time"]).month

            if commit_month in repo_commits_monthly:
                repo_commits_monthly[commit_month] += 1
            else:
                repo_commits_monthly[commit_month] = 1
            if commit_month in commits_monthly:
                commits_monthly[commit_month] += 1
            else:
                commits_monthly[commit_month] = 1

        repo_commits_monthly_list = []
        for i in range(1, 13):
            if i in repo_commits_monthly:
                repo_commits_monthly_list.append(repo_commits_monthly[i])
            else:
                repo_commits_monthly_list.append(0)
        repo["commits_monthly_num"] = repo_commits_monthly_list

    commits_monthly_list = []
    for i in range(1, 13):
        if i in commits_monthly:
            commits_monthly_list.append(commits_monthly[i])
        else:
            commits_monthly_list.append(0)
    data["commits_monthly_num"] = commits_monthly_list

    return data


def commits_weekdaily_number(data):
    commits_weekly = {}
    for repo in data["repos_details"]:
        repo_commits_weekly = {}
        for commit in repo["commits_details"]:
            commit_weekday = datetime.fromisoformat(commit["created_time"]).weekday()

            if commit_weekday in repo_commits_weekly:
                repo_commits_weekly[commit_weekday] += 1
            else:
                repo_commits_weekly[commit_weekday] = 1
            if commit_weekday in commits_weekly:
                commits_weekly[commit_weekday] += 1
            else:
                commits_weekly[commit_weekday] = 1

        repo_commits_weekly_list = []
        for i in range(7):
            if i in repo_commits_weekly:
                repo_commits_weekly_list.append(repo_commits_weekly[i])
            else:
                repo_commits_weekly_list.append(0)
        repo["commits_weekdaily_num"] = repo_commits_weekly_list

    commits_weekly_list = []
    for i in range(7):
        if i in commits_weekly:
            commits_weekly_list.append(commits_weekly[i])
        else:
            commits_weekly_list.append(0)
    data["commits_weekdaily_num"] = commits_weekly_list

    return data


def commits_daily_number(data):
    commits_daily = {}
    for repo in data["repos_details"]:
        repo_commits_daily = {}
        for commit in repo["commits_details"]:
            commit_date = (
                datetime.fromisoformat(commit["created_time"]).date().isoformat()
            )

            if commit_date in repo_commits_daily:
                repo_commits_daily[commit_date] += 1
            else:
                repo_commits_daily[commit_date] = 1
            if commit_date in commits_daily:
                commits_daily[commit_date] += 1
            else:
                commits_daily[commit_date] = 1

        repo_commmits_daily_list = {}

        for i in range(2000, datetime.now().year + 2):
            days_in_year = 366 if i % 4 == 0 and i % 100 != 0 or i % 400 == 0 else 365
            tmp = []
            for j in range(0, days_in_year):
                date = (datetime(i, 1, 1) + timedelta(days=j)).date().isoformat()
                if date in repo_commits_daily:
                    tmp.append(repo_commits_daily[date])
                else:
                    tmp.append(0)
            if sum(tmp) != 0:
                repo_commmits_daily_list[i] = tmp

        repo["commits_daily_num"] = repo_commmits_daily_list

    commits_daily_list = {}

    for i in range(2000, datetime.now().year + 2):
        days_in_year = 366 if i % 4 == 0 and i % 100 != 0 or i % 400 == 0 else 365
        tmp = []
        for j in range(0, days_in_year):
            date = (datetime(i, 1, 1) + timedelta(days=j)).date().isoformat()
            if date in commits_daily:
                tmp.append(commits_daily[date])
            else:
                tmp.append(0)
        if sum(tmp) != 0:
            commits_daily_list[i] = tmp

    data["commits_daily_num"] = commits_daily_list

    return data


def commits_hourly_number(data):
    commits_hourly = {}
    for repo in data["repos_details"]:
        repo_commits_hourly = {}
        for commit in repo["commits_details"]:
            commit_hour = datetime.fromisoformat(commit["created_time"]).hour

            if commit_hour in repo_commits_hourly:
                repo_commits_hourly[commit_hour] += 1
            else:
                repo_commits_hourly[commit_hour] = 1
            if commit_hour in commits_hourly:
                commits_hourly[commit_hour] += 1
            else:
                commits_hourly[commit_hour] = 1

        repo_commits_hourly_list = []
        for i in range(24):
            if i in repo_commits_hourly:
                repo_commits_hourly_list.append(repo_commits_hourly[i])
            else:
                repo_commits_hourly_list.append(0)
        repo["commits_hourly_num"] = repo_commits_hourly_list

    commits_hourly_list = []
    for i in range(24):
        if i in commits_hourly:
            commits_hourly_list.append(commits_hourly[i])
        else:
            commits_hourly_list.append(0)
    data["commits_hourly_num"] = commits_hourly_list

    return data


def repos_number(data):
    repos_number = len(data["repos_details"])
    data["repos_num"] = repos_number

    return data


def repos_languages_number(data):
    languages_num = {}
    repos_languages_count = {}
    for repo in data["repos_details"]:
        for key, value in repo["languages_num"].items():
            if key in languages_num:
                languages_num[key] += value
                repos_languages_count[key] += 1
            else:
                languages_num[key] = value
                repos_languages_count[key] = 1

        repo["languages_num"] = dict(
            sorted(repo["languages_num"].items(), key=lambda x: x[1], reverse=True)
        )

    data["languages_num"] = languages_num
    data["languages_num"] = dict(
        sorted(data["languages_num"].items(), key=lambda x: x[1], reverse=True)
    )

    data["repos_languages_num"] = repos_languages_count
    data["repos_languages_num"] = dict(
        sorted(data["repos_languages_num"].items(), key=lambda x: x[1], reverse=True)
    )

    return data


def repos_stargazer_number(data):
    stargazers_num = 0
    for repo in data["repos_details"]:
        stargazers_num += repo["stargazers_num"]

    data["stargazers_num"] = stargazers_num

    return data


def repos_fork_number(data):
    forks_num = 0
    for repo in data["repos_details"]:
        forks_num += repo["forks_num"]

    data["forks_num"] = forks_num

    return data


def prs_number(data):
    prs_number = len(data["prs_details"])
    data["prs_num"] = prs_number

    return data


def prs_merged_number(data):
    merged_prs_number = len(list(filter(lambda x: x["merged"], data["prs_details"])))
    data["prs_merged_num"] = merged_prs_number

    return data


def issues_number(data):
    issues_number = len(data["issues_details"])
    data["issues_num"] = issues_number

    return data


def stars_number(data):
    stars_number = len(data["stars_details"])
    data["stars_num"] = stars_number

    return data
