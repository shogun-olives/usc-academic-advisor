from .structs import Instructor
from datetime import datetime


class Section(object):
    """
    A class representing a section of a course.

    Attributes:
        section_id (str): The ID of the section.
        professor (Instructor): The instructor of the section.
        spaces_available (int): The number of spaces available in the section.
        number_registered (int): The number of students registered in the section.
        location (str): The location of the section.
        start_time (datetime.time): The start time of the section.
        end_time (datetime.time): The end time of the section.
        days (list[str]): A list of days when the section is held.
    """

    def __init__(
        self,
        section_id: str,
        professor: Instructor,
        spaces_available: int,
        number_registered: int,
        location: str,
        start_time: str,
        end_time: str,
        days: str,
    ):
        """
        Initialize a Section object.

        Args:
            section_id (str): The ID of the section.
            professor (str): The name of the professor.
            spaces_available (int): The number of spaces available in the section.
            number_registered (int): The number of students registered in the section.
            location (str): The location of the section.
            start_time (str): The start time of the section.
            end_time (str): The end time of the section.
            days (list[str]): A list of days when the section is held.
        """
        self.section_id = section_id
        self.professor = professor
        self.location = location

        # Make Numeric
        self.spaces_available = int(spaces_available)
        self.number_registered = int(number_registered)

        # Convert to time objects
        try:
            self.start_time = datetime.strptime(start_time, "%H:%M").strftime(
                "%I:%M %p"
            )
        except ValueError:
            self.start_time = start_time
        try:
            self.end_time = datetime.strptime(end_time, "%H:%M").strftime("%I:%M %p")
        except ValueError:
            self.end_time = end_time
        # Get day of week
        dow = {
            "M": "Mon",
            "T": "Tue",
            "W": "Wed",
            "H": "Thu",
            "F": "Fri",
            "S": "Sat",
            "U": "Sun",
        }
        self.days = [dow[day] for day in days]

    def __str__(self) -> str:
        """
        Return a string representation of the Section object.

        Returns:
            output (str): A string representation of the Section object.
        """
        return f"Professor {self.professor} ({self.section_id}): {', '.join(self.days)} {self.start_time} - {self.end_time} @{self.location} ({self.spaces_available - self.number_registered} spaces left)"


class Course(object):
    """
    A class representing a course.

    Attributes:
        id (str): The ID of the course.
        department (str): The department of the course.
        number (str): The course number.
        title (str): The title of the course.
        description (str): The description of the course.
        units (int): The number of units for the course.
        sections (list[Section]): A list of Section objects for the course.
    """

    def __init__(
        self,
        department: str,
        number: int,
        title: str,
        description: str,
        units: int,
        sections: list[Section],
    ):
        """
        Initialize a Course object.

        Args:
            department (str): The department of the course.
            number (int): The course code.
            title (str): The title of the course.
            description (str): The description of the course.
            units (int): The number of units for the course.
            sections (list[Section]): A list of Section objects for the course.
        """
        self.id = f"{department} {number}"
        self.department = department
        self.number = number
        self.title = title
        self.description = description
        self.units = units
        self.sections = sections

    def __str__(self) -> str:
        """
        Return a string representation of the Course object.

        Returns:
            output (str): A string representation of the Course object.
        """
        return f"{self.title} ({self.id}): {self.description}"

    def get_sections(self, sep="\n") -> list[str]:
        """
        Get a list of sections of this course.

        Args:
            sep (str): The separator to use between sections. (default: "\\n")

        Returns:
            sections (list[str]): A list of sections in this course.
        """
        return sep.join([str(section) for section in self.sections])
