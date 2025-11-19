import json
import os
import tempfile
import unittest
from unittest.mock import patch

import scripts.notion_sync as cli
from notion_sync import NotionSyncError


class TestNotionSyncCLI(unittest.TestCase):
    def test_load_event_payload(self) -> None:
        with tempfile.NamedTemporaryFile("w", delete=False) as handle:
            json.dump({"hello": "world"}, handle)
            path = handle.name

        try:
            payload = cli.load_event_payload(path)
            self.assertEqual(payload, {"hello": "world"})
        finally:
            os.remove(path)

    @patch("scripts.notion_sync.dispatch_event")
    @patch("scripts.notion_sync.NotionSyncClient")
    def test_main_success(self, mock_client, mock_dispatch) -> None:
        mock_dispatch.return_value = True
        with tempfile.NamedTemporaryFile("w", delete=False) as handle:
            json.dump({"action": "opened"}, handle)
            path = handle.name

        env = {
            "GITHUB_EVENT_PATH": path,
            "GITHUB_EVENT_NAME": "issues",
            "NOTION_API_TOKEN": "secret",
            "NOTION_DATABASE_ID": "db123",
        }

        try:
            with patch.dict(os.environ, env, clear=True):
                exit_code = cli.main()
        finally:
            os.remove(path)

        self.assertEqual(exit_code, 0)
        mock_client.assert_called_once()
        mock_dispatch.assert_called_once_with(
            "issues", "opened", {"action": "opened"}, mock_client.return_value
        )

    @patch("scripts.notion_sync.dispatch_event")
    @patch("scripts.notion_sync.NotionSyncClient")
    def test_main_handles_notion_error(self, mock_client, mock_dispatch) -> None:
        mock_dispatch.side_effect = NotionSyncError("boom")
        with tempfile.NamedTemporaryFile("w", delete=False) as handle:
            json.dump({"action": "opened"}, handle)
            path = handle.name

        env = {
            "GITHUB_EVENT_PATH": path,
            "GITHUB_EVENT_NAME": "issues",
            "NOTION_API_TOKEN": "secret",
            "NOTION_DATABASE_ID": "db123",
        }

        try:
            with patch.dict(os.environ, env, clear=True):
                exit_code = cli.main()
        finally:
            os.remove(path)

        self.assertEqual(exit_code, 0)
        mock_dispatch.assert_called_once()


if __name__ == "__main__":
    unittest.main()

