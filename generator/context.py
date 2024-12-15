from itertools import groupby

# from pprint import pprint


def get_context(year: int, data: dict, data_new_repo: dict) -> dict:
    # pprint(data)

    YEAR = year
    AVATAR = data["account_info"]["avatar"]
    USERNAME = data["account_info"]["username"]
    NAME = data["account_info"]["name"]
    CREATED_TIME = (int(data["account_info"]["created_time"]) + 99) // 100 * 100
    FOLLOWERS_NUM = data["account_info"]["followers_num"]
    FOLLOWING_NUM = data["account_info"]["following_num"]
    STARS_NUM = data["stargazers_num"]

    COMMITS_PER_DAY = data["commits_daily_num"][year]
    COMMITS_DAYS_NUM = len([x for x in COMMITS_PER_DAY if x > 0])
    LONGEST_COMMIT_STREAK = max(
        (len(list(g)) for k, g in groupby(COMMITS_PER_DAY) if k > 0), default=0
    )
    LONGEST_COMMIT_BREAK = max(
        (len(list(g)) for k, g in groupby(COMMITS_PER_DAY) if k == 0), default=0
    )
    MAX_COMMITS_PER_DAY = max(COMMITS_PER_DAY)

    COMMITS_PER_MONTH = data["commits_monthly_num"]
    MOST_ACTIVE_MONTH = [
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
    ][COMMITS_PER_MONTH.index(max(COMMITS_PER_MONTH))]
    COMMITS_PER_WEEKDAY = data["commits_weekdaily_num"]
    MOST_ACTIVE_WEEKDAY = [
        "Mon",
        "Tue",
        "Wed",
        "Thu",
        "Fri",
        "Sat",
        "Sun",
    ][COMMITS_PER_WEEKDAY.index(max(COMMITS_PER_WEEKDAY))]
    COMMITS_PER_HOUR = data["commits_hourly_num"]
    MOST_ACTIVE_HOUR = [f"{i}:00" for i in range(24)][
        COMMITS_PER_HOUR.index(max(COMMITS_PER_HOUR))
    ]

    COMMITS_NUM = data["commits_num"]
    ISSUES_NUM = data["issues_num"]
    PRS_NUM = data["prs_num"]

    REPOS_NUM = data["repos_num"]
    TOP_3_MOST_COMMITTED_REPOS = sorted(
        [
            {"name": repo["name"], "num": repo["commits_num"]}
            for repo in data["repos_details"]
        ],
        key=lambda x: x["num"],
        reverse=True,
    )[: min(3, len(data["repos_details"]))]
    LANGUAGES_NUM = len(data_new_repo["languages_num"])
    TOP_3_LANGUAGES_USED_IN_NEW_REPOS = list(
        [{"name": k, "num": v} for k, v in data_new_repo["languages_num"].items()],
    )[: min(3, len(data_new_repo["languages_num"]))]
    CONVENTIONAL_COMMITS_NUM = sum(
        [v for k, v in data["commits_types_num"].items() if k != "others"]
    )
    TOP_3_CONVENTIONAL_COMMIT_TYPES = sorted(
        [
            {"name": k, "num": v}
            for k, v in data["commits_types_num"].items()
            if k != "others"
        ],
        key=lambda x: x["num"],
        reverse=True,
    )[: min(3, len(data["commits_types_num"]) - 1)]

    return {
        "AVATAR": AVATAR,
        "YEAR": YEAR,
        "USERNAME": USERNAME,
        "NAME": NAME,
        "CREATED_TIME": CREATED_TIME,
        "FOLLOWERS_NUM": FOLLOWERS_NUM,
        "FOLLOWING_NUM": FOLLOWING_NUM,
        "STARS_NUM": STARS_NUM,
        "COMMITS_PER_DAY": COMMITS_PER_DAY,
        "COMMITS_DAYS_NUM": COMMITS_DAYS_NUM,
        "LONGEST_COMMIT_STREAK": LONGEST_COMMIT_STREAK,
        "LONGEST_COMMIT_BREAK": LONGEST_COMMIT_BREAK,
        "MAX_COMMITS_PER_DAY": MAX_COMMITS_PER_DAY,
        "COMMITS_PER_MONTH": COMMITS_PER_MONTH,
        "MOST_ACTIVE_MONTH": MOST_ACTIVE_MONTH,
        "COMMITS_PER_WEEKDAY": COMMITS_PER_WEEKDAY,
        "MOST_ACTIVE_WEEKDAY": MOST_ACTIVE_WEEKDAY,
        "COMMITS_PER_HOUR": COMMITS_PER_HOUR,
        "MOST_ACTIVE_HOUR": MOST_ACTIVE_HOUR,
        "COMMITS_NUM": COMMITS_NUM,
        "ISSUES_NUM": ISSUES_NUM,
        "PRS_NUM": PRS_NUM,
        "REPOS_NUM": REPOS_NUM,
        "TOP_3_MOST_COMMITTED_REPOS": TOP_3_MOST_COMMITTED_REPOS,
        "LANGUAGES_NUM": LANGUAGES_NUM,
        "TOP_3_LANGUAGES_USED_IN_NEW_REPOS": TOP_3_LANGUAGES_USED_IN_NEW_REPOS,
        "CONVENTIONAL_COMMITS_NUM": CONVENTIONAL_COMMITS_NUM,
        "TOP_3_CONVENTIONAL_COMMIT_TYPES": TOP_3_CONVENTIONAL_COMMIT_TYPES,
    }
