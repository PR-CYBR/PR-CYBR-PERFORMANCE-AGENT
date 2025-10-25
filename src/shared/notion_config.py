"""Utilities for loading Notion configuration from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict


class NotionConfigurationError(EnvironmentError):
    """Raised when required Notion configuration values are missing."""


@dataclass(frozen=True)
class NotionConfig:
    """Container for Notion database identifiers and authentication token."""

    token: str
    task_database_id: str
    pull_request_database_id: str
    project_database_id: str
    discussion_database_id: str

    @classmethod
    def from_env(cls) -> "NotionConfig":
        """Load configuration values from the process environment.

        Raises:
            NotionConfigurationError: If any required environment variable is
                absent or empty.
        """

        required_vars: Dict[str, str] = {
            "NOTION_TOKEN": os.environ.get("NOTION_TOKEN", ""),
            "NOTION_TASK_DB": os.environ.get("NOTION_TASK_DB", ""),
            "NOTION_PR_DB": os.environ.get("NOTION_PR_DB", ""),
            "NOTION_PROJECT_DB": os.environ.get("NOTION_PROJECT_DB", ""),
            "NOTION_DISCUSSION_DB": os.environ.get("NOTION_DISCUSSION_DB", ""),
        }

        missing = [name for name, value in required_vars.items() if not value.strip()]
        if missing:
            formatted = ", ".join(sorted(missing))
            raise NotionConfigurationError(
                "Missing Notion configuration environment variables: "
                f"{formatted}. Ensure Terraform Cloud workspace variables are "
                "mapped to GitHub secrets and exported to the workflow runtime."
            )

        return cls(
            token=required_vars["NOTION_TOKEN"],
            task_database_id=required_vars["NOTION_TASK_DB"],
            pull_request_database_id=required_vars["NOTION_PR_DB"],
            project_database_id=required_vars["NOTION_PROJECT_DB"],
            discussion_database_id=required_vars["NOTION_DISCUSSION_DB"],
        )


__all__ = ["NotionConfig", "NotionConfigurationError"]
