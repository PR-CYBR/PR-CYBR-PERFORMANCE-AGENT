from scripts.notion_sync import NotionSyncService


class DummyClient:
  def __init__(self) -> None:
    self.calls = []

  def upsert_page(self, database_id, properties, page_id=None):
    self.calls.append({
      "database_id": database_id,
      "properties": properties,
      "page_id": page_id,
    })
    return {"id": "mock-page"}


def test_issue_properties_include_expected_fields():
  service = NotionSyncService(None, {})
  issue = {
    "title": "Investigate latency regression",
    "state": "open",
    "html_url": "https://github.com/org/repo/issues/1",
    "number": 1,
  }
  props = service._issue_properties(issue)
  assert props["Name"]["title"][0]["text"]["content"] == issue["title"]
  assert props["Status"]["select"]["name"] == "Open"
  assert props["Source URL"]["url"] == issue["html_url"]
  assert props["External ID"]["rich_text"][0]["text"]["content"] == "1"
  assert "Last Synced" in props


def test_resolve_database_prefers_task_backlog():
  databases = {
    "NOTION_TASK_BACKLOG_DB_ID": "task-db",
    "NOTION_ISSUES_BACKLOG_DB_ID": "issues-db",
  }
  service = NotionSyncService(None, databases)
  assert service._resolve_database("issues") == "task-db"


def test_handle_invokes_notion_client_and_returns_summary():
  databases = {"NOTION_TASK_BACKLOG_DB_ID": "task-db"}
  client = DummyClient()
  service = NotionSyncService(client, databases)
  payload = {"issue": {"title": "Bug", "state": "closed", "html_url": "url", "number": 7}}

  result = service.handle("issues", payload)

  assert result["status"] == "synced"
  assert result["database_id"] == "task-db"
  assert client.calls[0]["database_id"] == "task-db"
  assert client.calls[0]["properties"]["Status"]["select"]["name"] == "Closed"


def test_handle_skips_when_database_missing():
  service = NotionSyncService(None, {})
  result = service.handle("issues", {"issue": {}})
  assert result["status"] == "skipped"
  assert result["reason"] == "missing_database"
