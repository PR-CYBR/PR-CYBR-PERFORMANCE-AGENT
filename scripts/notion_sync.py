"""Synchronize GitHub activity with Notion databases."""
from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import requests

from metrics.performance_logger import PerformanceLogger

NOTION_API_BASE = "https://api.notion.com/v1"
NOTION_VERSION = os.getenv("NOTION_VERSION", "2022-06-28")


class NotionAPIError(RuntimeError):
  """Raised when the Notion API returns an unexpected response."""


@dataclass
class NotionClient:
  token: str
  session: requests.Session = field(default_factory=requests.Session)

  def __post_init__(self) -> None:
    self.session.headers.update(
      {
        "Authorization": f"Bearer {self.token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
      }
    )

  def upsert_page(self, database_id: str, properties: Dict[str, Any], page_id: Optional[str] = None) -> Dict[str, Any]:
    payload = {"properties": properties}
    if page_id:
      response = self.session.patch(f"{NOTION_API_BASE}/pages/{page_id}", json=payload, timeout=30)
    else:
      payload["parent"] = {"database_id": database_id}
      response = self.session.post(f"{NOTION_API_BASE}/pages", json=payload, timeout=30)
    if response.status_code >= 400:
      raise NotionAPIError(f"Notion API error {response.status_code}: {response.text}")
    return response.json()

  def append_performance_record(self, database_id: str, record: Dict[str, Any]) -> None:
    properties = {
      "Name": {"title": [{"text": {"content": f"{record['event_type']} @ {record['timestamp']}"}}]},
      "Status": {"select": {"name": record["status"]}},
      "Latency": {"number": record["latency_ms"]},
      "Details": {"rich_text": [{"text": {"content": json.dumps(record["metadata"])[:2000]}}]},
    }
    self.upsert_page(database_id, properties)


