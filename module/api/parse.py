import pandas as pd
from .api_requests import api_get_courses
from ..util import conv_days, conv_time, conv_instr


def get_courses_dfs(
    dept_code: str,
    term_code: int | str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Get the courses and sections dataframes for a given department and term.

    For the courses dataframe, the columns are:
        - code: The course code (e.g. "CSCI 100")
        - dept: The department code (e.g. "CSCI")
        - term: The term code (e.g. 20253)
        - title: The course title
        - description: The course description
        - units: The number of units for the course

    For the sections dataframe, the columns are:
        - id: The section ID
        - code: The course code (e.g. "CSCI 100")
        - term: The term code (e.g. 20253)
        - dept: The department code (e.g. "CSCI")
        - title: The section title
        - instructor: The instructor name
        - location: The location of the section
        - start_time: The start time of the section
        - end_time: The end time of the section
        - day: The days of the week the section is held
        - spaces_left: The number of spaces left in the section
        - number_registered: The number of students registered for the section
        - spaces_available: The total number of spaces available in the section
        - units: The number of units for the section

    Args:
        dept_code (str): The department code (e.g. "CSCI").
        term_code (int | str): The term code (e.g. 20253 or "20253").

    Returns:
        output (tuple[pd.DataFrame, pd.DataFrame]): A tuple containing two dataframes:
            - courses: Dataframe of all courses in the given term and department.
            - sections: Dataframe of all sections in the given term and department.

    Examples:
        ```
        # Get the courses and sections dataframes for a given department and term
        courses, sections = get_courses_dfs("CSCI", "20253")

        # courses dataframe
        #         code  dept   term                                       title                                        description  units
        # 0    CSCI 100  CSCI  20243                   Explorations in Computing  A behind-the-scenes overview of the computatio...      4
        # 1    CSCI 102  CSCI  20243                 Fundamentals of Computation  Fundamental concepts of algorithmic thinking a...      2
        # 2    CSCI 103  CSCI  20243                 Introduction to Programming  Basic datatypes, assignments, control statemen...      4
        # ..        ...   ...    ...                                         ...                                                ...    ...
        #
        # [88 rows x 6 columns]

        # sections dataframe
        #         id       code  dept   term  title     instructor location start_time  end_time       day  spaces_left number_registered spaces_available  units
        # 0    30211   CSCI 100  CSCI  20243    ...   Raghavachary   ZHS352   11:00 AM  12:20 PM  Tue, Thu            1                59               60       4
        # 1    29918   CSCI 102  CSCI  20243    ...  Mark Redekopp   GFS106   01:00 PM  01:50 PM  Mon, Wed           23               121              144       4
        # 2    30235   CSCI 102  CSCI  20243    ...  Mark Redekopp   GFS106   02:00 PM  02:50 PM  Mon, Wed           30               114              144       4
        # ..     ...        ...   ...    ...    ...            ...      ...        ...       ...       ...          ...               ...              ...     ...
        #
        # [136 rows x 12 columns]
        ```
    """
    raw_data = api_get_courses(dept_code, term_code)
    term_code = int(term_code)

    courses = []
    sections = []
    for course_data in raw_data["OfferedCourses"]["course"]:
        courses.append(
            {
                "code": f"{course_data['CourseData']['prefix']} {course_data['CourseData']['number']}"
                + (
                    course_data["CourseData"]["sequence"]
                    if isinstance(course_data["CourseData"]["sequence"], str)
                    else ""
                ),
                "dept": course_data["CourseData"]["prefix"],
                "term": term_code,
                "title": course_data["CourseData"]["title"],
                "description": course_data["CourseData"]["description"],
                "units": int(course_data["CourseData"]["units"][0]),
            }
        )

        for section_data in (
            course_data["CourseData"]["SectionData"]
            if isinstance(course_data["CourseData"]["SectionData"], list)
            else [course_data["CourseData"]["SectionData"]]
        ):
            # Skip non-lecture sections
            if section_data.get("type") != "Lec":
                continue

            if "id" not in section_data:
                continue
            # Get instructor data
            sections.append(
                {
                    "id": section_data["id"],
                    "code": f"{course_data['CourseData']['prefix']} {course_data['CourseData']['number']}"
                    + (
                        course_data["CourseData"]["sequence"]
                        if isinstance(course_data["CourseData"]["sequence"], str)
                        else ""
                    ),
                    "dept": course_data["CourseData"]["prefix"],
                    "term": term_code,
                    "title": (
                        course_data["CourseData"]["section_title"]
                        if not isinstance(
                            course_data["CourseData"].get("section_title", dict()),
                            dict,
                        )
                        else course_data["CourseData"].get("title", "N/A")
                    ),
                    "instructor": conv_instr(section_data.get("instructor", None)),
                    "location": section_data.get("location", "N/A"),
                    "start_time": conv_time(section_data.get("start_time", None)),
                    "end_time": conv_time(section_data.get("end_time", None)),
                    "day": conv_days(section_data.get("day", "")),
                    "spaces_left": (
                        int(section_data.get("spaces_available", 0))
                        - int(section_data.get("number_registered", 0))
                    ),
                    "number_registered": section_data.get("number_registered", 0),
                    "spaces_available": section_data.get("spaces_available", 0),
                    "units": int(course_data["CourseData"]["units"][0]),
                }
            )

    # convert the list of dictionaries to a dataframe
    courses = pd.DataFrame(courses)
    sections = pd.DataFrame(sections)

    return courses, sections
