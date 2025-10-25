"""GitHub event dispatcher for Notion synchronization."""

from __future__ import annotations

import logging
from typing import Callable, Dict

from .client import NotionSyncClient, NotionSyncError
from .mappers import (
    MappingResult,
    map_discussion_payload,
    map_issue_payload,
    map_project_card_payload,
    map_project_column_payload,
    map_pull_request_payload,
    map_workflow_run_payload,
)

LOGGER = logging.getLogger(__name__)

Handler = Callable[[str, dict, NotionSyncClient], str]


def _handle_and_sync(mapper: Callable[[dict], MappingResult], payload: dict, client: NotionSyncClient) -> str:
    mapping = mapper(payload)
    return client.upsert_page(mapping)


def _issues_handler(action: str, payload: dict, client: NotionSyncClient) -> str:
    LOGGER.info("Processing issue event with action '%s'", action)
    return _handle_and_sync(map_issue_payload, payload, client)


def _pull_request_handler(action: str, payload: dict, client: NotionSyncClient) -> str:
    LOGGER.info("Processing pull request event with action '%s'", action)
    return _handle_and_sync(map_pull_request_payload, payload, client)


def _discussion_handler(action: str, payload: dict, client: NotionSyncClient) -> str:
    LOGGER.info("Processing discussion event with action '%s'", action)
    return _handle_and_sync(map_discussion_payload, payload, client)


def _project_card_handler(action: str, payload: dict, client: NotionSyncClient) -> str:
    LOGGER.info("Processing project card event with action '%s'", action)
    return _handle_and_sync(map_project_card_payload, payload, client)


def _project_column_handler(action: str, payload: dict, client: NotionSyncClient) -> str:
    LOGGER.info("Processing project column event with action '%s'", action)
    return _handle_and_sync(map_project_column_payload, payload, client)


def _workflow_run_handler(action: str, payload: dict, client: NotionSyncClient) -> str:
    LOGGER.info("Processing workflow run event with action '%s'", action)
    return _handle_and_sync(map_workflow_run_payload, payload, client)


_HANDLERS: Dict[str, Handler] = {
    "issues": _issues_handler,
    "pull_request": _pull_request_handler,
    "pull_request_review": _pull_request_handler,
    "discussion": _discussion_handler,
    "discussion_comment": _discussion_handler,
    "project_card": _project_card_handler,
    "project_column": _project_column_handler,
    "workflow_run": _workflow_run_handler,
}


def dispatch_event(event_name: str, action: str, payload: dict, client: NotionSyncClient) -> bool:
    """Dispatch an event to the appropriate handler.

    Parameters
    ----------
    event_name:
        The GitHub event type (for example ``"issues"``).
    action:
        The GitHub event action (for example ``"opened"`` or ``"closed"``).
    payload:
        The GitHub event JSON payload as a dictionary.
    client:
        A :class:`NotionSyncClient` used to persist results to Notion.

    Returns
    -------
    bool
        ``True`` if a handler processed the event. ``False`` if there was no
        handler or the handler encountered a recoverable error.
    """

    handler = _HANDLERS.get(event_name)
    if not handler:
        LOGGER.info("No Notion sync handler registered for event '%s'", event_name)
        return False

    try:
        handler(action, payload, client)
    except NotionSyncError:
        LOGGER.exception(
            "Notion API reported an error while handling %s event (action=%s)",
            event_name,
            action,
        )
        return False
    except Exception:  # pragma: no cover - defensive catch
        LOGGER.exception("Unexpected error while handling event '%s'", event_name)
        raise

    return True

