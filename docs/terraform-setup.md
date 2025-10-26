# Terraform Configuration

## Overview

This repository uses Terraform Cloud to manage infrastructure and configuration variables for the PR-CYBR-PERFORMANCE-AGENT.

## Files

- **main.tf**: Main Terraform configuration with backend setup
- **agent-variables.tf**: Variable declarations for agent configuration
- **.terraform/**: Local provider plugins (ignored by git)
- **.terraform.lock.hcl**: Dependency lock file (ignored by git)

## Terraform Cloud Setup

### Organization
- **Organization**: PR-CYBR
- **Workspace**: PR-CYBR-PERFORMANCE-AGENT

### Backend Configuration

The Terraform Cloud backend is configured in `main.tf`:

```hcl
terraform {
  cloud {
    organization = "PR-CYBR"
    
    workspaces {
      name = "PR-CYBR-PERFORMANCE-AGENT"
    }
  }
}
```

## GitHub Actions Integration

The `.github/workflows/tfc-sync.yml` workflow automates Terraform operations:

1. **On Pull Requests**: Runs `terraform plan` to validate changes
2. **On Push to Main**: Runs `terraform apply` to apply changes

### Required Secrets

- `TFC_TOKEN`: Terraform Cloud API token for authentication
- `AGENT_ACTIONS`: GitHub PAT for repository checkout

## Variables

All variables are declared in `agent-variables.tf` and their actual values are managed securely in Terraform Cloud. These include:

- Docker Hub credentials
- Global infrastructure URIs (Elasticsearch, Grafana, Kibana, Prometheus)
- Networking/security tokens (Tailscale, ZeroTier)
- Agent tokens (AGENT_ACTIONS, AGENT_COLLAB)

## Local Development

To work with this Terraform configuration locally:

1. Install Terraform CLI (>= 1.0)
2. Authenticate to Terraform Cloud:
   ```bash
   terraform login
   ```
3. Initialize the workspace:
   ```bash
   terraform init
   ```
4. Run plan to see changes:
   ```bash
   terraform plan
   ```

**Note**: Never run `terraform apply` locally unless you understand the implications. Use the GitHub Actions workflow for applying changes.

## Security

- All sensitive values are stored in Terraform Cloud, never in code
- State files are stored remotely in Terraform Cloud
- Local Terraform files (`.terraform/`, `*.tfstate`) are excluded via `.gitignore`
- Variable files (`*.tfvars`) are excluded to prevent credential leaks
