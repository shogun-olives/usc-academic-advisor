from langchain.agents import initialize_agent, Tool, AgentExecutor
from langchain.agents.agent_types import AgentType
from langchain_community.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from ..util import get_openai_api_key, get_depts
from ..api import Cache
from ..ui import create_schedule
import re
import difflib


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
            model="gpt-3.5-turbo",
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
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int = 512,
    ):
        # Retrieve API key from environment variable if not provided
        self.openai_api_key = openai_api_key if openai_api_key else get_openai_api_key()

        # Prepare cache
        self.cache = Cache()

        # Create a schedule
        self.fig = create_schedule()
        self.fig_created = False

        # Set up default parameters
        self.dflt_model = model
        self.dflt_temp = temperature
        self.dflt_max_tokens = max_tokens

        # Tool 1: Get courses by department
        def get_courses(dept: str) -> str:
            dept = self._fuzzy_match_dept(dept)
            return self.cache.get_courses(dept)

        # Tool 2: Get sections by course
        def get_sections(course: str) -> str:
            course = self._fuzzy_format_course(course)
            result = self.cache.get_sections(course)
            if (
                result.startswith("'")
                and "could not find corresponding department" in result
            ):
                dept_guess = self._guess_course_correction(course)
                if dept_guess:
                    return f"'{course}' could not be found. Did you mean '{dept_guess}'? I will assume that and proceed."
            return result

        # Tool 3: Get list of departments
        def simple_get_depts(*args) -> str:
            return "\n".join(
                [f"{code}: {dept}" for code, dept in get_depts(self.cache.term).items()]
            )

        # Tool 4: Create a schedule from sections
        def create_schedule_from_sections(sections: str) -> str:
            sections = [sect.strip() for sect in sections.split(",") if sect.strip()]
            sect_data = self.cache.sect_to_sched_dict(sections)
            self.fig = create_schedule(sect_data)
            self.fig_created = True
            return "updated schedule"

        self.tools = [
            Tool(
                name="get_departments",
                func=simple_get_depts,
                description="Takes no inputs and gives a complete list of departments and their codes for the given term",
            ),
            Tool(
                name="get_courses",
                func=get_courses,
                description="Takes a department code (CSCI, MATH, etc.) and returns all courses in the given term and department in csv format",
            ),
            Tool(
                name="get_sections",
                func=get_sections,
                description="Takes a course code (CSCI 101, MATH 125, etc.) and returns all sections in the given term and course in csv format",
            ),
            Tool(
                name="create_schedule",
                func=create_schedule_from_sections,
                description='Takes a str of section IDs seperated by commas (e.g., "29947,29953") and creates a schedule based on the given sections.'
                + "If you want to create an empty schedule, pass an empty string.",
            ),
        ]

        # Initialize meomry for agent
        self.memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )

        # Initialize LLM and agent
        self.llm = ChatOpenAI(
            openai_api_key=self.openai_api_key,
            model_name=self.dflt_model,
            temperature=self.dflt_temp,
            max_tokens=self.dflt_max_tokens,
        )

        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True,
        )

        # Modified executor that returns intermediate steps
        self.agent_executor = AgentExecutor.from_agent_and_tools(
            agent=self.agent.agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            return_intermediate_steps=True,
        )

    def _fuzzy_match_dept(self, raw: str) -> str:
        raw = raw.strip().lower()
        dept_dict = get_depts(self.cache.term)
        codes = list(dept_dict.keys())
        names = list(dept_dict.values())
        all_options = codes + names
        match = difflib.get_close_matches(raw, all_options, n=1, cutoff=0.5)
        if match:
            for code, name in dept_dict.items():
                if match[0].lower() in [code.lower(), name.lower()]:
                    return code
        return raw.upper()

    def _fuzzy_format_course(self, course: str) -> str:
        course = course.strip().upper().replace(" ", "")
        match = re.match(r"([A-Z]{2,4})0*([0-9]{1,3}[A-Z]?)", course)
        if match:
            return f"{match.group(1)} {match.group(2)}"
        return course

    def _guess_course_correction(self, course_code: str) -> str:
        course_code = course_code.strip().upper().replace(" ", "")
        match = re.match(r"([A-Z]{1,4})([0-9]{1,3}[A-Z]?)", course_code)
        if match:
            return f"CSCI {match.group(2)}"
        return ""

    def __call__(self, prompt: str) -> str:
        result = self.agent_executor(prompt)
        response = result["output"]
        steps = result["intermediate_steps"]

        try:
            import streamlit as st

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
