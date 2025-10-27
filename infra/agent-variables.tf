#############################################
# PR-CYBR Performance Agent Terraform Inputs
# These variables align with the Terraform
# Cloud workspace schema for agent A-08.
#############################################

variable "AGENT_ACTIONS" {
  description = "Token that authorizes CI/CD automation for the performance agent"
  type        = string
  sensitive   = true
}

variable "NOTION_TOKEN" {
  description = "Integration token for Notion API access"
  type        = string
  sensitive   = true
}

variable "NOTION_PAGE_ID" {
  description = "Root Notion page identifier used for contextual linking"
  type        = string
}

variable "NOTION_DISCUSSIONS_ARC_DB_ID" {
  description = "Database ID for archiving GitHub discussions"
  type        = string
}

variable "NOTION_ISSUES_BACKLOG_DB_ID" {
  description = "Database ID that mirrors the GitHub issues backlog"
  type        = string
}

variable "NOTION_KNOWLEDGE_FILE_DB_ID" {
  description = "Database ID for associating knowledge base files with GitHub activity"
  type        = string
}

variable "NOTION_PROJECT_BOARD_BACKLOG_DB_ID" {
  description = "Database ID for project board backlog synchronization"
  type        = string
}

variable "NOTION_TASK_BACKLOG_DB_ID" {
  description = "Database ID for actionable task synchronization from GitHub events"
  type        = string
}

variable "TFC_TOKEN" {
  description = "Terraform Cloud user or team token used for workspace operations"
  type        = string
  sensitive   = true
}
