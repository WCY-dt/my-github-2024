from datetime import datetime


def _filter_year(data, key: str, year: int):
    return list(filter(lambda x: datetime.fromisoformat(x[key]).year == year, data))


def commits_year(data, year: int):
    for repo in data["repos_details"]:
        repo["commits_details"] = _filter_year(
            repo["commits_details"], "created_time", year
        )

    data["repos_details"] = list(
        filter(lambda x: len(x["commits_details"]) > 0, data["repos_details"])
    )

    return data


def repos_year(data, year: int):
    data["repos_details"] = _filter_year(data["repos_details"], "created_time", year)

    return data


def issues_year(data, year: int):
    data["issues_details"] = _filter_year(data["issues_details"], "created_time", year)

    return data


def prs_year(data, year: int):
    data["prs_details"] = _filter_year(data["prs_details"], "created_time", year)

    return data


def stars_year(data, year: int):
    data["stars_details"] = _filter_year(data["stars_details"], "created_time", year)

    return data


def json_key(data, key: dict):
    if isinstance(data, list):
        return [json_key(x, key) for x in data]

    json_key_result = {}

    for k, v in key.items():
        if k not in data:
            raise KeyError(f"KeyError: {k} not found in {data}")

        if isinstance(v, dict):
            json_key_result[k] = json_key(data[k], v)
        else:
            json_key_result[k] = data[k]

    return json_key_result
