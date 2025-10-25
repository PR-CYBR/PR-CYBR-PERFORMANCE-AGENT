"""Registry for Notion sync operations.

Projects can append to :data:`NOTION_OPERATIONS` during application startup to
customise the default CLI behaviour without modifying the core package.
"""

from typing import List

from .handlers import NotionOperation

NOTION_OPERATIONS: List[NotionOperation] = []

__all__ = ["NOTION_OPERATIONS"]
