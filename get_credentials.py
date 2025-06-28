"""get_credentials.py

Utility for loading the OpenAI API key and returning an initialized OpenAI client.
Supports:
- .env file (via python-dotenv)
- Environment variable fallback

"""

import os
from dotenv import load_dotenv
from openai import OpenAI


def get_openai_client(verbose=False):
    """Load OpenAI API key from .env or environment and return a client object."""
    load_dotenv()  # Load from .env file, if present
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "❌ OPENAI_API_KEY not found. Please add it to a .env file or set it in your environment.\n"
            "Example .env file:\n\n    OPENAI_API_KEY=your-api-key-here\n"
        )

    if verbose:
        print("✅ OpenAI API key loaded successfully.")

    return OpenAI(api_key=api_key)
