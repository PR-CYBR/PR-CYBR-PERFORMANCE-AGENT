# Notion Sync

## Future Enhancements
- Schedule a GitHub Action or coordinate with an external polling service to periodically query the Notion API for recently edited pages, ensuring that GitHub stays synchronized even when changes originate from Notion.
- Use the GitHub identifiers already captured on each Notion page (issue and pull request numbers) to drive outbound GitHub REST API calls that can create or close issues and pull requests, move or update project cards, and post comments on discussions as edits occur in Notion.
- Explore wiring Notion webhooks into an intermediary such as an AWS Lambda function, which can then trigger a repository dispatch or workflow_run event, because GitHub Actions cannot receive inbound webhooks directly.

## Required Data for Two-Way Linking
- **GitHub Issue or Pull Request Number**: Stored on the Notion page as part of the synced metadata, enabling the automation to map a Notion task back to its corresponding GitHub record.
- **Notion Page ID**: Persisted within GitHub (for example in front matter, structured issue body data, or a custom field) so that automations can call back into the correct Notion resource.
