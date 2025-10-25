import logging
from unittest.mock import Mock

import pytest

from notion_sync.handlers import NotionOperation, NotionSyncRunner


def test_runner_aggregates_errors_and_continues(caplog):
    success_action = Mock(return_value={"id": "123"})
    failing_action = Mock(side_effect=ValueError("boom"))
    final_action = Mock(return_value={"status": "archived"})

    operations = [
        NotionOperation(name="create_page", action=success_action),
        NotionOperation(name="update_page", action=failing_action),
        NotionOperation(name="archive_page", action=final_action),
    ]

    runner = NotionSyncRunner(operations, notion_client=Mock())

    with caplog.at_level(logging.INFO, logger="notion_sync"):
        result = runner.run(dry_run=False)

    assert success_action.called
    assert final_action.called
    assert result.errors[0]["operation"] == "update_page"
    assert result.summary()["failures"] == 1

    events = [record.getMessage() for record in caplog.records]
    assert any("operation_failed" in event for event in events)
    assert any("run_completed" in event for event in events)


def test_runner_respects_dry_run_flag(monkeypatch, caplog):
    action = Mock(return_value={"id": "real_call"})
    operations = [NotionOperation(name="create", action=action)]
    runner = NotionSyncRunner(operations, notion_client=Mock())

    with caplog.at_level(logging.INFO, logger="notion_sync"):
        result = runner.run(dry_run=True)

    action.assert_not_called()
    assert result.successes[0]["data"] == {"status": "skipped", "reason": "dry-run"}
    assert result.ok


def test_runner_reads_environment_variable(monkeypatch):
    action = Mock(return_value={"id": "real_call"})
    operations = [NotionOperation(name="create", action=action)]
    runner = NotionSyncRunner(operations, notion_client=Mock())

    monkeypatch.setenv("DRY_RUN", "true")
    runner.run()
    action.assert_not_called()


def test_runner_returns_error_summary_when_failures(monkeypatch):
    action = Mock(side_effect=RuntimeError("network down"))
    operations = [NotionOperation(name="create", action=action)]
    runner = NotionSyncRunner(operations, notion_client=Mock())

    result = runner.run(dry_run=False)
    assert not result.ok
    assert result.summary()["failures"] == 1
    assert result.errors[0]["error_type"] == "RuntimeError"
