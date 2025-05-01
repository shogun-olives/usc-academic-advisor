from ..util import term_code, dept_code
from ..classes import Course, Section, Instructor
from .usc_soc_requests import call_usc_api


class Cache(object):
    """
    A class to represent a cache for storing data.

    Attributes:
        term (str | int): The current term to scrape data from (e.g., "Fall 2025" or "20253").
        cache (dict): A dictionary to store cached data.

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
        my_cache["CSCI", 20253]  # (str) of all courses in the given term and department
        my_cache["CSCI"]  # (str) of all courses in the active term and department

        # Can access sections by course code
        my_cache["CSCI 101", 20253]  # (str) of all sections in the given term and course
        my_cache["CSCI 101"]  # (str) of all sections in the active term and course
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
        self.term = term_code(term)
        self.cache = {self.term: dict()}

    def __getitem__(self, args) -> str:
        """
        Get the value of a specific attribute from the cache.

        Return will always be a formatted string of the data


        Args:
            key (str): The key to access the cache.
            term (int | str): The term code (e.g., "20253" or "Fall 2025").


        Examples:
            ```
            # Data stored in cache will be prioritized
            # If data is not in cache, API call will be made to fetch data

            # Can access courses by department code
            my_cache["CSCI", 20253]  # (str) of all courses in the given term and department
            my_cache["CSCI"]  # (str) of all courses in the active term and department
            my_cache["Computer Science"]  # (str) of all courses in the active term and department

            # Can access sections by course code
            my_cache["CSCI 101", 20253]  # (str) of all sections in the given term and course
            my_cache["CSCI 101"]  # (str) of all sections in the active term and course
            my_cache["Computer Science 101"]  # (str) of all sections in the active term and course
            ```
        """
        # ensure input is tuple
        if isinstance(args, str):
            args = (args,)

        # Check if the number of arguments is valid
        if len(args) > 2:
            raise ValueError("Too many arguments provided.")
        elif len(args) == 0:
            raise ValueError("No arguments provided.")

        # If there are two arguments, the second is the term
        if len(args) == 2:
            self.update_term(args[1])

        # First argument is always the key
        key = args[0]

        # Split the key into department and course number
        key_split = key.split(" ")

        # If there is no course number, key is a department code
        if len(key_split) == 1:
            dept = dept_code(key)

            # If department is valid but not in cache, retrieve it
            if dept not in self.cache[self.term]:
                self.retrieve(dept)

            return "\n".join(
                [str(course) for course in self.cache[self.term][dept].values()]
            )

        # If there is a course number, key is a course code
        dept = dept_code(" ".join(key_split[:-1]))
        course_num = key_split[-1]

        # If department is valid but not in cache, retrieve it
        if dept not in self.cache[self.term]:
            self.retrieve(dept)

        # If course number is valid, return the course object
        if course_num in self.cache[self.term][dept]:
            return str(self.cache[self.term][dept][course_num])
        else:
            raise ValueError(
                f"Course '{course_num}' not found in department '{dept}' for term '{self.term}'."
            )

    def retrieve(self, dept: str, term: str | int = None) -> None:
        """
        Retrieve course data for a specific department and term.

        Args:
            dept (str): The department code (e.g., "CSCI").
            term (str | int): The term code (e.g., "20253" or "Fall 2025"). (default: None)
                If None, the current term will be used.

        Examples:
            ```
            # Retrieve course data for a specific department and term
            my_cache.retrieve("CSCI", "20253")
            my_cache.retrieve("CSCI", "Fall 2025")
            my_cache.retrieve("Computer Science")

            data = my_cache["CSCI 101"]
            ```
        """
        # Update term if provided
        if term is not None:
            self.update_term(term)

        # check dept
        dept = dept_code(dept)

        # make API call to USC
        raw_data = call_usc_api(dept, self.term)

        # prepare cache for the term
        self.cache[self.term][dept] = dict()

        # For each course in the raw data
        for course_data in raw_data["OfferedCourses"]["course"]:
            course_data = course_data["CourseData"]
            # Get all sections in the course
            sections = []
            for section_data in (
                course_data["SectionData"]
                if isinstance(course_data["SectionData"], list)
                else [course_data["SectionData"]]
            ):
                # Skip non-lecture sections
                if section_data.get("type") != "Lecture":
                    continue

                # Get instructor data
                if "instructor" not in section_data:
                    instructor = "N/A"
                elif isinstance(section_data["instructor"], list):
                    instructor = Instructor(
                        section_data["instructor"][0]["first_name"],
                        section_data["instructor"][0]["last_name"],
                        section_data["instructor"][0].get("bio_url"),
                    )
                else:
                    instructor = Instructor(
                        section_data["instructor"]["first_name"],
                        section_data["instructor"]["last_name"],
                        section_data["instructor"].get("bio_url"),
                    )
                # Create a section object
                sections.append(
                    Section(
                        section_data.get("id"),
                        instructor,
                        section_data.get("spaces_available", 0),
                        section_data.get("number_registered", 0),
                        section_data.get("location", "N/A"),
                        section_data.get("start_time", "N/A"),
                        section_data.get("end_time", "N/A"),
                        section_data.get("day", ""),
                    )
                )

            # Create a course object
            course = Course(
                course_data["prefix"],
                course_data["number"],
                course_data["title"],
                course_data["description"],
                course_data["units"],
                sections,
            )

            # Add course to cache at cache[term][dept][number]
            self.cache[self.term][dept][course.number] = course

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
            ```
        """
        self.term = term_code(term)
        self.cache[self.term] = dict()
