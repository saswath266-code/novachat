import unittest
from unittest.mock import patch

from app import create_app
from services import gemini_service
from services.gemini_service import GeminiServiceError


class ChatRouteTests(unittest.TestCase):
    def setUp(self):
        self.prompts = []

        def fake_generator(prompt):
            self.prompts.append(prompt)
            return f"Reply: {prompt}"

        app = create_app(fake_generator)
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def test_home_page_loads(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"NovaChat", response.data)

    def test_chat_returns_generator_response(self):
        response = self.client.post("/chat", json={"message": "  Hello  "})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"response": "Reply: Hello"})
        self.assertEqual(self.prompts, ["Hello"])

    def test_chat_rejects_non_json_body(self):
        response = self.client.post("/chat", data="message=Hello")

        self.assertEqual(response.status_code, 400)
        self.assertIn("JSON object", response.get_json()["error"])

    def test_chat_rejects_missing_empty_and_non_string_messages(self):
        for payload in ({}, {"message": "   "}, {"message": 42}):
            with self.subTest(payload=payload):
                response = self.client.post("/chat", json=payload)
                self.assertEqual(response.status_code, 400)

    def test_chat_rejects_messages_over_the_limit(self):
        response = self.client.post("/chat", json={"message": "a" * 12_001})

        self.assertEqual(response.status_code, 400)
        self.assertIn("too long", response.get_json()["error"])

    def test_chat_rejects_oversized_request_bodies(self):
        response = self.client.post("/chat", json={"message": "a" * 40_000})

        self.assertEqual(response.status_code, 413)

    def test_chat_hides_provider_failures(self):
        app = create_app(
            lambda _prompt: (_ for _ in ()).throw(GeminiServiceError("provider detail"))
        )
        app.config.update(TESTING=True)

        response = app.test_client().post("/chat", json={"message": "Hello"})

        self.assertEqual(response.status_code, 503)
        self.assertNotIn("provider detail", response.get_json()["error"])


class GeminiServiceConfigTests(unittest.TestCase):
    def test_timeout_uses_default_for_invalid_values(self):
        for value in ("", "zero", "0", "-1"):
            with self.subTest(value=value), patch.dict(
                "os.environ", {"GEMINI_TIMEOUT_MS": value}
            ):
                self.assertEqual(
                    gemini_service._timeout_ms(), gemini_service.DEFAULT_TIMEOUT_MS
                )

    def test_timeout_accepts_positive_milliseconds(self):
        with patch.dict("os.environ", {"GEMINI_TIMEOUT_MS": "2500"}):
            self.assertEqual(gemini_service._timeout_ms(), 2500)


if __name__ == "__main__":
    unittest.main()
