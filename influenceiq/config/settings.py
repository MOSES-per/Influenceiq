import random

# Basic request headers to look like a normal browser
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9"
}

# Rate limiting (seconds)
MIN_DELAY = 5
MAX_DELAY = 8

def get_random_delay():
    return random.uniform(MIN_DELAY, MAX_DELAY)
YOUTUBE_API_KEY = "AIzaSyDUs7KEk_9jLS_JVScK7zS16sY53-BtEbk"
