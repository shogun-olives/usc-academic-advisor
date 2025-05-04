from dotenv import load_dotenv
import os

def get_openai_api_key() -> str:
    """
    Get the OpenAI API key from the environment variable.

    Returns:
        str: The OpenAI API key.

    Raises:
        ValueError: If the API key is not set in the environment variable.
    """
    # Load environment variables from .env file
    load_dotenv()

    # Get the OpenAI API key from the environment variable
    openai_api = os.getenv("OPENAI_API_KEY")

    # Check if the API key is set in the environment variable raise error
    if openai_api is None:
        raise ValueError(
            "\n\t".join(
                [
                    "Missing API key for OpenAI. Please check your environment variables or .env file.",
                    "1.   Create a .env file in the root directory",
                    "2.   Add OPENAI_API_KEY=your_api_key to the .env file",
                    "3.   Restart the program",
                ]
            )
        )
