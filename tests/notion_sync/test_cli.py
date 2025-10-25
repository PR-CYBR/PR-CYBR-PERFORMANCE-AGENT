import logging
from unittest.mock import Mock

import pytest

from notion_sync.cli import main
from notion_sync.handlers import NotionOperation
from notion_sync.registry import NOTION_OPERATIONS


@pytest.fixture(autouse=True)
def clear_registry():
    NOTION_OPERATIONS.clear()
    yield
    NOTION_OPERATIONS.clear()


def test_cli_respects_dry_run(caplog):
    operation = NotionOperation(name="create", action=Mock())
    NOTION_OPERATIONS.append(operation)

    with caplog.at_level(logging.INFO, logger="notion_sync"):
        exit_code = main(["--dry-run"])

    assert exit_code == 0
    operation.action.assert_not_called()


def test_cli_propagates_failures(caplog):
    operation = NotionOperation(name="create", action=Mock(side_effect=RuntimeError("oops")))
    NOTION_OPERATIONS.append(operation)

    with caplog.at_level(logging.INFO, logger="notion_sync"):
        exit_code = main([])

    assert exit_code == 1
