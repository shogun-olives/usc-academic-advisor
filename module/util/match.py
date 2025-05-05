from .dept_info import get_depts
import difflib
import re


def fuzzy_match_dept(dept: str) -> str | None:
    """
    Fuzzy match a department name or code to a valid department code.

    Args:
        dept (str): The department name or code (e.g., "Computer Science" or "CSCI").

    Returns:
        output (str | None): The department code (e.g., "CSCI") or None if the department is not found.

    Examples:
        ```
        # Fuzzy match department name
        dept_code = fuzzy_match_dept("Computer Science")
        print(dept_code)  # Output: "CSCI"

        # Fuzzy match department name
        dept_code = fuzzy_match_dept("Compute Scienc")
        print(dept_code)  # Output: "CSCI"

        # Fuzzy match department code
        dept_code = fuzzy_match_dept("CSCI")
        print(dept_code)  # Output: "CSCI"

        dept_code = fuzzy_match_dept("CSCU")
        print(dept_code)  # Output: "CSCI"
        ```
    """
    # format dept
    dept = dept.strip().lower()
    dept_dict = get_depts(code_is_key=False)
    codes, names = list(dept_dict.values()), list(dept_dict.keys())
    all_options = set(codes + names)

    # Fuzzy match the department name or code
    match = difflib.get_close_matches(dept, all_options, n=1, cutoff=0.5)

    # No match found
    if not match:
        return None

    # Match is a code
    if match[0] in codes:
        return match[0].upper()

    # Match is a name
    if match[0] in names:
        return dept_dict[match[0]].upper()


def fuzzy_match_course(course: str) -> str | None:
    """
    Fuzzy match a course code to a valid course code.

    Args:
            course (str): The course code (e.g., "CSCI 100" or "CSCI100").

    Returns:
        output (str | None): The course code (e.g., "CSCI 100") or None if the course is not found.

    Examples:
        ```
        # Fuzzy match course code
        course_code = fuzzy_match_course("CSCI 100")
        print(course_code)  # Output: "CSCI 100"

        # Fuzzy match course code
        course_code = fuzzy_match_course("CSCI100")
        print(course_code)  # Output: "CSCI 100"

        # Fuzzy match course code
        course_code = fuzzy_match_course("CSCI 101")
        print(course_code)  # Output: "CSCI 101"

        # Fuzzy match course code
        course_code = fuzzy_match_course("CSCU 101")
        print(course_code)  # Output: "CSCI 101"
        ```
    """
    # Format course
    course = course.strip().upper().replace(" ", "")

    # Match course using regex
    match = re.match(r"([A-Z]{2,4})0*([0-9]{1,3}[A-Z]?)", course)

    # If no match found, return None
    if not match:
        return None

    # Fuzzy match the department code
    dept = fuzzy_match_dept(match.group(1))

    # If the department code is not found, return None
    if dept is None:
        return None

    # Otherwise, return matched course
    return f"{dept} {match.group(2)}"
