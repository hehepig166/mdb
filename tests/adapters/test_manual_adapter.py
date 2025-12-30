import json
import pathlib
import unittest

from memory_base.adapters import ManualAdapter


class TestManualAdapter(unittest.TestCase):
    def test_examples(self) -> None:
        adapter = ManualAdapter()
        examples_dir = pathlib.Path(__file__).parent / "examples"

        for path in sorted(examples_dir.glob("*.json")):
            with path.open("r", encoding="utf-8") as f:
                raw = json.load(f)

            nei = adapter.ingest(raw)
            # traceability must exist
            self.assertIsNotNone(nei.source_ref, msg=f"{path} missing source_ref")
            self.assertTrue(len(nei.source_ref) > 0, msg=f"{path} empty source_ref")

            # attempt is strongly recommended; minimal example should have it
            if path.name == "manual_minimal.json":
                self.assertIsInstance(nei.attempt, str)
                self.assertGreater(len(nei.attempt or ""), 0)

            # label must be in allowed set
            self.assertIn(nei.label, ("success", "failure", "unknown"))


if __name__ == "__main__":
    unittest.main()


