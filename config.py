"""Configuration settings and environment loading for AI Interview Coach."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip()
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "").strip()
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "").strip()
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21").strip()

# App Constants
MODES = ["Technical", "HR/Behavioral", "Mixed"]
DIFFICULTY_LEVELS = ["Fresher", "Mid-level", "Senior"]

MIN_QUESTIONS = 3
MAX_QUESTIONS = 15
DEFAULT_QUESTIONS = 5

MAX_CHAR_LIMIT = 12000
MIN_RESUME_CHAR_WARN = 200

# Scoring Dimensions
SCORE_DIMENSIONS = ["relevance", "depth", "structure", "clarity"]


def validate_config() -> tuple[bool, list[str]]:
    """
    Validates that all required Azure OpenAI environment variables are set.
    Returns:
        (is_valid: bool, missing_vars: list[str])
    """
    missing = []
    if not AZURE_OPENAI_ENDPOINT or AZURE_OPENAI_ENDPOINT.startswith("https://your-resource"):
        missing.append("AZURE_OPENAI_ENDPOINT")
    if not AZURE_OPENAI_API_KEY or AZURE_OPENAI_API_KEY == "your-azure-api-key-here":
        missing.append("AZURE_OPENAI_API_KEY")
    if not AZURE_OPENAI_DEPLOYMENT:
        missing.append("AZURE_OPENAI_DEPLOYMENT")

    return (len(missing) == 0, missing)
