import unittest
from unittest.mock import MagicMock, patch

from notion_sync.client import NotionSyncClient, NotionSyncError
from notion_sync.mappers import MappingResult


class FakeAPIResponseError(Exception):
    def __init__(self, status, body=None):
        super().__init__("error")
        self.status = status
        self.body = body or {}


class TestNotionSyncClient(unittest.TestCase):
    def setUp(self) -> None:
        self.session = MagicMock()
        self.session.pages.create.return_value = {"id": "new-page"}
        self.session.pages.update.return_value = {"id": "new-page"}
        self.session.databases.query.return_value = {"results": []}
        self.client = NotionSyncClient(
            token="secret",
            database_id="db123",
            session=self.session,
        )

    def mapping(self) -> MappingResult:
        return MappingResult(
            github_id="issue:1001",
            properties={
                "Title": {"title": [{"text": {"content": "Example"}}]},
                "Status": {"select": {"name": "Open"}},
                "Assignee": {"rich_text": []},
                "Tags": {"multi_select": []},
                "Links": {"url": "https://example.com"},
                "GitHub ID": {"rich_text": [{"text": {"content": "gid"}}]},
                "Notion Page ID": {"rich_text": []},
                "Created At": {"date": None},
                "Updated At": {"date": None},
            },
        )

    def test_upsert_creates_new_page(self) -> None:
        page_id = self.client.upsert_page(self.mapping())
        self.assertEqual(page_id, "new-page")
        self.session.pages.create.assert_called_once()
        self.session.pages.update.assert_called()
        update_kwargs = self.session.pages.update.call_args.kwargs
        self.assertEqual(update_kwargs["page_id"], "new-page")
        notion_id = update_kwargs["properties"]["Notion Page ID"]["rich_text"][0]["text"]["content"]
        self.assertEqual(notion_id, "new-page")

    def test_upsert_updates_existing_page(self) -> None:
        self.session.databases.query.return_value = {"results": [{"id": "existing-page"}]}
        page_id = self.client.upsert_page(self.mapping())
        self.assertEqual(page_id, "existing-page")
        self.session.pages.create.assert_not_called()
        self.session.pages.update.assert_called()
        update_kwargs = self.session.pages.update.call_args.kwargs
        self.assertEqual(update_kwargs["page_id"], "existing-page")

    def test_upsert_propagates_errors(self) -> None:
        self.session.pages.create.side_effect = Exception("boom")
        with self.assertRaises(NotionSyncError):
            self.client.upsert_page(self.mapping())

    def test_retry_on_rate_limit(self) -> None:
        from notion_sync import client as client_module

        original = client_module.APIResponseError
        client_module.APIResponseError = FakeAPIResponseError
        self.addCleanup(lambda: setattr(client_module, "APIResponseError", original))

        call_state = {"count": 0}

        def flaky_create(**kwargs):
            if call_state["count"] == 0:
                call_state["count"] += 1
                raise FakeAPIResponseError(429, {"retry_after": 0})
            return {"id": "retry-page"}

        self.session.pages.create.side_effect = flaky_create

        with patch("notion_sync.client.time.sleep") as sleep_mock:
            page_id = self.client.upsert_page(self.mapping())

        self.assertEqual(page_id, "retry-page")
        self.assertGreaterEqual(sleep_mock.call_count, 1)


if __name__ == "__main__":
    unittest.main()

