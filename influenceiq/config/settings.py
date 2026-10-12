import os
import random

from dotenv import load_dotenv

load_dotenv()

# Basic request headers to look like a normal browser
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

# Rate limiting (seconds)
MIN_DELAY = 5
MAX_DELAY = 8


def get_random_delay():
    return random.uniform(MIN_DELAY, MAX_DELAY)


# Secrets come from environment variables / a local .env file (never commit it)
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_EMBED_MODEL = os.getenv("GEMINI_EMBED_MODEL", "gemini-embedding-001")
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
