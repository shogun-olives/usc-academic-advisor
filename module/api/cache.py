import pandas as pd
from ..util import conv_term, conv_dept, get_depts, time_to_decimal
from .parse import get_courses_dfs
from ..errors import (
    DepartmentNotFound,
    CourseNotFound,
    SectionNotFound,
    ScheduleConflictError,
)


class Cache(object):
    """
    A class to represent a cache for storing data.

    Attributes:
        term (str | int): The term code (e.g., "20253").
        cached (set): A set of cached department and term pairs.
        depts (dict): A dictionary of department codes and names.
        courses (pd.DataFrame): A DataFrame containing course data.
            - code (str): The course code (e.g., "CSCI 100").
            - dept (str): The department code (e.g., "CSCI").
            - term (str | int): The term code (e.g., "20253").
            - title (str): The course title.
            - description (str): The course description.
            - units (int): The number of units for the course.
        sections (pd.DataFrame): A DataFrame containing section data.
            - id (str): The section ID.
            - code (str): The course code (e.g., "CSCI 100").
            - dept (str): The department code (e.g., "CSCI").
            - term (str | int): The term code (e.g., "20253").
            - title (str): The course title.
            - instructor (str): The instructor name.
            - location (str): The location of the section.
            - start_time (str): The start time of the section.
            - end_time (str): The end time of the section.
            - day (str): The days of the week the section is held.
            - spaces_left (int): The number of spaces left in the section.
            - number_registered (int): The number of students registered for the section.


    Examples:
        Initialization:
        ```
        # Initialize the Cache class with a specific term
        my_cache = Cache("Fall 2025")
        my_cache = Cache(20253)

        # Initialize the Cache class without a specific term
        my_cache = Cache()
        ```
        Data Access:
        ```
        # Data stored in cache will be prioritized
        # If data is not in cache, API call will be made to fetch data

        # Can access courses by department code
        my_cache.get_courses("CSCI")
        my_cache.get_courses("Computer Science")

        # Can access sections by course code
        my_cache.get_sections("CSCI 100")
        ```
    """

    def __init__(self, term: str | int = None) -> None:
        """
        Initialize the Cache class with a specific term.

        Args:
            term (str | int): The term name (e.g., "Fall 2025" or "20253"). (default: None)
                If None, the next term will be used.

        Examples:
            ```
            # Initialize the Cache class with a specific term
            my_cache = Cache("Fall 2025")
            my_cache = Cache(20253)

            # Initialize the Cache class without a specific term
            my_cache = Cache()
            ```
        """
        self.term = conv_term(term)
        self.cached = set()
        self.depts = get_depts(code_is_key=False)
        self.courses = pd.DataFrame(
            columns=[
                "code",
                "dept",
                "term",
                "title",
                "description",
                "units",
            ]
        )
        self.sections = pd.DataFrame(
            columns=[
                "id",
                "code",
                "dept",
                "term",
                "title",
                "instructor",
                "location",
                "start_time",
                "end_time",
                "day",
                "spaces_left",
                "number_registered",
                "spaces_available",
                "units",
            ]
        )

    def update_term(self, term: str | int) -> None:
        """
        Update the current term to scrape data from.

        Args:
            term (str | int): The new term name (e.g., "Fall 2025" or "20253").

        Examples:
            ```
            # Update the current term to scrape data from
            my_cache.update_term("Fall 2025")
            my_cache.update_term(20253)

            # Uses next term
            my_cache.update_term()
            ```
        """
        self.term = conv_term(term)

    def retrieve(self, dept: str) -> None:
        """
        Retrieve course data for a specific department and term.

        Args:
            dept (str): The department code (e.g., "CSCI").

        Examples:
            ```
            # Retrieve course data for a specific department and term from API
            my_cache.retrieve("CSCI")
            ```
        """
        # Check if the department is already cached
        if (dept, self.term) in self.cached:
            return

        # If not cached, retrieve data from API and store it in the cache
        self.cached.add((dept, self.term))
        courses, sections = get_courses_dfs(dept, self.term)

        self.courses = pd.concat([self.courses, courses], ignore_index=True)
        self.sections = pd.concat([self.sections, sections], ignore_index=True)

    def get_courses(self, dept: str) -> str:
        """
        Get all courses for a specific department in the current term. (comma separated values)

        Args:
            dept (str): The department code (e.g., "CSCI").

        Returns:
            output (str): A csv formatted string of all courses in the given term and department.

        Examples:
            ```
            # Get all courses for a specific department in the current term
            courses = my_cache.get_courses("CSCI")
            courses = my_cache.get_courses("Computer Science")

            print(courses)
            # code,title,description,units
            # CSCI 794A,Doctoral Dissertation,Credit on acceptance of Dissertation. Graded CR/NC.,2
            # CSCI 794B,Doctoral Dissertation,Credit on acceptance of Dissertation. Graded CR/NC.,2
            # CSCI 794C,Doctoral Dissertation,Credit on acceptance of Dissertation. Graded CR/NC.,2
            # CSCI 794D,Doctoral Dissertation,Credit on acceptance of Dissertation. Graded CR/NC.,2
            # CSCI 794Z,Doctoral Dissertation,Credit on acceptance of Dissertation. Graded CR/NC.,0
            # ...

            # If the department is not found, an error message will be returned
            courses = my_cache.get_courses("INVALID_DEPT")

            print(courses)
            # "'INVALID_DEPT' is not a valid department"
            ```
        """
        # check if the department is valid
        dept = conv_dept(dept)
        if dept is None:
            raise DepartmentNotFound(dept)

        # Retrieve data if not already cached
        self.retrieve(dept)

        # filter courses by term and department
        ret = self.courses[self.courses["term"] == self.term]
        ret = ret[ret["dept"] == dept.upper()]
        ret.drop(columns=["term", "dept"], inplace=True)

        # format as csv
        if ret.empty:
            return f"'{dept}' does not have any courses in the current term"

        return ret.to_csv(index=False, sep=",")

    def get_sections(self, course_code: str) -> str:
        """
        Get all sections for a specific course in the current term. (csv formatted)

        Args:
            course_num (str): The course number (e.g., "CSCI 100").

        Returns:
            output (str): A csv formatted string of all sections in the given term and course.

        Examples:
            ```
            # Get all sections for a specific course in the current term
            sections = my_cache.get_sections("CSCI 104")

            print(sections)
            # id,title,instructor,location,start_time,end_time,day,spaces_left,number_registered,units
            # 29903,Data Structures,Carter Slocum,THH201,12:30 PM,01:50 PM,"Tue, Thu",33,87,4
            # 29910,Data Structures,Mukund Raghothaman,MHP101,05:00 PM,06:20 PM,"Mon, Wed",64,6,4
            # 30397,Data Structures,Carter Slocum,SGM124,09:30 AM,10:50 AM,"Tue, Thu",74,46,4

            # If the course number department is not found, an error message will be returned
            sections = my_cache.get_sections("INVALID_COURSE")

            print(sections)
            # "'INVALID_COURSE' could not find corresponding department"

            # If the course number is not found, an error message will be returned
            sections = my_cache.get_sections("CSCI 101")

            print(sections)
            # "'CSCI 101' could not be found"
            ```
        """
        # Split into department and course number
        code_split = course_code.split(" ")
        dept = " ".join(code_split[:-1])
        course_num = code_split[-1]

        # check if the department is valid
        dept = conv_dept(dept)
        if dept is None:
            raise DepartmentNotFound(course_code)

        # Retrieve data if not already cached
        self.retrieve(dept)

        # filter courses by term and department
        ret = self.sections[self.sections["term"] == self.term]
        ret = ret[ret["code"] == f"{dept.upper()} {course_num}"]
        ret.drop(columns=["term", "dept", "code", "spaces_available"], inplace=True)

        if ret.empty:
            raise CourseNotFound(course_code)

        # format as csv
        return ret.to_csv(index=False, sep=",")

    def sect_to_sched_dict(self, sections: list[str]) -> list[dict[str : str | int]]:
        """
        Convert a list of sections to a list of dictionaries for schedule display.

        Args:
            sections (list[str]): A list of section IDs.
                    Example: ["29903", "29910", "30397"]

        Returns:
            list[dict[str, str]]: A list of dictionaries containing section information.

        Examples:
            ```
            # Convert a list of sections to a list of dictionaries for schedule display
            sections = ["29903", "29910"]
            schedule = my_cache.sect_to_sched_dict(sections)

            print(schedule)
            # Output: [
            #     {
            #         "label": "CSCI 100 - 29903<br>Carter Slocum<br>@THH201",
            #         "start_hour": 12.5,
            #         "end_hour": 13.83333,
            #         "day": ["Tue", "Thu"],
            #         "hover": "Data Structures (4 un.)<br>Tue, Thu,  12:30 PM – 01:50 PM",
            #     },
            #     {
            #         "label": "CSCI 100 - 29910<br>Mukund Raghothaman<br>@MHP101",
            #         "start_hour": 17.0,
            #         "end_hour": 18.33333,
            #         "day": ["Mon", "Wed"],
            #         "hover": "Data Structures (4 un.)<br>Mon, Wed,  05:00 PM – 06:20 PM",
            #     },
            # ]
            ```
        """
        # Check if all sections are valid
        for section in sections:
            if section not in self.sections["id"].values:
                raise SectionNotFound(section)

        data = [
            {
                "label": f"{row['code']} - {row['id']}<br>{row['instructor']}<br>@{row['location']}",
                "start_hour": time_to_decimal(row["start_time"]),
                "end_hour": time_to_decimal(row["end_time"]),
                "day": row["day"].split(", "),
                "hover": f"{row['title']} ({row['units']} un.)<br>{row['day']},  {row['start_time']} – {row['end_time']}",
            }
            for _, row in self.sections[self.sections["id"].isin(sections)].iterrows()
        ]

        # Check for any scheduling conflicts
        for i, sect1 in enumerate(data):
            for sect2 in data[i + 1 :]:
                if set(sect1["day"]) & set(sect2["day"]):
                    if not (
                        sect1["end_hour"] <= sect2["start_hour"]
                        or sect2["end_hour"] <= sect1["start_hour"]
                    ):
                        raise ScheduleConflictError(sect1, sect2)

        # If no conflicts, return data
        return data

    def is_valid_section(self, section: str) -> bool:
        """
        Check if a section is valid.

        Args:
            section (str): The section ID.

        Returns:
            output (bool): True if the section is valid, False otherwise.

        Examples:
            ```
            # Check if a section is valid
            is_valid = my_cache.is_valid_section("29903")
            print(is_valid)
            # Output: True

        ```
        """
        return section in self.sections["id"].values

    def get_section_data(self, section: str) -> dict[str, str | int]:
        """
        Get data for a specific section.

        Args:
            section (str): The section ID.

        Returns:
            output (dict[str, str | int]): A dictionary containing section information.

        Examples:
            ```
            # Get data for a specific section
            section_data = my_cache.get_section_data("29903")
            print(section_data)
            # Output: {
            #     "id": "29903",
            #     "instructor": "Carter Slocum",
            #     "location": "THH201",
            #     "start_time": "12:30 PM",
            #     "end_time": "01:50 PM",
            #     "day": ["Tue", "Thu"],
            #     "spaces_left": 33,
            #     "number_registered": 87,
            #     "units": 4,
            # }
            ```
        """
        if not self.is_valid_section(section):
            raise SectionNotFound(section)

        return self.sections[self.sections["id"] == section].iloc[0].to_dict()

    def get_sections_data(self, sections: list[str]) -> pd.DataFrame:
        """
        Get data for multiple sections.

        Args:
            sections (list[str]): A list of section IDs.
                Example: ["29903", "29910", "30397"]

        Returns:
            output (pd.DataFrame): A DataFrame containing section information.

        Examples:
            ```
            # Get data for multiple sections
            sections_data = my_cache.get_sections_data(["29903", "29910"])
            print(sections_data)
            # Output: A DataFrame containing section information for the specified sections
            ```
        """
        for section in sections:
            if not self.is_valid_section(section):
                raise SectionNotFound(section)
        return self.sections[self.sections["id"].isin(sections)]
