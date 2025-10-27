# PR-CYBR Performance Agent Synchronization Spec

_Last updated: 2025-05-27_

## Terraform Workspace Schema

The `infra/agent-variables.tf` file declares the Terraform Cloud workspace inputs that A-08 expects. All values are delivered through Terraform Cloud environment variables.

| Variable | Description |
| --- | --- |
| `AGENT_ACTIONS` | Token that authorizes CI/CD automation for the performance agent. |
| `NOTION_TOKEN` | Integration token for Notion API access. |
| `NOTION_PAGE_ID` | Root Notion page identifier used for contextual linking. |
| `NOTION_DISCUSSIONS_ARC_DB_ID` | Database ID for archiving GitHub discussions. |
| `NOTION_ISSUES_BACKLOG_DB_ID` | Database ID that mirrors the GitHub issues backlog. |
| `NOTION_KNOWLEDGE_FILE_DB_ID` | Database ID for knowledge base associations. |
| `NOTION_PROJECT_BOARD_BACKLOG_DB_ID` | Database ID for project board backlog synchronization. |
| `NOTION_TASK_BACKLOG_DB_ID` | Database ID for actionable task synchronization. |
| `TFC_TOKEN` | Terraform Cloud token used for workspace operations. |

`infra/variables.tfvars` contains placeholder values for local validation. The official values remain protected inside the Terraform Cloud workspace.

## GitHub ⇄ Notion Synchronization

The workflow `.github/workflows/notion-sync.yml` runs on the following events:

- Issues: `opened`, `edited`, `closed`, `reopened`
- Pull requests: `opened`, `reopened`, `closed`
- Discussions: `created`, `answered`
- Projects (Projects v2 items): `created`, `updated`, `deleted`
- Manual workflow dispatch triggers

Workflow steps:

1. Checkout repository
2. Configure Python 3.11
3. Install dependencies from `requirements.txt`
4. Execute `python scripts/notion_sync.py` with Notion credentials supplied from repository secrets

## Notion Database Mapping

The synchronization service routes events to Notion databases using the following mapping:

- GitHub issues → `NOTION_TASK_BACKLOG_DB_ID` (fallback `NOTION_ISSUES_BACKLOG_DB_ID`)
- Pull requests (including merged state) → `NOTION_PROJECT_BOARD_BACKLOG_DB_ID`
- Discussions → `NOTION_DISCUSSIONS_ARC_DB_ID`
- Project board items → `NOTION_PROJECT_BOARD_BACKLOG_DB_ID`
- Manual or workflow dispatch events → `NOTION_KNOWLEDGE_FILE_DB_ID`

Each Notion page records:

- Name (title)
- Status (Open/Closed based on GitHub state)
- Category (Issue, Pull Request, Discussion, Project Board, Manual)
- Last Synced timestamp
- Source URL and External ID when available

## Performance Telemetry

The module `metrics/performance_logger.py` appends JSONL records to `logs/sync_metrics.jsonl`. Each record captures:

- Timestamp (UTC)
- Event type
- Sync status (synced/skipped/error)
- Latency (ms)
- Metadata (database, page identifiers, error message)

When a `NOTION_PERFORMANCE_LOG_DB_ID` secret is provided the logger forwards summaries to Notion through the same API client.

## Validation

Terraform automation runs from the `.github/workflows/tfc-sync.yml` workflow which now sets `working-directory: ./infra` for every Terraform command. The workflow sequence ensures:

1. `terraform fmt -check`
2. `terraform init`
3. `terraform validate`
4. `terraform plan -input=false -no-color`

Local validation can be executed with:

```bash
terraform -chdir=infra fmt
terraform -chdir=infra validate
terraform -chdir=infra plan -input=false -no-color
```

Pytest coverage for the synchronization logic lives in `tests/test_notion_sync.py` and exercises event mapping as well as Notion client invocation.
