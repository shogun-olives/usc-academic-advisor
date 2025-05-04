from .format import conv_term
from .scrape import scrape
import urllib


def get_depts(
    term: str = None,
    as_lower: bool = True,
    code_is_key: bool = True,
) -> dict[str, str]:
    """
    Gets the departments from the USC website for a given term.

    Args:
        term (str): The term object containing the information as a code (ex: 20253 or Fall 2023). (default: None)
        as_lower (bool): If True, the department names and codes will be converted to lowercase. (default: True)
        code_is_key (bool): If True, the department code will be used as the key in the returned dictionary. (default: False)

    Returns:
        out (dict[str, str]): A dictionary containing the department names and their codes.

    Examples:
        ```
        # Get departments with department code as key
        # csci: computer science
        # math: mathematics
        departments = get_depts()
        print(departments)

        # Get departments with department name as key
        # computer science: csci
        # mathematics: math
        departments = get_depts(code_is_key=False)
        print(departments)

        # Get departments in original case
        # CSCI: Computer Science
        # MATH: Mathematics
        departments = get_depts(as_lower=False)
        print(departments)
        ```
    """
    # Set the term to the upcoming term if not provided]
    term = conv_term(term)

    # Get the soup object for the given term
    url = f"https://classes.usc.edu/term-{term}/"

    # Check if the term is listed yet
    try:
        soup = scrape(url)
    except urllib.error.HTTPError:
        raise ValueError(
            f"{term} not found. It is likely courses for this semester have not yet been listed."
        )

    # Find the department list in the soup object
    departments = {}
    for row in soup.find_all("li"):
        if row.get("data-type", None) != "department":
            continue
        name = row["data-title"]
        code = row["data-code"]

        if as_lower:
            name = name.lower()
            code = code.lower()

        if code_is_key:
            departments[code] = name
        else:
            departments[name] = code

    return departments


# This function really should be in format.py,
# but due to creating a circular import, it is here.
def conv_dept(dept: str, lower: bool = False) -> str | None:
    """
    Convert a department to a code.

    Args:
        dept (str): The department name or code (e.g., "Computer Science" or "CSCI").
        lower (bool): If True, the department code will be converted to lowercase. (default: False)

    Returns:
        out (str | None): The department code (e.g., "CSCI") or None if the department is not found.

    Examples:
        ```
        # Department: Computer Science
        dept = dept_code("Computer Science")
        print(dept)  # Output: "CSCI"

        dept = dept_code("CSCI")
        print(dept)  # Output: "CSCI"
        ```
    """
    departments = get_depts(code_is_key=False)
    dept = dept.lower()

    if dept in departments.keys():
        # Department name format (e.g., "Computer Science")
        return departments[dept] if lower else departments[dept].upper()

    if dept.lower() in departments.values():
        # Department code format (e.g., "CSCI")
        return dept if lower else dept.upper()

    # If the department is not found, return None
    return None
