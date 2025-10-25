"""Wrapper around the Notion SDK that provides retry-aware helpers."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, TYPE_CHECKING

from notion_client import Client
from notion_client.errors import APIResponseError, HTTPResponseError

if TYPE_CHECKING:  # pragma: no cover - imported only for type checking
    from .mappers import MappingResult


LOGGER = logging.getLogger(__name__)


class NotionSyncError(RuntimeError):
    """Raised when an operation against the Notion API ultimately fails."""


@dataclass
class RetryConfig:
    """Configuration for exponential backoff when invoking Notion APIs."""

    max_attempts: int = 3
    backoff_factor: float = 1.5
    max_backoff: float = 30.0


class NotionSyncClient:
    """Convenience wrapper around :class:`notion_client.Client`."""

    def __init__(
        self,
        token: str,
        database_id: str,
        *,
        retry_config: Optional[RetryConfig] = None,
        session: Optional[Client] = None,
    ) -> None:
        self._client = session or Client(auth=token)
        self._database_id = database_id
        self._retry_config = retry_config or RetryConfig()

    @property
    def database_id(self) -> str:
        return self._database_id

    def _with_retries(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        attempt = 0
        while True:
            try:
                return func(*args, **kwargs)
            except (APIResponseError, HTTPResponseError) as error:
                attempt += 1
                if not self._should_retry(error, attempt):
                    raise NotionSyncError(str(error)) from error
                sleep_for = self._sleep_for(error, attempt)
                LOGGER.warning(
                    "Retrying Notion API call after error (attempt %s/%s): %s",
                    attempt,
                    self._retry_config.max_attempts,
                    error,
                )
                time.sleep(sleep_for)
            except Exception as error:  # pragma: no cover - defensive catch
                raise NotionSyncError(str(error)) from error

    def _should_retry(self, error: Exception, attempt: int) -> bool:
        if attempt >= self._retry_config.max_attempts:
            return False
        status = getattr(error, "status", None)
        if status in (429, 500, 502, 503, 504):
            return True
        return bool(status and status >= 500)

    def _sleep_for(self, error: Exception, attempt: int) -> float:
        retry_after = 0.0
        body = getattr(error, "body", {}) or {}
        if isinstance(body, dict):
            retry_after = float(body.get("retry_after", 0.0))
        backoff = min(self._retry_config.backoff_factor ** attempt, self._retry_config.max_backoff)
        return max(retry_after, backoff)

    def create_page(self, properties: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        payload = {
            "parent": {"database_id": self._database_id},
            "properties": properties,
        }
        payload.update(kwargs)
        return self._with_retries(self._client.pages.create, **payload)

    def update_page(self, page_id: str, properties: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        payload = {"page_id": page_id, "properties": properties}
        payload.update(kwargs)
        return self._with_retries(self._client.pages.update, **payload)

    def query_database(self, **kwargs: Any) -> Dict[str, Any]:
        payload = {"database_id": self._database_id}
        payload.update(kwargs)
        return self._with_retries(self._client.databases.query, **payload)

    def find_page_by_property(self, property_name: str, value: str) -> Optional[Dict[str, Any]]:
        filter_payload = {
            "filter": {
                "property": property_name,
                "rich_text": {"equals": value},
            }
        }
        response = self.query_database(**filter_payload)
        results = response.get("results", [])
        if results:
            return results[0]
        return None

    def upsert_page(self, mapping: "MappingResult") -> str:
        properties = dict(mapping.properties)
        notion_page_id = mapping.notion_page_id
        if notion_page_id:
            LOGGER.debug("Updating Notion page %s from mapping", notion_page_id)
            final_properties = self._ensure_page_id_property(properties, notion_page_id)
            self.update_page(notion_page_id, final_properties)
            return notion_page_id

        github_id_property = properties.get("GitHub ID")
        github_id_value = None
        if github_id_property and isinstance(github_id_property.get("rich_text"), list):
            texts = github_id_property["rich_text"]
            if texts:
                github_id_value = texts[0].get("text", {}).get("content")

        existing_page = None
        if github_id_value:
            LOGGER.debug("Searching for Notion page with GitHub ID %s", github_id_value)
            existing_page = self.find_page_by_property("GitHub ID", github_id_value)

        if existing_page:
            page_id = existing_page.get("id")
            if not page_id:
                raise NotionSyncError("Existing Notion page is missing an identifier")
            final_properties = self._ensure_page_id_property(properties, page_id)
            self.update_page(page_id, final_properties)
            return page_id

        LOGGER.debug("Creating new Notion page for GitHub ID %s", mapping.github_id)
        new_page = self.create_page(self._ensure_page_id_property(properties, None))
        page_id = new_page.get("id")
        if not page_id:
            raise NotionSyncError("Created Notion page did not return an identifier")
        final_properties = self._ensure_page_id_property(properties, page_id)
        self.update_page(page_id, final_properties)
        return page_id

    def _ensure_page_id_property(self, properties: Dict[str, Any], page_id: Optional[str]) -> Dict[str, Any]:
        if "Notion Page ID" not in properties:
            return properties
        updated = dict(properties)
        if page_id:
            updated["Notion Page ID"] = {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": page_id},
                    }
                ]
            }
        else:
            updated["Notion Page ID"] = {"rich_text": []}
        return updated

