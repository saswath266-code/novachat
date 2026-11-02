"""Small, defensive wrapper around the Gemini SDK."""

import os
from functools import lru_cache

from dotenv import load_dotenv


load_dotenv()

DEFAULT_MODEL = "gemini-flash-latest"
DEFAULT_TIMEOUT_MS = 30_000


class GeminiServiceError(RuntimeError):
    """Raised when Gemini cannot provide a usable response."""


class GeminiConfigurationError(GeminiServiceError):
    """Raised when the local Gemini configuration is incomplete."""


def _api_key() -> str:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or api_key.lower() == "your_api_key_here":
        raise GeminiConfigurationError(
            "GEMINI_API_KEY is missing. Add a valid key to .env before starting the app."
        )
    return api_key


def _model_name() -> str:
    model = os.getenv("GEMINI_MODEL", DEFAULT_MODEL).strip()
    if not model:
        raise GeminiConfigurationError("GEMINI_MODEL cannot be empty.")
    return model


def _timeout_ms() -> int:
    """Return the whole-request timeout used by the Gemini HTTP client."""
    try:
        timeout = int(os.getenv("GEMINI_TIMEOUT_MS", DEFAULT_TIMEOUT_MS))
    except (TypeError, ValueError):
        return DEFAULT_TIMEOUT_MS
    return timeout if timeout > 0 else DEFAULT_TIMEOUT_MS


@lru_cache(maxsize=1)
def _get_client():
    """Create the SDK client only when the first chat request arrives."""
    try:
        from google import genai
    except ImportError as error:
        raise GeminiConfigurationError(
            "The google-genai package is not installed. Run pip install -r requirements.txt."
        ) from error

    return genai.Client(
        api_key=_api_key(),
        # The Google Gen AI SDK expects this value in milliseconds.
        http_options={"timeout": _timeout_ms()},
    )


def generate_response(prompt: str) -> str:
    """Generate plain text for one user message."""
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("prompt must be a non-empty string")

    try:
        response = _get_client().models.generate_content(
            model=_model_name(),
            contents=prompt,
        )
        text = response.text
    except GeminiConfigurationError:
        raise
    except Exception as error:
        raise GeminiServiceError("Gemini request failed") from error

    if not isinstance(text, str) or not text.strip():
        raise GeminiServiceError("Gemini returned no text response")

    return text.strip()
