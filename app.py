"""Flask application for NovaChat."""

import os
from collections.abc import Callable

from flask import Flask, jsonify, render_template, request

from services.gemini_service import (
    GeminiConfigurationError,
    GeminiServiceError,
    generate_response,
)


DEFAULT_MAX_MESSAGE_LENGTH = 12_000
DEFAULT_MAX_REQUEST_BYTES = 32 * 1024


def _positive_int_from_env(name: str, default: int) -> int:
    """Return a positive integer environment setting, falling back safely."""
    try:
        value = int(os.getenv(name, default))
    except (TypeError, ValueError):
        return default
    return value if value > 0 else default


def create_app(
    response_generator: Callable[[str], str] = generate_response,
) -> Flask:
    """Create the application instance.

    Accepting the response function makes the HTTP layer easy to test without
    an API key or a network call.
    """
    app = Flask(__name__)
    app.config.from_mapping(
        MAX_CONTENT_LENGTH=_positive_int_from_env(
            "MAX_REQUEST_BYTES", DEFAULT_MAX_REQUEST_BYTES
        ),
        MAX_MESSAGE_LENGTH=_positive_int_from_env(
            "MAX_MESSAGE_LENGTH", DEFAULT_MAX_MESSAGE_LENGTH
        ),
    )

    @app.get("/")
    def home():
        return render_template("index.html")

    @app.post("/chat")
    def chat():
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify(error="Send a JSON object with a 'message' field."), 400

        user_message = data.get("message")
        if not isinstance(user_message, str):
            return jsonify(error="'message' must be a string."), 400

        user_message = user_message.strip()
        if not user_message:
            return jsonify(error="'message' cannot be empty."), 400

        if len(user_message) > app.config["MAX_MESSAGE_LENGTH"]:
            return jsonify(
                error=(
                    "Your message is too long. "
                    f"Use {app.config['MAX_MESSAGE_LENGTH']:,} characters or fewer."
                )
            ), 400

        try:
            ai_response = response_generator(user_message)
            if not isinstance(ai_response, str) or not ai_response.strip():
                raise GeminiServiceError("Gemini returned no text response")
        except GeminiConfigurationError:
            app.logger.error("Gemini is not configured correctly.", exc_info=True)
            return jsonify(error="The AI service is not configured yet."), 503
        except GeminiServiceError:
            app.logger.error("Gemini request failed.", exc_info=True)
            return jsonify(
                error="The AI service is temporarily unavailable. Please try again."
            ), 503
        except Exception:
            # Do not send provider details or exception text to the browser.
            app.logger.exception("Unexpected error while generating an AI response.")
            return jsonify(
                error="The AI service is temporarily unavailable. Please try again."
            ), 503

        return jsonify(response=ai_response)

    @app.errorhandler(413)
    def request_too_large(_error):
        return jsonify(error="Request is too large."), 413

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG") == "1")
