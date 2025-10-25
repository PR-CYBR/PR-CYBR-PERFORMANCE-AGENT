import os
import pathlib
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from agent_logic.core_functions import AgentCore
from shared.notion_config import NotionConfigurationError


class TestAgentCore(unittest.TestCase):
    @mock.patch.dict(
        os.environ,
        {
            "NOTION_TOKEN": "fake-token",
            "NOTION_TASK_DB": "task-db",
            "NOTION_PR_DB": "pr-db",
            "NOTION_PROJECT_DB": "project-db",
            "NOTION_DISCUSSION_DB": "discussion-db",
        },
        clear=True,
    )
    def test_run(self):
        agent = AgentCore()
        self.assertIsNone(agent.run())

    @mock.patch.dict(os.environ, {}, clear=True)
    def test_missing_environment_variables(self):
        with self.assertRaises(NotionConfigurationError) as exc:
            AgentCore()

        self.assertIn("Missing Notion configuration environment variables", str(exc.exception))


if __name__ == '__main__':
    unittest.main()
