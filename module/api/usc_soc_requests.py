from ..util import dept_code, term_code
import requests


def call_usc_api(dept: str, term: int | str) -> dict:
    """
    Call the USC API to get course data for a specific department and term.

    Args:
        dept (str): The department code (e.g., "CSCI").
        term (int | str): The term code (e.g., "20253" or "Fall 2025").

    Returns:
        output (dict): The JSON response from the API containing course data.

    Examples:
        ```
        # Call the USC API for a specific department and term
        data = call_usc_api("CSCI", "20253")
        data = call_usc_api("CSCI", "Fall 2025")
        data = call_usc_api("Computer Science", 20253)
        ```
    """
    dept = dept_code(dept)
    term = term_code(term)
    url = f"https://web-app.usc.edu/web/soc/api/classes/{dept}/{term}"
    return requests.get(url).json()
