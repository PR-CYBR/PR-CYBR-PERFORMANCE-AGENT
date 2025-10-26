"""Translate GitHub webhook payloads into Notion property dictionaries."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional


@dataclass
class MappingResult:
    """Container for the result of mapping a payload to Notion properties."""

    github_id: str
    properties: Dict[str, Any]
    notion_page_id: Optional[str] = None
    url: Optional[str] = None


def _rich_text(value: Optional[str]) -> Dict[str, Any]:
    if not value:
        return {"rich_text": []}
    return {
        "rich_text": [
            {
                "type": "text",
                "text": {"content": value},
            }
        ]
    }


def _title(value: str) -> Dict[str, Any]:
    if not value:
        raise ValueError("Title property requires a non-empty value")
    return {
        "title": [
            {
                "type": "text",
                "text": {"content": value},
            }
        ]
    }


def _select(value: Optional[str]) -> Dict[str, Any]:
    if not value:
        return {"select": None}
    return {"select": {"name": value}}


def _multi_select(values: Iterable[Any]) -> Dict[str, Any]:
    unique_values = []
    seen = set()
    for value in values:
        normalized = str(value).strip()
        if normalized and normalized not in seen:
            seen.add(normalized)
            unique_values.append({"name": normalized})
    return {"multi_select": unique_values}


def _url(value: Optional[str]) -> Dict[str, Any]:
    return {"url": value or None}


def _date(value: Optional[str]) -> Dict[str, Any]:
    if not value:
        return {"date": None}
    return {"date": {"start": value}}


def _issue_status(state: str, action: Optional[str]) -> str:
    if action == "closed":
        return "Closed"
    if action == "reopened":
        return "Open"
    if state == "open":
        return "Open"
    if state == "closed":
        return "Closed"
    return state.title()


def map_issue_payload(payload: Dict[str, Any]) -> MappingResult:
    issue = payload.get("issue")
    if not issue:
        raise ValueError("Issues payload must include an 'issue' object")

    action = payload.get("action")
    title = issue.get("title")
    github_id = f"issue:{issue.get('id')}"
    url = issue.get("html_url")
    status = _issue_status(issue.get("state", ""), action)
    assignees = [assignee.get("login", "") for assignee in issue.get("assignees", [])]
    tags = [label.get("name", "") for label in issue.get("labels", [])]

    properties = {
        "Title": _title(title),
        "Status": _select(status),
        "Assignee": _rich_text(", ".join([name for name in assignees if name])),
        "Tags": _multi_select(tags),
        "Links": _url(url),
        "GitHub ID": _rich_text(str(issue.get("node_id", issue.get("id")))),
        "Notion Page ID": _rich_text(payload.get("notion_page_id")),
        "Created At": _date(issue.get("created_at")),
        "Updated At": _date(issue.get("updated_at")),
    }

    return MappingResult(github_id=github_id, properties=properties, url=url)


def _pull_request_status(pr: Dict[str, Any], action: Optional[str]) -> str:
    if pr.get("merged"):
        return "Merged"
    if action == "closed" and pr.get("state") == "closed":
        return "Closed"
    if pr.get("state") == "open":
        return "Open"
    return pr.get("state", "Unknown").title()


def map_pull_request_payload(payload: Dict[str, Any]) -> MappingResult:
    pull_request = payload.get("pull_request")
    if not pull_request:
        raise ValueError("Pull request payload must include a 'pull_request' object")

    action = payload.get("action")
    github_id = f"pull_request:{pull_request.get('id')}"
    url = pull_request.get("html_url")
    status = _pull_request_status(pull_request, action)
    assignees = [assignee.get("login", "") for assignee in pull_request.get("assignees", [])]
    reviewers = [reviewer.get("login", "") for reviewer in pull_request.get("requested_reviewers", [])]
    participants = [name for name in assignees + reviewers if name]
    tags = [label.get("name", "") for label in pull_request.get("labels", [])]

    properties = {
        "Title": _title(pull_request.get("title")),
        "Status": _select(status),
        "Assignee": _rich_text(", ".join(participants)),
        "Tags": _multi_select(tags),
        "Links": _url(url),
        "GitHub ID": _rich_text(str(pull_request.get("node_id", pull_request.get("id")))),
        "Notion Page ID": _rich_text(payload.get("notion_page_id")),
        "Created At": _date(pull_request.get("created_at")),
        "Updated At": _date(pull_request.get("updated_at")),
        "Merged At": _date(pull_request.get("merged_at")),
    }

    return MappingResult(github_id=github_id, properties=properties, url=url)


def map_discussion_payload(payload: Dict[str, Any]) -> MappingResult:
    discussion = payload.get("discussion")
    if not discussion:
        raise ValueError("Discussion payload must include a 'discussion' object")

    github_id = f"discussion:{discussion.get('id')}"
    url = discussion.get("html_url")
    tags = []
    category = discussion.get("category")
    if isinstance(category, dict):
        name = category.get("slug") or category.get("name")
        if name:
            tags.append(name)

    properties = {
        "Title": _title(discussion.get("title")),
        "Status": _select(payload.get("action", "" ).title() or "Active"),
        "Assignee": _rich_text(None),
        "Tags": _multi_select(tags),
        "Links": _url(url),
        "GitHub ID": _rich_text(str(discussion.get("node_id", discussion.get("id")))),
        "Notion Page ID": _rich_text(payload.get("notion_page_id")),
        "Created At": _date(discussion.get("created_at")),
        "Updated At": _date(discussion.get("updated_at")),
    }

    return MappingResult(github_id=github_id, properties=properties, url=url)


def map_project_card_payload(payload: Dict[str, Any]) -> MappingResult:
    project_card = payload.get("project_card")
    if not project_card:
        raise ValueError("Project card payload must include a 'project_card' object")

    github_id = f"project_card:{project_card.get('id')}"
    note = project_card.get("note") or "Project card"
    url = project_card.get("url") or project_card.get("html_url")
    column_name = None
    column = project_card.get("column") or payload.get("column") or {}
    if isinstance(column, dict):
        column_name = column.get("name")

    properties = {
        "Title": _title(note),
        "Status": _select(column_name or payload.get("action", "").title()),
        "Assignee": _rich_text(None),
        "Tags": _multi_select([]),
        "Links": _url(url),
        "GitHub ID": _rich_text(str(project_card.get("node_id", project_card.get("id")))),
        "Notion Page ID": _rich_text(payload.get("notion_page_id")),
        "Created At": _date(project_card.get("created_at")),
        "Updated At": _date(project_card.get("updated_at")),
    }

    return MappingResult(github_id=github_id, properties=properties, url=url)


def map_project_column_payload(payload: Dict[str, Any]) -> MappingResult:
    project_column = payload.get("project_column")
    if not project_column:
        raise ValueError("Project column payload must include a 'project_column' object")

    github_id = f"project_column:{project_column.get('id')}"
    name = project_column.get("name")
    url = project_column.get("url") or project_column.get("html_url")

    properties = {
        "Title": _title(name),
        "Status": _select(payload.get("action", "").title() or "Active"),
        "Assignee": _rich_text(None),
        "Tags": _multi_select([]),
        "Links": _url(url),
        "GitHub ID": _rich_text(str(project_column.get("node_id", project_column.get("id")))),
        "Notion Page ID": _rich_text(payload.get("notion_page_id")),
        "Created At": _date(project_column.get("created_at")),
        "Updated At": _date(project_column.get("updated_at")),
    }

    return MappingResult(github_id=github_id, properties=properties, url=url)


def map_workflow_run_payload(payload: Dict[str, Any]) -> MappingResult:
    workflow_run = payload.get("workflow_run")
    if not workflow_run:
        raise ValueError("Workflow run payload must include a 'workflow_run' object")

    github_id = f"workflow_run:{workflow_run.get('id')}"
    url = workflow_run.get("html_url")
    status_parts = [workflow_run.get("status"), workflow_run.get("conclusion")]
    status = " / ".join([part.title() for part in status_parts if part]) or "Unknown"

    properties = {
        "Title": _title(workflow_run.get("name")),
        "Status": _select(status),
        "Assignee": _rich_text(None),
        "Tags": _multi_select([workflow_run.get("event", ""), workflow_run.get("workflow_id", "")]),
        "Links": _url(url),
        "GitHub ID": _rich_text(str(workflow_run.get("node_id", workflow_run.get("id")))),
        "Notion Page ID": _rich_text(payload.get("notion_page_id")),
        "Created At": _date(workflow_run.get("created_at")),
        "Updated At": _date(workflow_run.get("updated_at")),
    }

    return MappingResult(github_id=github_id, properties=properties, url=url)

