import requests
import json
import os


def api_get_courses(
    dept_code: str,
    term_code: int | str,
    overwrite: bool = False,
) -> dict | None:
    """
    Call the USC API to get course data for a specific department and term.

    Args:
        dept_code (str): The department code (e.g., "CSCI").
        term_code (int | str): The term code (e.g., "20253" or 20253).
        overwrite (bool): If True, overwrite the cache. (default: False)

    Returns:
        output (dict | None): The JSON response from the API containing course data, or None if the request fails.

    Examples:
        ```
        # Call the USC API for a specific department and term
        data = call_usc_api("CSCI", "20253")
        data = call_usc_api("CSCI", 20253)
        ```
    """
    url = f"https://web-app.usc.edu/web/soc/api/classes/{dept_code}/{term_code}"
    fn = f"./data/cache/api/{dept_code}_{term_code}.json"

    if overwrite or not os.path.exists(fn) or os.path.getsize(fn) == 0:
        os.makedirs(os.path.dirname(fn), exist_ok=True)
        with open(fn, "w", encoding="utf-8") as f:
            response = requests.get(url)
            if response.status_code == 200:
                json.dump(response.json(), f, indent=4)
            else:
                return None

    with open(fn, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data
