# Notion Sync Configuration

This repository synchronises GitHub activity to a collection of Notion databases.
All configuration is sourced from Terraform Cloud workspace variables that are
mirrored into GitHub repository secrets. Those secrets are exported to the
workflow runtime through the `env:` block so that automation and local tooling
can access them.

## Required Environment Variables

| Variable | Purpose |
| --- | --- |
| `NOTION_TOKEN` | Notion internal integration token with access to all PR-CYBR databases. |
| `NOTION_TASK_DB` | Database ID for the task tracking database. |
| `NOTION_PR_DB` | Database ID for the pull request tracking database. |
| `NOTION_PROJECT_DB` | Database ID for the overarching project portfolio database. |
| `NOTION_DISCUSSION_DB` | Database ID for cross-repo discussion tracking. |

These variables are required by runtime components (see
`src/shared/notion_config.py`) and any missing value will halt execution with a
clear error that points back to secret provisioning.

## Database Schema

All Notion databases used by this project are expected to expose the following
common fields:

| Property | Type | Description |
| --- | --- | --- |
| `Status` | Select | Workflow state (for example: Backlog, In Progress, Review, Complete). |
| `GitHub URL` | URL | Direct link to the associated GitHub issue, pull request, or discussion. |
| `Identifier` | Title | Primary human-readable identifier (e.g., `OPS-123`, PR title). |
| `Tags` | Multi-select | Labels for filtering, typically mapped from GitHub labels. |
| `Assignee` | Person | Owner accountable for the task or review. |
| `Linked Issue/PR` | Relation | Cross-links between tasks, issues, PRs, and discussions. |

Additional fields may exist per database (e.g., story points on the task
database), but the properties above are the required contract that automation
relies upon.

## Secret Provisioning Flow

The provisioning process mirrors the approach defined in
[`spec-bootstrap`](https://github.com/PR-CYBR/spec-bootstrap/):

1. **Terraform Cloud workspace variables** – In the workspace dedicated to this
   repository, create the following sensitive environment variables with the
   values noted above: `NOTION_TOKEN`, `NOTION_TASK_DB`, `NOTION_PR_DB`,
   `NOTION_PROJECT_DB`, and `NOTION_DISCUSSION_DB`.
2. **Terraform to GitHub secrets mapping** – Run the Terraform pipeline (via the
   `tfc-sync` workflow or `terraform apply`) so that the workspace variables are
   surfaced as GitHub repository secrets of the same name. This mirrors the
   pattern established in `spec-bootstrap` for propagating secrets.
3. **Workflow consumption** – The `.github/workflows/tfc-sync.yml` workflow
   exports each secret into its environment block. Application code reads them
   via `os.environ`, providing a uniform interface for both CI and local
   development.

Following these steps keeps Notion credentials out of the public repository
while ensuring automation has the data required to sync GitHub activity.
