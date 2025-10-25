"""CLI entrypoint for syncing GitHub events to Notion."""

from __future__ import annotations

import json
import logging
import os
import sys
from typing import Any, Dict

from notion_sync import NotionSyncClient, NotionSyncError, dispatch_event

LOGGER = logging.getLogger(__name__)


def load_event_payload(path: str) -> Dict[str, Any]:
    """Load a GitHub event payload from disk."""

    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _configure_logging() -> None:
    level_name = os.environ.get("NOTION_SYNC_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def main() -> int:
    _configure_logging()

    event_path = os.environ.get("GITHUB_EVENT_PATH")
    event_name = os.environ.get("GITHUB_EVENT_NAME", "")
    token = os.environ.get("NOTION_API_TOKEN") or os.environ.get("NOTION_TOKEN")
    database_id = os.environ.get("NOTION_DATABASE_ID")

    if not event_path or not os.path.exists(event_path):
        LOGGER.error("GITHUB_EVENT_PATH is not set or does not point to a file")
        return 0

    if not token:
        LOGGER.error("NOTION_API_TOKEN (or NOTION_TOKEN) is required")
        return 0

    if not database_id:
        LOGGER.error("NOTION_DATABASE_ID is required")
        return 0

    try:
        payload = load_event_payload(event_path)
    except json.JSONDecodeError:
        LOGGER.exception("Unable to parse GitHub event payload at %s", event_path)
        return 0
    except OSError:
        LOGGER.exception("Unable to open GitHub event payload at %s", event_path)
        return 0

    action = payload.get("action", "")
    if not event_name:
        event_name = payload.get("event", "")

    client = NotionSyncClient(token=token, database_id=database_id)

    try:
        handled = dispatch_event(event_name, action, payload, client)
    except NotionSyncError:
        LOGGER.exception(
            "Failed to dispatch %s event with action %s to Notion", event_name, action
        )
        handled = False
    except Exception:  # pragma: no cover - defensive
        LOGGER.exception("Unexpected error while dispatching event")
        handled = False

    if not handled:
        LOGGER.warning("No handler executed successfully for event '%s'", event_name)

    return 0


if __name__ == "__main__":
    sys.exit(main())

