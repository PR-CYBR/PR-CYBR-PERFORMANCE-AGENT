# Configuration Guide

This document describes the required secrets and variables needed for the PR-CYBR-PERFORMANCE-AGENT to function properly.

## Required GitHub Secrets

GitHub Secrets are encrypted environment variables used for sensitive data. Configure these in your repository settings under **Settings → Secrets and variables → Actions → Secrets**.

### 1. AGENT_ACTIONS
- **Type:** GitHub Personal Access Token (PAT)
- **Purpose:** Allows automated workflows to interact with the repository
- **Required Scopes:** 
  - `repo` (Full control of private repositories)
  - `workflow` (Update GitHub Action workflows)
- **How to create:**
  1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
  2. Click "Generate new token (classic)"
  3. Select the required scopes
  4. Copy the token and add it as a repository secret

### 2. NOTION_TOKEN
- **Type:** Notion Integration Token
- **Purpose:** Enables synchronization between GitHub and Notion databases
- **How to create:**
  1. Go to [Notion Integrations](https://www.notion.so/my-integrations)
  2. Click "New integration"
  3. Give it a name (e.g., "PR-CYBR Agent")
  4. Copy the "Internal Integration Token"
  5. Share your Notion databases with this integration
  6. Add the token as a repository secret

## Required GitHub Variables

GitHub Variables are non-sensitive configuration values. Configure these in your repository settings under **Settings → Secrets and variables → Actions → Variables**.

### Notion Database IDs

All of the following variables should contain Notion database IDs (32-character alphanumeric strings):

1. **NOTION_DISCUSSIONS_ARC_DB_ID**
   - Purpose: Stores archived discussions
   - Example: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`

2. **NOTION_ISSUES_BACKLOG_DB_ID**
   - Purpose: Tracks GitHub issues in Notion
   - Example: `b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7`

3. **NOTION_KNOWLEDGE_FILE_DB_ID**
   - Purpose: Stores knowledge base and documentation
   - Example: `c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8`

4. **NOTION_PAGE_ID**
   - Purpose: Main Notion page for the project
   - Example: `d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9`

5. **NOTION_PR_BACKLOG_DB_ID**
   - Purpose: Tracks pull requests in Notion
   - Example: `e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0`

6. **NOTION_PROJECT_BOARD_BACKLOG_DB_ID**
   - Purpose: Project board for tracking work items
   - Example: `f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1`

7. **NOTION_TASK_BACKLOG_DB_ID**
   - Purpose: Task management and backlog
   - Example: `g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2`

## How to Find Notion Database IDs

1. Open your Notion database in a web browser
2. Copy the URL from the address bar
3. The database ID is the 32-character string after the workspace name and before the `?v=`
   
   Example URL: `https://www.notion.so/myworkspace/a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6?v=...`
   
   Database ID: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`

## Verification

After configuring all secrets and variables, you can verify the setup by:

1. Running the "Verify Environment Variables" workflow manually:
   - Go to Actions → Verify Environment Variables → Run workflow

2. Pushing a commit to the `main` branch (the workflow runs automatically)

The workflow will check all required configuration and report any missing values.

## Troubleshooting

### Workflow fails with "Missing required secret/variable"

**Solution:** Ensure you've added the secret or variable in the correct location:
- Secrets: `Settings → Secrets and variables → Actions → Secrets`
- Variables: `Settings → Secrets and variables → Actions → Variables`

### Notion sync doesn't work

**Common issues:**
1. **Integration not shared with databases:** Make sure your Notion integration has been shared with all the databases
2. **Wrong database IDs:** Double-check that the database IDs are correct and complete (32 characters)
3. **Invalid token:** Regenerate your Notion integration token and update the secret

### AGENT_ACTIONS permission errors

**Solution:** Ensure your GitHub PAT has the required scopes:
- `repo` - Full control of private repositories
- `workflow` - Update GitHub Action workflows

## Additional Resources

- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [GitHub Variables Documentation](https://docs.github.com/en/actions/learn-github-actions/variables)
- [Notion API Documentation](https://developers.notion.com/)
- [Notion Integration Setup](https://www.notion.so/help/create-integrations-with-the-notion-api)
