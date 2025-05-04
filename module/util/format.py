from datetime import datetime


def conv_time(time_str: str) -> str:
    """
    Convert a time string to a 12-hour format if valid, otherwise return original string.

    Args:
        time_str (str): The time string to convert (e.g., "14:30", "9:00").

    Returns:
        str: The converted time string in 12-hour format.

    Examples:
        ```
        # Convert "14:30" to "02:30 PM"
        time = conv_time("14:30")

        # Convert "9:00" to "09:00 AM"
        time = conv_time("9:00")

        # Convert "invalid_time" to "invalid_time"
        time = conv_time("invalid_time")
        ```
    """
    try:
        return datetime.strptime(time_str, "%H:%M").strftime("%I:%M %p")
    except ValueError:
        return time_str


def conv_days(days_str: str) -> str:
    """
    Convert a string of days to a list of days. Removes any invalid days. Any non-string input will return "N/A".

    Args:
        days_str (str): The string of days to convert (e.g., "MTWHFSU", "MW" "TH").

    Returns:
        output (str): The converted string of days (e.g., "Mon, Tue, Wed").

    Examples:
        ```
        # Convert "mtwtfsu" to "Mon, Tue, Wed, Thu, Fri, Sat, Sun"
        days = conv_days("MTWHFSU")

        # Convert "MW" to "Mon, Wed"
        days = conv_days("MW")

        # Convert "TH" to "Tue, Thu"
        days = conv_days("TH")

        # Converter "hello friend" to "Thu, Fri"
        days = conv_days("hello friend")

        # convert {} to "N/A"
        days = conv_days({})

        # convert 123 to "N/A"
        days = conv_days(123)
        ```
    """
    if not isinstance(days_str, str):
        return "N/A"

    day_of_week = {
        "M": "Mon",
        "T": "Tue",
        "W": "Wed",
        "H": "Thu",
        "F": "Fri",
        "S": "Sat",
        "U": "Sun",
    }
    return ", ".join(
        [day_of_week[day.upper()] for day in days_str if day in day_of_week.keys()]
    )


def conv_instr(instr_data: list | dict) -> str:
    """
    Convert instructor data to a string.

    Args:
        instr_data (list | dict): The instructor data to convert.

    Returns:
        output (str): The converted instructor string.

    Examples:
        ```
        instructor_data = [
            {
                "last_name": "Redekopp",
                "first_name": "Mark",
                "bio_url": "https://minghsiehee.usc.edu/directory/faculty/profile/?lname=Redekopp&fname=Mark"
            },
            {
                "last_name": "Paolieri",
                "first_name": "Marco",
                "bio_url": "https://qed.usc.edu/paolieri/"
            }
        ]

        instr_str = conv_instructor(instructor_data)
        print(instr_str)  # Output: "Mark Redekopp, Marco Paolieri"

        instructor_data = {
            "last": "Redekopp",
            "first": "Mark",
            "bio_url": "https://minghsiehee.usc.edu/directory/faculty/profile/?lname=Redekopp&fname=Mark"
        }

        instr_str = conv_instructor(instructor_data)
        print(instr_str)  # Output: "Mark Redekopp"

        instructor_data = "Some arbitrary string"
        instr_str = conv_instructor(instructor)
        print(instr_str)  # Output: "N/A"
        ```
    """
    if isinstance(instr_data, list):
        return ", ".join(
            [f"{instr['first_name']} {instr['last_name']}" for instr in instr_data]
        )
    elif isinstance(instr_data, dict):
        return f"{instr_data['first_name']} {instr_data['last_name']}"
    else:
        return "N/A"


def conv_term(term: int | str = None) -> int:
    """
    Converts a term to a term code.

    Args:
        term (int | str): The term name (e.g., "Fall 2025" "20253"). (default: None)

    Examples:
        ```
        # Term: Fall 2025
        term = Term("Fall 2025")
        term = Term("20253")

        # Finds next term
        term = Term()

        # Output is an int
        print(term)  # Output: 20253
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
        return int(f"{year}{semester}")

    # convert to string if term is an int
    if isinstance(term, int):
        term = str(term)

    # Term ID format (e.g., "20253")
    if term.isdigit() and len(term) == 5:
        return int(term)

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

        return int(f"{year}{semester}")

    # given term is not valid
    raise ValueError(
        f"Term '{term}' has an invalid format. Expected 'Fall 2025' or '20253' or None."
    )
