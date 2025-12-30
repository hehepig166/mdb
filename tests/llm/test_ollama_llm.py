import os
import unittest

from memory_base.llm.base import LLMClient
from memory_base.llm.providers.ollama_provider import OllamaLLM, ollama_has_model


class TestOllamaLLM(unittest.TestCase):
    """
    Optional integration test.

    Requirements:
    - `ollama serve` running locally
    - model available (default: qwen3:4b)

    Control:
    - set RUN_OLLAMA_TESTS=1 to enable
    - optionally set OLLAMA_MODEL / OLLAMA_BASE_URL
    """

    def test_ollama_respond_and_chat_session(self) -> None:
        if os.environ.get("RUN_OLLAMA_TESTS") != "1":
            self.skipTest("Set RUN_OLLAMA_TESTS=1 to run Ollama integration tests.")

        base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        model = os.environ.get("OLLAMA_MODEL", "qwen2.5:3b")

        if not ollama_has_model(base_url=base_url, model=model):
            self.skipTest(f"Ollama not reachable or model not found: {model!r} at {base_url!r}")

        provider = OllamaLLM(base_url=base_url, timeout_s=60.0)  # auto-generated __init__
        llm = LLMClient(llm=provider, model=model)
        # Single response (respond)
        resp = llm.respond("用一句话介绍一下你自己。")
        self.assertIsInstance(resp.text, str)
        self.assertGreater(len(resp.text.strip()), 0)

        # Chat session (2 turns), adapted from test.ipynb example.
        session = llm.start_chat()
        r1 = session.send("What's the capital of France?")
        self.assertIn("paris", r1.text.lower())

        r2 = session.send("What about Germany?")
        self.assertIn("berlin", r2.text.lower())


if __name__ == "__main__":
    unittest.main()


