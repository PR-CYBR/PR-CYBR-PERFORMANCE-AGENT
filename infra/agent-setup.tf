#############################################
# PR-CYBR Agent Terraform Configuration     #
# Purpose: Mirror Terraform Cloud variables  #
#          into GitHub Actions secrets for   #
#          the PR-CYBR agent repository.     #
#############################################

terraform {
  required_version = ">= 1.6.0"

  required_providers {
    github = {
      source  = "integrations/github"
      version = "~> 6.4"
    }
  }
}

provider "github" {
  owner = "PR-CYBR"
  token = var.AGENT_ACTIONS
}

locals {
  repository_name = "PR-CYBR-PERFORMANCE-AGENT"

  github_secrets = {
    AGENT_ACTIONS                      = var.AGENT_ACTIONS
    AGENT_ID                           = var.AGENT_ID
    DOCKERHUB_TOKEN                    = var.DOCKERHUB_TOKEN
    DOCKERHUB_USERNAME                 = var.DOCKERHUB_USERNAME
    GLOBAL_DOMAIN                      = var.GLOBAL_DOMAIN
    NOTION_DISCUSSIONS_ARC_DB_ID       = var.NOTION_DISCUSSIONS_ARC_DB_ID
    NOTION_ISSUES_BACKLOG_DB_ID        = var.NOTION_ISSUES_BACKLOG_DB_ID
    NOTION_KNOWLEDGE_FILE_DB_ID        = var.NOTION_KNOWLEDGE_FILE_DB_ID
    NOTION_PAGE_ID                     = var.NOTION_PAGE_ID
    NOTION_PR_BACKLOG_DB_ID            = var.NOTION_PR_BACKLOG_DB_ID
    NOTION_PROJECT_BOARD_BACKLOG_DB_ID = var.NOTION_PROJECT_BOARD_BACKLOG_DB_ID
    NOTION_TASK_BACKLOG_DB_ID          = var.NOTION_TASK_BACKLOG_DB_ID
    NOTION_TOKEN                       = var.NOTION_TOKEN
    PR_CYBR_DOCKER_PASS                = var.PR_CYBR_DOCKER_PASS
    PR_CYBR_DOCKER_USER                = var.PR_CYBR_DOCKER_USER
    TFC_TOKEN                          = var.TFC_TOKEN
  }
}

resource "github_actions_secret" "agent" {
  for_each        = local.github_secrets
  repository      = local.repository_name
  secret_name     = each.key
  plaintext_value = each.value
}
