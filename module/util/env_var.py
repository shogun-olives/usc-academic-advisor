from datetime import date
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


def get_current_term_code() -> str:
    """
    Estimate the current USC term code based on today's date.

    Returns:
        str: The term code (e.g., "20253")
    """
    today = date.today()
    year = today.year
    month = today.month

    if 1 <= month <= 5:
        return f"{year}1"
    elif 6 <= month <= 7:
        return f"{year}2"
    else:
        return f"{year}3"
