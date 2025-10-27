"""Telemetry helpers for monitoring Notion synchronization."""
from __future__ import annotations

import json
import logging
import os
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class PerformanceLogger:
  """Record synchronization performance metrics to disk and optional sinks."""

  log_path: Path = field(default_factory=lambda: Path("logs/sync_metrics.jsonl"))
  notion_callback: Optional[Any] = None
  notion_performance_db_id: Optional[str] = None
  _lock: threading.Lock = field(default_factory=threading.Lock, init=False, repr=False)

  def __post_init__(self) -> None:
    self.log_path.parent.mkdir(parents=True, exist_ok=True)

  def log_sync_event(
    self,
    event_type: str,
    status: str,
    metadata: Optional[Dict[str, Any]],
    started_at: float,
  ) -> None:
    """Persist sync telemetry for later analysis."""

    now = time.time()
    latency_ms = int((now - started_at) * 1000)
    record = {
      "timestamp": datetime.now(timezone.utc).isoformat(),
      "event_type": event_type,
      "status": status,
      "latency_ms": latency_ms,
      "metadata": metadata or {},
    }

    with self._lock:
      with self.log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, separators=(",", ":")) + os.linesep)

    if self.notion_callback and self.notion_performance_db_id:
      try:
        self.notion_callback(self.notion_performance_db_id, record)
      except Exception:  # pragma: no cover - protective logging
        logger.exception("Failed to forward performance record to Notion")
