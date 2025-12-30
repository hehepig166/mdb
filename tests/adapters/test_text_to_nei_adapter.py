import os
import pathlib
import unittest

from memory_base.adapters import TextToNEIAdapter
from memory_base.llm.base import LLM, LLMClient
from memory_base.llm.providers import OllamaLLM
from memory_base.llm.providers.ollama_provider import ollama_has_model
from memory_base.llm.types import ChatMessage, LLMResponse


class FakeJSONLLM(LLM):
    """
    Deterministic fake provider for unit tests.
    It returns a tagged NEI block no matter what the prompt is.
    """

    def _chat(
        self,
        *,
        messages,
        model,
        temperature=None,
        max_output_tokens=None,
        metadata=None,
    ) -> LLMResponse:
        return LLMResponse(
            text=(
                "<nei>\n"
                "<situation>s</situation>\n"
                "<goal>g</goal>\n"
                "<attempt>a</attempt>\n"
                "<result>r</result>\n"
                "<reflection>rho</reflection>\n"
                "<label>unknown</label>\n"
                "</nei>"
            )
        )


class TestTextToNEIAdapter(unittest.TestCase):
    def test_unit_parse_with_fake_llm(self) -> None:
        llm = LLMClient(llm=FakeJSONLLM(), model="fake")
        adapter = TextToNEIAdapter(llm=llm)
        nei = adapter.ingest("some free text")

        self.assertEqual(nei.situation, "s")
        self.assertEqual(nei.goal, "g")
        self.assertEqual(nei.attempt, "a")
        self.assertEqual(nei.result, "r")
        self.assertEqual(nei.reflection, "rho")
        self.assertEqual(nei.label, "unknown")
        self.assertTrue(len(nei.source_ref) > 0)

    def test_ollama_integration_optional(self) -> None:
        if os.environ.get("RUN_OLLAMA_TESTS") != "1":
            self.skipTest("Set RUN_OLLAMA_TESTS=1 to run Ollama integration tests.")

        base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        model = os.environ.get("OLLAMA_MODEL", "qwen3:4b")
        if not ollama_has_model(base_url=base_url, model=model):
            self.skipTest(f"Ollama not reachable or model not found: {model!r} at {base_url!r}")

        provider = OllamaLLM(base_url=base_url, timeout_s=60.0)
        llm = LLMClient(llm=provider, model=model)
        adapter = TextToNEIAdapter(llm=llm)

        text_path = pathlib.Path(__file__).parent / "examples" / "life_task_text_1.txt"
        text = text_path.read_text(encoding="utf-8")
        nei = adapter.ingest(text)

        self.assertIsNotNone(nei.source_ref)
        self.assertIn(nei.label, ("success", "failure", "unknown"))


if __name__ == "__main__":
    unittest.main()


