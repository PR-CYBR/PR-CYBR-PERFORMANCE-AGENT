"""Notion sync helpers with structured logging and error aggregation."""
from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, List, Optional

LOGGER_NAME = "notion_sync"


def _ensure_logger_configured(logger: logging.Logger) -> None:
    """Ensure the module logger has at least one handler configured."""
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class _StructuredLogger:
    """Helper wrapper that emits JSON structured log entries."""

    def __init__(self, logger: logging.Logger) -> None:
        _ensure_logger_configured(logger)
        self._logger = logger

    def log(self, level: int, event: str, **context: Any) -> None:
        payload = {"event": event, **context}
        self._logger.log(level, json.dumps(payload, sort_keys=True))


@dataclass
class NotionOperation:
    """Represents a single Notion mutation or query to execute."""

    name: str
    action: Callable[[Any], Any]
    dry_run_preview: Optional[Callable[[], Any]] = None

    def execute(self, client: Any, *, dry_run: bool) -> Any:
        """Execute the operation, respecting the dry-run flag."""
        if dry_run:
            if self.dry_run_preview:
                return self.dry_run_preview()
            return {"status": "skipped", "reason": "dry-run"}
        return self.action(client)


@dataclass
class NotionSyncResult:
    """Collects successes and errors encountered during a sync run."""

    successes: List[dict] = field(default_factory=list)
    errors: List[dict] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    def summary(self) -> dict:
        return {
            "successes": len(self.successes),
            "failures": len(self.errors),
            "errors": self.errors,
        }


class NotionSyncRunner:
    """Executes a series of Notion operations with fault isolation."""

    def __init__(
        self,
        operations: Optional[Iterable[NotionOperation]] = None,
        notion_client: Any = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.operations: List[NotionOperation] = list(operations or [])
        self.notion_client = notion_client
        self._logger = _StructuredLogger(logger or logging.getLogger(LOGGER_NAME))

    def run(self, dry_run: Optional[bool] = None) -> NotionSyncResult:
        if dry_run is None:
            dry_run = os.getenv("DRY_RUN", "false").lower() == "true"

        result = NotionSyncResult()

        for operation in self.operations:
            self._logger.log(
                logging.INFO,
                "operation_started",
                operation=operation.name,
                dry_run=dry_run,
            )
            try:
                data = operation.execute(self.notion_client, dry_run=dry_run)
                result.successes.append({"operation": operation.name, "data": data})
                self._logger.log(
                    logging.INFO,
                    "operation_succeeded",
                    operation=operation.name,
                    dry_run=dry_run,
                    data=data,
                )
            except Exception as exc:  # noqa: BLE001 - we want to aggregate all failures
                error_info = {
                    "operation": operation.name,
                    "error": str(exc),
                    "error_type": exc.__class__.__name__,
                }
                result.errors.append(error_info)
                self._logger.log(logging.ERROR, "operation_failed", **error_info, dry_run=dry_run)

        summary = result.summary()
        level = logging.ERROR if result.errors else logging.INFO
        self._logger.log(level, "run_completed", dry_run=dry_run, **summary)
        return result


__all__ = [
    "NotionOperation",
    "NotionSyncResult",
    "NotionSyncRunner",
]
