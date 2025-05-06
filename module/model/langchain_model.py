from langchain.agents import initialize_agent, Tool, AgentExecutor
from langchain.agents.agent_types import AgentType
from langchain_community.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from ..util import get_openai_api_key, get_depts
from ..api import Cache
from ..ui import create_schedule
import streamlit as st
from ..util import fuzzy_match_dept, fuzzy_match_course, conv_dept
from ..errors import DepartmentNotFound, CourseNotFound
import re
import os


class LangChainModel:
    """
    A class to interact with the OpenAI API using LangChain.

    This class provides a simple interface to make predictions using the OpenAI model.

    It also includes tools to retrieve course and section information based on department codes and terms.

    The class uses caching to store and retrieve data efficiently.

    Attributes:
        openai_api_key (str): The OpenAI API key.
        dflt_model (str): The default OpenAI model to use.
        dflt_temp (float): The default temperature for the model.
        dflt_max_tokens (int): The default maximum number of tokens to generate.
        cache (Cache): An instance of the Cache class for storing data.
        fig (Figure): A Plotly Figure that stores the current course schedule.
        fig_created (bool): A flag indicating whether the schedule has been created.
        tools (list): A list of tools for the agent to use.
        memory (ConversationBufferMemory): Memory for the agent to store conversation history.
        llm (ChatOpenAI): The OpenAI model instance.
        agent (Agent): The agent instance for interacting with the model.

    Examples:
        ```
        # Initialize the LangChainModel class with environment API key
        my_model = LangChainModel()

        # Alternatively, initialize with specific parameters
        my_model = LangChainModel(
            openai_api_key="your_api_key",
            model="gpt-4-1106-preview",
            temperature=0.7,
            max_tokens=100,
        )

        # To make a prediction
        output = my_model("What is the name of the US President?")
        print(output)
        ```
    """

    def __init__(
        self,
        openai_api_key: str = None,
        model: str = "gpt-4-1106-preview",
        temperature: float = 0.7,
        max_tokens: int = 512,
    ):
        # Attributes ===============================================================================
        self.openai_api_key = openai_api_key if openai_api_key else get_openai_api_key()
        self.cache = Cache()
        self.fig = create_schedule()
        self.fig_created = False
        self.dflt_model = model
        self.dflt_temp = temperature
        self.dflt_max_tokens = max_tokens
        self.section_ids = []
        self.last_course = None

        # Tools =====================================================================================
        def get_courses(dept: str) -> str:
            depts = [x.strip() for x in dept.split(",")]
            ret = ""
            for dept in depts:
                matched = fuzzy_match_dept(dept)
                if matched is None:
                    raise DepartmentNotFound(dept)

                temp = self.cache.get_courses(matched)

                # If the department was fuzzy matched, report it
                if matched != conv_dept(dept.strip(), lower=True):
                    ret += (
                        f"'{dept}' could not be found. Did you mean {matched}? "
                        f"Here are the corresponding courses '{matched}':\n\n{temp}\n\n"
                    )
                    continue

                # If the department is found, return the courses
                ret += f"Here are the courses for '{matched}':\n\n{temp}\n\n"

            return ret

        def get_sections(course: str) -> str:
            courses = [x.strip() for x in course.split(",")]
            ret = ""
            for course in courses:
                matched = fuzzy_match_course(course)
                if matched is None:
                    raise CourseNotFound(course)

                temp = self.cache.get_sections(matched)

                # If the course was fuzzy matched, report it
                if course.strip().upper().replace(" ", "") != matched.replace(" ", ""):
                    ret += (
                        f"'{course}' could not be found. Did you mean '{matched}'? "
                        f"Here are the corresponding sections '{matched}':\n\n{temp}\n\n"
                    )
                    continue

                # If the course is found, return the sections
                ret += f"Here are the sections for '{matched}':\n\n{temp}\n\n"
            return ret

        def simple_get_depts(arg: str = None) -> str:
            return (
                "The following is a list of departments at the University of Southern California.\n"
                "For more information about courses, use `get_courses_from_department`"
                "with the corresponding department code\n"
                + "\n".join(
                    [
                        f"{code}: {dept}"
                        for code, dept in get_depts(self.cache.term).items()
                    ]
                )
            )

        def add_sections_to_schedule(sections: str) -> str:
            # convert str to list of sections
            sections = [s.strip() for s in sections.split(",") if s.strip()]

            # check which sections are valid
            valid, invalid = [], []
            for sec in sections:
                if self.cache.is_valid_section(sec):
                    self.section_ids.append(sec)
                    valid.append(sec)
                else:
                    invalid.append(sec)

            # If any sections were added, create a new schedule
            if valid:
                sect_data = self.cache.sect_to_sched_dict(self.section_ids)
                self.fig = create_schedule(sect_data)
                self.fig_created = True

            # If no sections were invalid, return a success message
            if not invalid:
                return f"Successfully added sections: {', '.join(valid)}."

            # If any sections were invalid, return an error message
            err_msg = []
            for inv in invalid:
                regex = re.match(r"[A-Z]{2,4}\s*\d{3}[A-Z]?", inv)

                if not regex:
                    err_msg.append(f"Invalid section ID: {inv}.")
                    continue

                course = fuzzy_match_course(regex.group())
                if course is None:
                    err_msg.append(f"Invalid course code: {inv}.")
                else:
                    err_msg.append(
                        "You specified a course code instead of a section ID. "
                        f"The available sections for {course} are as follows:"
                        f"\n{self.cache.get_sections(course)}\n"
                        "Please provide a valid section ID to add this course."
                    )

            return (
                f"Successfully added sections: {', '.join(valid)}.\n"
                "However, the following errors occured\n"
                "\n".join(err_msg)
            )

        def remove_sections_from_schedule(sections: str) -> str:
            # convert str to list of sections
            sections = [s.strip() for s in sections.split(",") if s.strip()]
            existing_sections = {
                self.cache.get_section_data(s)["code"]: s for s in self.section_ids
            }

            # check which sections are valid
            valid, invalid = [], []
            for sec in sections:
                # If section is in the schedule, remove it
                if sec in self.section_ids:
                    self.section_ids.remove(sec)
                    valid.append(sec)
                    continue

                # If section is not in the schedule, check if it's a valid section ID
                regex = re.match(r"[A-Z]{2,4}\s*\d{3}[A-Z]?", sec)
                if not regex:
                    invalid.append(
                        f"The given section ID: {sec} does not exist in the schedule."
                    )
                    continue

                # If section is a valid course code, check if it exists in the schedule
                course = fuzzy_match_course(regex.group())
                if course is None:
                    invalid.append(
                        f"The selected course code: {sec} is in an invalid format."
                    )
                    continue

                if course in existing_sections:
                    self.section_ids.remove(existing_sections[course])
                    valid.append(existing_sections[course])
                    continue

                invalid.append(
                    f"The selected course code: {sec} is not in the schedule."
                )

            # If any sections were removed, create a new schedule
            if valid:
                sect_data = self.cache.sect_to_sched_dict(self.section_ids)
                self.fig = create_schedule(sect_data)
                self.fig_created = True

            # If no sections were invalid, return a success message
            if not invalid:
                return f"Successfully removed sections: {', '.join(valid)}."

            # If any sections were invalid, return an error message
            return (
                f"Successfully removed sections: {', '.join(valid)}.\n"
                "However, the following errors occured\n"
                "\n".join(invalid)
            )

        def remove_all_sections(arg: str = None) -> str:
            self.section_ids = []
            self.fig = create_schedule()
            self.fig_created = False
            return "All sections have been removed from the schedule."

        self.tools = [
            Tool(
                name="get_departments",
                func=simple_get_depts,
                description="Takes no inputs and gives a complete list "
                "of departments and their codes for the given term",
                handle_tool_error=True,
            ),
            Tool(
                name="get_courses_from_department",
                func=get_courses,
                description="Takes a department code (CSCI, MATH, etc.) "
                "and returns all courses in the given term and department in csv format",
                handle_tool_error=True,
            ),
            Tool(
                name="get_sections_from_course_code",
                func=get_sections,
                description="Takes a course code (CSCI 101, MATH 125, etc.) "
                "and returns all sections in the given term and course in csv format",
                handle_tool_error=True,
            ),
            Tool(
                name="add_section_to_schedule",
                func=add_sections_to_schedule,
                description="Takes a str of section IDs seperated by commas "
                '(e.g., "29947,29953") and adds these sections to the schedule.'
                "The section MUST be in ID format, if not, course cannot be added",
                handle_tool_error=True,
            ),
            Tool(
                name="remove_section_from_schedule",
                func=remove_sections_from_schedule,
                description="Takes a str of section IDs seperated by commas "
                '(e.g., "29947,29953") and removes these sections from the schedule.'
                "The section MUST be in ID format, if not, course cannot be added",
                handle_tool_error=True,
            ),
            Tool(
                name="remove_all_sections",
                func=remove_all_sections,
                description="Takes no inputs and removes all sections from the schedule.",
                handle_tool_error=True,
            ),
        ]

        # LLM =======================================================================================
        self.memory = ConversationBufferMemory(
            memory_key="chat_history", output_key="output", return_messages=True
        )

        self.llm = ChatOpenAI(
            openai_api_key=self.openai_api_key,
            model_name=self.dflt_model,
            temperature=self.dflt_temp,
            max_tokens=self.dflt_max_tokens,
        )

        with open(
            os.path.join(os.path.dirname(__file__), "system_prompt.txt"), "r"
        ) as f:
            prefix = "\n".join(x.strip() for x in f.readlines())

        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True,
            agent_kwargs={"prefix": prefix},
        )

        self.agent_executor = AgentExecutor.from_agent_and_tools(
            agent=self.agent.agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            return_intermediate_steps=True,
        )

    def __call__(self, prompt: str) -> str:
        result = self.agent_executor(prompt)
        response = result["output"]
        steps = result["intermediate_steps"]

        try:

            debug_mode = st.session_state.get("_sidebar_state", {}).get(
                "debug_mode", False
            ) or st.session_state.get("debug_mode", False)

            if debug_mode:
                st.session_state["debug_logs"].append(
                    "\n\n".join([f"[{step[0].tool}] {step[1]}" for step in steps])
                )
                response += "\n\n---\nTool Details:\n" + "\n".join(
                    f"[{step[0].tool}] {step[1]}" for step in steps
                )
        except Exception:
            pass

        return response
