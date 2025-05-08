import pandas as pd
import requests
import json
import os

from module.util.format import conv_instr
from ..util.dept_info import get_depts
from ..util.env_var import get_current_term_code


def api_get_courses(
    dept_code: str,
    term_code: int | str,
    overwrite: bool = False,
) -> dict | None:
    """
    Call the USC API to get course data for a specific department and term.

    Args:
        dept_code (str): The department code (e.g., "CSCI").
        term_code (int | str): The term code (e.g., "20253" or 20253).
        overwrite (bool): If True, overwrite the cache. (default: False)

    Returns:
        output (dict | None): The JSON response from the API containing course data, or None if the request fails.

    Examples:
        ```
        # Call the USC API for a specific department and term
        data = call_usc_api("CSCI", "20253")
        data = call_usc_api("CSCI", 20253)
        ```
    """
    url = f"https://web-app.usc.edu/web/soc/api/classes/{dept_code}/{term_code}"
    fn = f"./data/cache/api/{dept_code}_{term_code}.json"

    if overwrite or not os.path.exists(fn) or os.path.getsize(fn) == 0:
        os.makedirs(os.path.dirname(fn), exist_ok=True)
        with open(fn, "w", encoding="utf-8") as f:
            response = requests.get(url)
            if response.status_code == 200:
                json.dump(response.json(), f, indent=4)
            else:
                return None

    with open(fn, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data


def fetch_all_sections() -> pd.DataFrame:
    term = get_current_term_code()
    all_sections = []

    print(f"[INFO] Fetching all departments for term: {term}")

    for dept in list(get_depts(code_is_key=True).keys()):
        try:
            url = f"https://web-app.usc.edu/web/soc/api/classes/{dept}/{term}"
            print(f"\n[INFO] Fetching URL: {url}")
            response = requests.get(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            })

            data = response.json()
            course_list = data.get("OfferedCourses", {}).get("course", [])
            print(
                f"[INFO] Department '{dept}': {len(course_list)} courses found.")

            for i, course_data in enumerate(course_list):
                course_info = course_data.get("CourseData", {})
                section_list = course_info.get("SectionData", [])

                if not isinstance(section_list, list):
                    section_list = [section_list]

                print(
                    f"  [Course {i+1}] {course_info.get('prefix')} {course_info.get('number')} - {len(section_list)} sections")

                for section in section_list:
                    try:
                        section_id = section.get("id")
                        if not section_id:
                            print("    [SKIP] Missing section ID.")
                            continue

                        all_sections.append({
                            "id": section_id,
                            "code": f"{course_info.get('prefix', '')} {course_info.get('number', '')}",
                            "dept": course_info.get("prefix"),
                            "term": term,
                            "title": section.get("title", course_info.get("title", "")),
                            "instructor": conv_instr(section.get("instructor")),
                            "location": section.get("location", ""),
                            "start_time": section.get("start_time", ""),
                            "end_time": section.get("end_time", ""),
                            "day": section.get("day", ""),
                            "spaces_left": int(section.get("spaces_available", 0)) - int(section.get("number_registered", 0)),
                            "number_registered": section.get("number_registered", 0),
                            "spaces_available": section.get("spaces_available", 0),
                            "units": int(course_info.get("units", "0")[0]) if isinstance(course_info.get("units"), str) else 0
                        })

                        print(f"    [OK] Section {section_id} added.")

                    except Exception as se:
                        print(f"    [ERROR] Section parse error: {se}")

        except Exception as e:
            print(f"[ERROR] Failed to fetch '{dept}': {e}")

    print(f"\n[INFO] Finished fetching. Total sections: {len(all_sections)}")
    return pd.DataFrame(all_sections)
