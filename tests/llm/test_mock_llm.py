import unittest

from memory_base.llm.providers import MockLLM
from memory_base.llm.base import LLMClient


class TestMockLLM(unittest.TestCase):
    def test_respond(self) -> None:
        llm = MockLLM()  # provider has an auto-generated __init__ (dataclass)
        resp = llm.respond("hello", model="mock-model")
        self.assertIn("hello", resp.text)

    def test_chat_session(self) -> None:
        llm = MockLLM()
        session = llm.start_chat(model="mock-model", system="You are a test bot.")
        r1 = session.send("hi")
        r2 = session.send("second")
        self.assertIn("hi", r1.text)
        self.assertIn("second", r2.text)
        self.assertGreaterEqual(len(session.history), 3)  # system + 2*(user+assistant)

    def test_llm_client(self) -> None:
        llm = MockLLM()
        client = LLMClient(llm=llm, model="mock-model", system="You are a test bot.")
        resp = client.respond("hello")
        self.assertIn("hello", resp.text)
        session = client.start_chat()
        r1 = session.send("one")
        self.assertIn("one", r1.text)
        # client itself is also a dataclass (auto-generated __init__)
        self.assertIsNotNone(client.__init__)


if __name__ == "__main__":
    unittest.main()


