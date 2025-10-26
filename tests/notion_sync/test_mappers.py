import json
import unittest
from pathlib import Path

from notion_sync.mappers import (
    MappingResult,
    map_issue_payload,
    map_workflow_run_payload,
)

FIXTURES = Path(__file__).parent / "fixtures"


class TestMappers(unittest.TestCase):
    def load_fixture(self, name: str) -> dict:
        with open(FIXTURES / name, "r", encoding="utf-8") as handle:
            return json.load(handle)

    def test_map_issue_payload(self) -> None:
        payload = self.load_fixture("issue_opened.json")
        mapping = map_issue_payload(payload)

        self.assertIsInstance(mapping, MappingResult)
        self.assertEqual(mapping.github_id, "issue:1001")
        self.assertEqual(mapping.url, "https://github.com/example/repo/issues/1")

        props = mapping.properties
        self.assertEqual(
            props["Title"]["title"][0]["text"]["content"],
            "Example issue",
        )
        self.assertEqual(props["Status"]["select"]["name"], "Open")
        self.assertEqual(props["Assignee"]["rich_text"][0]["text"]["content"], "octocat")
        tag_names = [tag["name"] for tag in props["Tags"]["multi_select"]]
        self.assertEqual(tag_names, ["bug", "help wanted"])
        self.assertEqual(props["GitHub ID"]["rich_text"][0]["text"]["content"], "MDU6SXNzdWUxMDAx")
        self.assertEqual(props["Created At"]["date"]["start"], "2024-01-01T12:00:00Z")
        self.assertEqual(props["Updated At"]["date"]["start"], "2024-01-02T12:00:00Z")
        self.assertEqual(props["Notion Page ID"], {"rich_text": []})

    def test_map_issue_payload_requires_issue(self) -> None:
        with self.assertRaises(ValueError):
            map_issue_payload({"action": "opened"})

    def test_map_workflow_run_payload(self) -> None:
        payload = self.load_fixture("workflow_run_completed.json")
        mapping = map_workflow_run_payload(payload)

        self.assertEqual(mapping.github_id, "workflow_run:9001")
        props = mapping.properties
        self.assertEqual(props["Status"]["select"]["name"], "Completed / Success")
        self.assertEqual(
            props["Tags"]["multi_select"],
            [{"name": "push"}, {"name": "6789"}],
        )
        self.assertEqual(props["Links"]["url"], "https://github.com/example/repo/actions/runs/9001")

    def test_map_workflow_run_requires_payload(self) -> None:
        with self.assertRaises(ValueError):
            map_workflow_run_payload({})


if __name__ == "__main__":
    unittest.main()