class NotionSyncService:
  """Translate GitHub webhook payloads into Notion updates."""

  def __init__(self, notion_client: Optional[NotionClient], databases: Dict[str, Optional[str]]) -> None:
    self.notion_client = notion_client
    self.databases = databases
    self.log = logging.getLogger(self.__class__.__name__)

  def handle(self, event_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    event_key = self._normalize_event_key(event_name, payload)
    database_id = self._resolve_database(event_key)
    if not database_id:
      self.log.info("No Notion database configured for event %s", event_key)
      return {"status": "skipped", "reason": "missing_database", "event_key": event_key}

    if not self.notion_client:
      self.log.warning("Notion token unavailable; skipping sync for %s", event_key)
      return {"status": "skipped", "reason": "missing_token", "event_key": event_key}

    properties = self._build_properties(event_key, payload)
    if not properties:
      self.log.info("No properties generated for event %s; skipping", event_key)
      return {"status": "skipped", "reason": "empty_payload", "event_key": event_key}

    page_id = self._extract_page_id(payload)
    response = self._call_with_retry(database_id, properties, page_id)
    summary = {
      "status": "synced",
      "event_key": event_key,
      "database_id": database_id,
      "page_id": response.get("id") if response else page_id,
    }
    return summary

  def _call_with_retry(self, database_id: str, properties: Dict[str, Any], page_id: Optional[str]) -> Dict[str, Any]:
    retries = 3
    delay = 2
    last_error: Optional[Exception] = None
    for attempt in range(1, retries + 1):
      try:
        return self.notion_client.upsert_page(database_id, properties, page_id)
      except Exception as exc:  # pragma: no cover - network boundary
        last_error = exc
        self.log.warning("Notion API call failed (%s/%s): %s", attempt, retries, exc)
        time.sleep(delay)
        delay *= 2
    assert last_error is not None
    raise last_error

  def _normalize_event_key(self, event_name: str, payload: Dict[str, Any]) -> str:
    if event_name == "pull_request" and payload.get("action") == "closed" and payload.get("pull_request", {}).get("merged"):
      return "pull_request_merged"
    if event_name == "workflow_dispatch":
      return payload.get("sync_target", "manual")
    return event_name

  def _resolve_database(self, event_key: str) -> Optional[str]:
    mapping: Dict[str, Any] = {
      "issues": ["NOTION_TASK_BACKLOG_DB_ID", "NOTION_ISSUES_BACKLOG_DB_ID"],
      "pull_request": ["NOTION_PROJECT_BOARD_BACKLOG_DB_ID"],
      "pull_request_merged": ["NOTION_PROJECT_BOARD_BACKLOG_DB_ID"],
      "discussions": ["NOTION_DISCUSSIONS_ARC_DB_ID"],
      "discussion": ["NOTION_DISCUSSIONS_ARC_DB_ID"],
      "projects_v2_item": ["NOTION_PROJECT_BOARD_BACKLOG_DB_ID"],
      "manual": ["NOTION_KNOWLEDGE_FILE_DB_ID"],
    }
    keys = mapping.get(event_key, [])
    for key in keys:
      db_id = self.databases.get(key)
      if db_id:
        return db_id
    return None

  def _build_properties(self, event_key: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    if event_key in {"issues"}:
      return self._issue_properties(payload.get("issue", {}))
    if event_key in {"pull_request", "pull_request_merged"}:
      return self._pull_request_properties(payload.get("pull_request", {}))
    if event_key in {"discussions", "discussion"}:
      return self._discussion_properties(payload.get("discussion", {}))
    if event_key == "projects_v2_item":
      return self._project_properties(payload.get("projects_v2_item", {}))
    if event_key == "manual":
      return self._manual_trigger_properties(payload)
    return {}

  def _issue_properties(self, issue: Dict[str, Any]) -> Dict[str, Any]:
    if not issue:
      return {}
    return self._base_properties(
      title=issue.get("title", "Untitled Issue"),
      state=issue.get("state", "open"),
      url=issue.get("html_url"),
      number=issue.get("number"),
      category="GitHub Issue",
    )

  def _pull_request_properties(self, pull_request: Dict[str, Any]) -> Dict[str, Any]:
    if not pull_request:
      return {}
    state = "merged" if pull_request.get("merged") else pull_request.get("state", "open")
    return self._base_properties(
      title=pull_request.get("title", "Untitled Pull Request"),
      state=state,
      url=pull_request.get("html_url"),
      number=pull_request.get("number"),
      category="Pull Request",
    )

  def _discussion_properties(self, discussion: Dict[str, Any]) -> Dict[str, Any]:
    if not discussion:
      return {}
    return self._base_properties(
      title=discussion.get("title", "GitHub Discussion"),
      state=discussion.get("state", "open"),
      url=discussion.get("html_url") or discussion.get("url"),
      number=discussion.get("number"),
      category="Discussion",
    )

  def _project_properties(self, project_item: Dict[str, Any]) -> Dict[str, Any]:
    if not project_item:
      return {}
    title = project_item.get("title") or project_item.get("content", {}).get("title") or "Project Item"
    state = project_item.get("status") or project_item.get("state", "active")
    url = project_item.get("url") or project_item.get("content", {}).get("url")
    return self._base_properties(
      title=title,
      state=state,
      url=url,
      number=project_item.get("id"),
      category="Project Board",
    )

  def _manual_trigger_properties(self, payload: Dict[str, Any]) -> Dict[str, Any]:
    note = payload.get("note", "Manual synchronization trigger")
    return self._base_properties(
      title=note,
      state="triggered",
      url=payload.get("reference_url"),
      number=payload.get("reference_id"),
      category="Manual",
    )

  def _base_properties(self, title: str, state: str, url: Optional[str], number: Optional[int], category: str) -> Dict[str, Any]:
    now_iso = datetime.now(timezone.utc).isoformat()
    status = "Closed" if state in {"closed", "completed", "merged"} else "Open"
    properties: Dict[str, Any] = {
      "Name": {"title": [{"text": {"content": title}}]},
      "Status": {"select": {"name": status}},
      "Category": {"select": {"name": category}},
      "Last Synced": {"date": {"start": now_iso}},
    }
    if url:
      properties["Source URL"] = {"url": url}
    if number is not None:
      properties["External ID"] = {"rich_text": [{"text": {"content": str(number)}}]}
    return properties

  def _extract_page_id(self, payload: Dict[str, Any]) -> Optional[str]:
    notion_info = payload.get("notion")
    if isinstance(notion_info, dict):
      return notion_info.get("page_id")
    return None


def load_github_event_payload() -> Dict[str, Any]:
  event_path = os.getenv("GITHUB_EVENT_PATH")
  if event_path and Path(event_path).exists():
    with open(event_path, "r", encoding="utf-8") as handle:
      return json.load(handle)
  return {}


def build_databases_map() -> Dict[str, Optional[str]]:
  keys = [
    "NOTION_DISCUSSIONS_ARC_DB_ID",
    "NOTION_ISSUES_BACKLOG_DB_ID",
    "NOTION_KNOWLEDGE_FILE_DB_ID",
    "NOTION_PROJECT_BOARD_BACKLOG_DB_ID",
    "NOTION_TASK_BACKLOG_DB_ID",
  ]
  return {key: os.getenv(key) for key in keys}


def configure_logging() -> None:
  logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


def main() -> None:
  configure_logging()
  logger = logging.getLogger("notion-sync")
  event_name = os.getenv("GITHUB_EVENT_NAME", "workflow_dispatch")
  payload = load_github_event_payload()
  token = os.getenv("NOTION_TOKEN")
  notion_client = NotionClient(token) if token else None
  databases = build_databases_map()

  performance_logger = PerformanceLogger(
    notion_callback=(notion_client.append_performance_record if notion_client else None),
    notion_performance_db_id=os.getenv("NOTION_PERFORMANCE_LOG_DB_ID"),
  )

  service = NotionSyncService(notion_client, databases)
  start_time = time.time()
  metadata: Dict[str, Any] = {"event": event_name, "action": payload.get("action")}
  try:
    result = service.handle(event_name, payload)
    metadata.update(result)
    status = result.get("status", "unknown")
    if status == "synced":
      logger.info("Notion sync completed for %s", result.get("event_key"))
    else:
      logger.warning("Notion sync skipped: %s", result)
  except Exception as exc:  # pragma: no cover - CLI guard
    metadata["error"] = str(exc)
    performance_logger.log_sync_event(event_name, "error", metadata, start_time)
    logger.exception("Notion sync failed")
    raise SystemExit(1) from exc
  else:
    performance_logger.log_sync_event(event_name, status, metadata, start_time)


if __name__ == "__main__":
  main()
