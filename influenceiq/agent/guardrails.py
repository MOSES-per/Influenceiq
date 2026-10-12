"""Basic safety guards: input limits, prompt-injection filtering, PII/secret redaction."""
import logging
import re

log = logging.getLogger("influenceiq.agent")

MAX_INPUT_CHARS = 1000

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE_RE = re.compile(r"(?<!\d)(?:\+?\d[\d\s().-]{8,}\d)(?!\d)")
SECRET_RE = re.compile(r"(AIza[0-9A-Za-z_-]{20,}|sk-[A-Za-z0-9_-]{20,})")

# Phrases that try to give the model new instructions from inside data
INJECTION_RE = re.compile(
    r"(ignore (all |any )?(the )?(previous|prior|above) (instructions|prompts?)"
    r"|disregard (all |any )?(the )?(previous|prior|above)"
    r"|forget (all |your )?(previous )?instructions"
    r"|you are now\b|new instructions:|system prompt|reveal (your|the) (prompt|instructions|api key))",
    re.IGNORECASE,
)

REFUSAL = (
    "I can only help with analyzing creators (scores, comparisons, content). "
    "I can't follow that request."
)


def check_user_input(text):
    """Return (ok, cleaned_text_or_message)."""
    text = (text or "").strip()
    if not text:
        return False, "Please type a question."
    if len(text) > MAX_INPUT_CHARS:
        return False, f"Please keep questions under {MAX_INPUT_CHARS} characters."
    if INJECTION_RE.search(text):
        log.warning("Blocked suspicious user input: %r", text[:80])
        return False, REFUSAL
    return True, text


def redact_pii(text):
    """Mask emails, phone numbers and API-key-like strings."""
    text = text or ""
    text = SECRET_RE.sub("[secret removed]", text)  # first, so digits inside keys aren't read as phones
    text = EMAIL_RE.sub("[email removed]", text)
    text = PHONE_RE.sub("[phone removed]", text)
    return text


def sanitize_untrusted(text):
    """Clean text that came from outside (post titles, bios) before the LLM sees it."""
    text = redact_pii(text)
    if INJECTION_RE.search(text):
        log.warning("Removed injection-like text from untrusted data")
        text = INJECTION_RE.sub("[removed]", text)
    return text.strip()[:300]
