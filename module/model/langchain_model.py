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
        def get_courses(dept: str) -> str:
            return self.cache.get_courses(dept)

        # Second tool for model to use
        def get_sections(course: str) -> str:
            return self.cache.get_sections(course)

        # Simplified wrapper for get_depts
        def simple_get_depts(*args) -> str:
            return "\n".join(
                [f"{code}: {dept}" for code, dept in get_depts(self.cache.term).items()]
            )

        # Set up tools for agent
        # TODO Figure out how to get langchain to use tools properly
        # TODO The responses should be used to suppliment the original prompt's response
        # TODO Right now, it just summarizes the response from the tools
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
