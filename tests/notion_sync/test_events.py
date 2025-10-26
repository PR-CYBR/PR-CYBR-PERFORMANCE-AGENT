import json
import unittest
from pathlib import Path

from notion_sync import NotionSyncError
from notion_sync.events import dispatch_event

FIXTURES = Path(__file__).parent / "fixtures"


class FakeClient:
    def __init__(self) -> None:
        self.mappings = []

    def upsert_page(self, mapping):  # pragma: no cover - trivial
        self.mappings.append(mapping)
        return "page-id"


class TestEventDispatch(unittest.TestCase):
    def load_fixture(self, name: str) -> dict:
        with open(FIXTURES / name, "r", encoding="utf-8") as handle:
            return json.load(handle)

    def test_dispatch_issue_event(self) -> None:
        payload = self.load_fixture("issue_opened.json")
        client = FakeClient()
        handled = dispatch_event("issues", payload["action"], payload, client)
        self.assertTrue(handled)
        self.assertEqual(len(client.mappings), 1)

    def test_dispatch_unknown_event(self) -> None:
        payload = self.load_fixture("issue_opened.json")
        client = FakeClient()
        handled = dispatch_event("unknown_event", payload["action"], payload, client)
        self.assertFalse(handled)
        self.assertEqual(client.mappings, [])

    def test_dispatch_handles_notion_error(self) -> None:
        payload = self.load_fixture("issue_opened.json")

        class ErrorClient(FakeClient):
            def upsert_page(self, mapping):  # pragma: no cover - intentionally raises
                raise NotionSyncError("boom")

        client = ErrorClient()
        handled = dispatch_event("issues", payload["action"], payload, client)
        self.assertFalse(handled)


if __name__ == "__main__":
    unittest.main()

