"""Command line helpers for running Notion sync workflows."""
from __future__ import annotations

import argparse
import logging
from typing import Sequence

from .handlers import LOGGER_NAME, NotionSyncRunner
from .registry import NOTION_OPERATIONS

_cli_logger = logging.getLogger(f"{LOGGER_NAME}.cli")


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the Notion sync workflow")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Log intended actions without issuing API calls.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)

    runner = NotionSyncRunner(NOTION_OPERATIONS)
    result = runner.run(dry_run=args.dry_run)

    if not NOTION_OPERATIONS:
        _cli_logger.info("No Notion operations were registered; nothing to do.")

    if result.ok:
        _cli_logger.info("Notion sync completed successfully with %s operations.", len(result.successes))
        return 0

    _cli_logger.error(
        "Notion sync completed with %s failures. Error details: %s",
        len(result.errors),
        result.errors,
    )
    return 1


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
