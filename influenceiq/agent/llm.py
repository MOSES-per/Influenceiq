"""LLM + embedding client (Gemini through its OpenAI-compatible endpoint)."""
import time

from openai import (
    APIConnectionError,
    APITimeoutError,
    InternalServerError,
    OpenAI,
    RateLimitError,
)

from influenceiq.config import settings

_client = None
_embed_cache = {}
RETRYABLE = (RateLimitError, InternalServerError, APIConnectionError, APITimeoutError)


def get_client():
    global _client
    if _client is None:
        if not settings.GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY is not set. Add it to your .env file.")
        _client = OpenAI(
            api_key=settings.GEMINI_API_KEY,
            base_url=settings.GEMINI_BASE_URL,
            timeout=60,
            max_retries=0,  # we handle retries ourselves
        )
    return _client


def _with_retry(fn, attempts=4, base_delay=4.0):
    """Retry on rate limits (429), Google overload (503) and network errors."""
    for i in range(attempts):
        try:
            return fn()
        except RETRYABLE:
            if i == attempts - 1:
                raise
            time.sleep(base_delay * (2 ** i))  # 4s, 8s, 16s


def chat(messages, tools=None):
    kwargs = {"model": settings.GEMINI_MODEL, "messages": messages}
    if tools:
        kwargs["tools"] = tools
    return _with_retry(lambda: get_client().chat.completions.create(**kwargs))


def embed(texts):
    """Return one embedding vector per input text. Repeated texts are served from a cache."""
    missing = list(dict.fromkeys(t for t in texts if t not in _embed_cache))
    for i in range(0, len(missing), 50):
        batch = missing[i:i + 50]
        resp = _with_retry(
            lambda: get_client().embeddings.create(model=settings.GEMINI_EMBED_MODEL, input=batch)
        )
        for text, item in zip(batch, resp.data):
            _embed_cache[text] = item.embedding
    return [_embed_cache[t] for t in texts]
