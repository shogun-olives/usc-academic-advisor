from langchain.agents import initialize_agent, Tool
from langchain.agents.agent_types import AgentType
from langchain_community.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from ..util import get_openai_api_key, get_depts
from ..api import Cache


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
        """
        Initialize the LangChainModel class with the OpenAI API key and model parameters.

        Args:
            openai_api_key (str): The OpenAI API key. If not provided, it will be retrieved from the environment variable.
            model (str): The OpenAI model to use (default: "gpt-3.5-turbo").
            temperature (float): The temperature for the model (default: 0.7).
            max_tokens (int): The maximum number of tokens to generate (default: 512).

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
        # Retrieve API key from environment variable if not provided
        self.openai_api_key = openai_api_key if openai_api_key else get_openai_api_key()

        # Prepare cache
        self.cache = Cache()

        # Set up default parameters
        self.dflt_model = model
        self.dflt_temp = temperature
        self.dflt_max_tokens = max_tokens

        # First tool for model to use
        def get_courses(departments: list[str] | str) -> str:
            """
            Get all courses in the given term and departments.

            Args:
                departments (list[str]): List of department codes.

            Returns:
                str: Formatted string of all courses in the given term and departments.
            """
            if isinstance(departments, str):
                departments = [departments]

            response = []
            errors = []
            for dept in departments:
                # try to get the course
                try:
                    response.append(self.cache[dept])
                except ValueError:
                    errors.append(dept)

            if len(errors) > 0:
                return (
                    f"The following departments could not be found: {', '.join(errors)}\n\n"
                    + "\n\n".join(response)
                )
            return "\n\n".join(response)

        # Second tool for model to use
        def get_sections(courses: list[str] | str) -> str:
            """
            Get all sections in the given term and courses.

            Args:
                courses (list[str]): List of course codes.

            Returns:
                str: Formatted string of all sections in the given term and courses.
            """
            if isinstance(courses, str):
                courses = [courses]

            response = []
            errors = []
            for course in courses:
                # try to get the course
                try:
                    response.append(self.cache[course])
                except ValueError:
                    errors.append(course)

            if len(errors) > 0:
                return (
                    f"The following courses could not be found: {', '.join(errors)}\n\n"
                    + "\n\n".join(response)
                )
            return "\n\n".join(response)

        # Simplified wrapper for get_depts
        def simple_get_depts(*args) -> str:
            """
            Get all departments in the given term.

            Returns:
                str: Formatted string of all departments in the given term.
            """
            return "\n".join(
                [f"{code}: {dept}" for code, dept in get_depts(
                    self.cache.term).items()]
            )

        # Set up tools for agent
        # TODO Figure out how to get langchain to use tools properly
        # TODO The responses should be used to suppliment the original prompt's response
        # TODO Right now, it just summarizes the response from the tools
        self.tools = [
            Tool(
                name="get_departments",
                func=simple_get_depts,
                description=(
                    "Use this tool when the user wants to see which departments offer courses in the current term. "
                    "This tool returns a list of department codes along with their full department names. "
                    "For example, use it when the user asks 'What departments are available?' or 'List all departments'."
                ),
            ),

            Tool(
                name="get_courses",
                func=get_courses,
                description=(
                    "Use this tool to retrieve a list of all courses offered by one or more departments in the current term. "
                    "You can input a single department code or a list of department codes (e.g., ['CSCI', 'EE']). "
                    "This is helpful when a user asks: 'Show me all courses in CSCI', 'What courses does EE offer this term?', etc."
                ),
            ),

            Tool(
                name="get_sections",
                func=get_sections,
                description=(
                    "Use this tool to retrieve detailed section information for specific courses in the current term. "
                    "Input a list of course codes (e.g., ['CSCI 104', 'MATH 125']). "
                    "This tool returns section numbers, meeting times, and instructors. "
                    "Use it when the user asks: 'Who teaches CSCI 104?', 'What time is MATH 125?', or 'List all sections of CSCI 201'."
                ),
            ),

            Tool(
                name="get_instructors",
                func=get_instructors,
                description=(
                    "Use this tool to extract and display the professor or instructor names for given courses. "
                    "Input one or more course codes (e.g., 'CSCI 104'). "
                    "Use this tool when the user asks: 'Who is the instructor for CSCI 104?', or 'Which professor teaches MATH 125?'."
                ),
            ),

            Tool(
                name="get_credits",
                func=get_credits,
                description=(
                    "Use this tool to retrieve the number of units (credits) for specified courses. "
                    "Input one or more course codes, such as 'CSCI 201'. "
                    "Use this tool when users ask: 'How many units is CSCI 104?' or 'What are the credit values of these courses?'."
                ),
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
            handle_parsing_errors=True,
        )

    def __call__(self, prompt: str) -> str:
        """
        Make a prediction using the OpenAI model.

        Args:
            prompt (str): The input prompt for the model.

        Returns:
            output (str): The generated text from the model.

        Examples:
            ```
            # To make a prediction
            output = my_model("What is the name of the US President?")
            ```
        """
        return self.agent.run(prompt)
