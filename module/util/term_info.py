from datetime import datetime


def term_code(term: int | str = None) -> str:
    """
    Initialize a Term object.

    Args:
        term (int | str): The term name (e.g., "Fall 2025" "20253"). (default: None)

    Examples:
        ```
        # Term: Fall 2025
        term = Term("Fall 2025")
        term = Term("20253")

        # Finds next term
        term = Term()
        ```
    """
    # No term given, find the next term
    if term is None:
        today = datetime.now()

        # If the current month is Jan:          Spring of this year
        # If the current month is Feb - Aug:    Fall of this year
        # If the current month is Sep - Dec:    Spring of next year
        year = today.year + (1 if today.month >= 9 else 0)
        semester = 3 if today.month >= 2 and today.month <= 8 else 1

        # Convert to format 20253 (2025 Fall)
        return f"{year}{semester}"

    # convert to string if term is an int
    if isinstance(term, int):
        term = str(term)

    # Term ID format (e.g., "20253")
    if term.isdigit() and len(term) == 5:
        return term

    # Term name format (e.g., "Fall 2025")
    splt_term = term.split(" ")
    if (
        len(splt_term) == 2
        and splt_term[0].lower() in ["spring", "summer", "fall"]
        and splt_term[1].isdigit()
        and len(splt_term[1]) == 4
    ):
        year = int(splt_term[1])
        semester = {
            "spring": 1,
            "summer": 2,
            "fall": 3,
        }[splt_term[0].lower()]

        return f"{year}{semester}"

    # given term is not valid
    raise ValueError(
        f"Term '{term}' has an invalid format. Expected 'Fall 2025' or '20253' or None."
    )
