from ..util import decimal_to_time


class DepartmentNotFound(Exception):
    """Exception raised when a department is not found."""

    def __init__(self, dept: str) -> None:
        self.dept = dept
        super().__init__(
            f"'{dept}' is invalid. "
            "Please input a valid department name or code. "
            "(e.g., 'CSCI' or 'Computer Science')"
        )


class CourseNotFound(Exception):
    """Exception raised when a course is not found."""

    def __init__(self, course: str) -> None:
        self.course = course
        super().__init__(
            f"'{course}' is invalid"
            "Please input a valid course code. "
            "(e.g., 'CSCI 100' or 'CSCI101')"
        )


class SectionNotFound(Exception):
    """Exception raised when a section is not found."""

    def __init__(self, section: str) -> None:
        self.section = section
        super().__init__(
            f"'{section}' is invalid"
            "Please confirm that the section exists."
            "Section may not be valid until the corresponding department is cached."
        )


class ScheduleConflictError(Exception):
    """Exception raised when a schedule conflict is detected."""

    def __init__(self, section_1: dict[str], section_2: dict[str]) -> None:
        self.sect_1_id = section_1["label"].split("<br>")[0]
        self.sect_2_id = section_2["label"].split("<br>")[0]
        self.sect_1_time = (
            f"{decimal_to_time(section_1['start_hour'][0])} - "
            f"{decimal_to_time(section_1['end_hour'][1])} on "
            ", ".join(section_1["days"])
        )
        self.sect_2_time = (
            f"{decimal_to_time(section_2['start_hour'][0])} - "
            f"{decimal_to_time(section_2['end_hour'][1])} on "
            ", ".join(section_2["days"])
        )
        super().__init__(
            f"Schedule conflict detected:\n"
            f"Section 1: {self.sect_1_id} at {self.sect_1_time}\n"
            f"Section 2: {self.sect_2_id} at {self.sect_2_time}"
        )
