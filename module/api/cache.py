from ..util import term_code, dept_code
from ..classes import Course, Section, Instructor
from .usc_soc_requests import call_usc_api
import difflib
import requests


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
        self.term = term_code(term)
        self.cache = {self.term: dict()}

    def __getitem__(self, args) -> Course | list[Course]:
        if isinstance(args, str):
            args = (args,)

        if len(args) > 2:
            raise ValueError("Too many arguments provided.")
        elif len(args) == 0:
            raise ValueError("No arguments provided.")

        if len(args) == 2:
            self.update_term(args[1])

        key = args[0]
        key_split = key.split(" ")

        if len(key_split) == 1:
            dept = dept_code(key)

            if dept not in self.cache[self.term]:
                print(f"[Cache] Miss department {dept} – retrieving...")
                self.retrieve(dept)
            else:
                print(f"[Cache] Hit department {dept}")

            return list(self.cache[self.term][dept].values())

        dept = dept_code(" ".join(key_split[:-1]))
        course_num = key_split[-1]

        if dept not in self.cache[self.term]:
            print(f"[Cache] Miss course {dept} {course_num} – retrieving...")
            self.retrieve(dept)
        else:
            print(f"[Cache] Hit department {dept}")

        if course_num in self.cache[self.term][dept]:
            print(f"[Cache] Hit course {dept} {course_num}")
            return self.cache[self.term][dept][course_num]
        else:
            raise ValueError(
                f"Course '{course_num}' not found in department '{dept}' for term '{self.term}'."
            )

    def retrieve(self, dept: str, term: str | int = None) -> None:
        if term is not None:
            self.update_term(term)

        dept = dept_code(dept)
        raw_data = call_usc_api(dept, self.term)

        print(
            f"[USC API DEBUG] https://web-app.usc.edu/web/soc/api/classes/{dept}/{self.term}")
        print(
            f"[USC API DEBUG] Response keys: {list(raw_data.keys()) if isinstance(raw_data, dict) else type(raw_data)}")

        self.cache[self.term][dept] = dict()

        for course_data in raw_data["OfferedCourses"]["course"]:
            course_data = course_data["CourseData"]
            sections = []

            for section_data in (
                course_data["SectionData"]
                if isinstance(course_data["SectionData"], list)
                else [course_data["SectionData"]]
            ):
                if section_data.get("type") != "Lecture":
                    continue

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

            course = Course(
                course_data["prefix"],
                course_data["number"],
                course_data["title"],
                course_data["description"],
                course_data["units"],
                sections,
            )

            self.cache[self.term][dept][course.number] = course

    def update_term(self, term: str | int) -> None:
        self.term = term_code(term)
        self.cache[self.term] = dict()

    def fuzzy_search_course(self, keyword: str) -> list[str]:
        results = []
        for dept, courses in self.cache[self.term].items():
            for number in courses:
                code = f"{dept} {number}"
                if difflib.get_close_matches(keyword, [code], cutoff=0.6):
                    results.append(code)
        return results
