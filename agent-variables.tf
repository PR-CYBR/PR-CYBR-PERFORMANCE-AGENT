#############################################
# PR-CYBR Agent Variables (Generic Baseline)
# This file declares variables expected by
# Terraform Cloud across all PR-CYBR Agents.
# Real values are securely managed in TFC.
#############################################

# --- Docker / Registry ---
variable "DOCKERHUB_TOKEN" {
  type        = string
  sensitive   = true
  description = "Docker Hub access token"
}

variable "DOCKERHUB_USERNAME" {
  type        = string
  description = "Docker Hub username"
}

variable "PR_CYBR_DOCKER_USER" {
  type        = string
  description = "GitHub Actions secret for Docker Hub username"
}

variable "PR_CYBR_DOCKER_PASS" {
  type        = string
  sensitive   = true
  description = "GitHub Actions secret for Docker Hub password"
}

variable "DOCKER_USERNAME" {
  type        = string
  description = "Generic Docker registry username used by workflows"
}

variable "DOCKER_PASSWORD" {
  type        = string
  sensitive   = true
  description = "Generic Docker registry password used by workflows"
}

# --- Global Infrastructure URIs ---
variable "GLOBAL_DOMAIN" {
  type        = string
  description = "Root DNS domain for PR-CYBR services"
}

variable "GLOBAL_ELASTIC_URI" {
  type        = string
  description = "Elasticsearch endpoint"
}

variable "GLOBAL_GRAFANA_URI" {
  type        = string
  description = "Grafana endpoint"
}

variable "GLOBAL_KIBANA_URI" {
  type        = string
  description = "Kibana endpoint"
}

variable "GLOBAL_PROMETHEUS_URI" {
  type        = string
  description = "Prometheus endpoint"
}

# --- Networking / Security ---
variable "GLOBAL_TAILSCALE_AUTHKEY" {
  type        = string
  sensitive   = true
  description = "Auth key for Tailscale VPN/DNS"
}

variable "GLOBAL_TRAEFIK_ACME_EMAIL" {
  type        = string
  description = "Email used by Traefik for Let's Encrypt"
}

variable "GLOBAL_TRAEFIK_ENTRYPOINTS" {
  type        = string
  description = "Default entrypoints for Traefik"
}

variable "GLOBAL_ZEROTIER_NETWORK_ID" {
  type        = string
  sensitive   = true
  description = "ZeroTier overlay network ID"
}

# --- GitHub / Terraform Automation ---
variable "GITHUB_TOKEN" {
  type        = string
  sensitive   = true
  description = "GitHub token used by Terraform Cloud sync workflows"
}

variable "TFC_TOKEN" {
  type        = string
  sensitive   = true
  description = "Terraform Cloud API token for CLI authentication"
}

# --- Agent Tokens ---
variable "AGENT_ACTIONS" {
  type        = string
  sensitive   = true
  description = "Token for CI/CD pipelines (builds, tests, deploys)"
}

variable "AGENT_COLLAB" {
  type        = string
  sensitive   = true
  description = "Token for governance, discussions, issues, project boards"
}

# --- Application Configuration ---
variable "FLASK_ENV" {
  type        = string
  description = "Flask environment mode (development/production)"
}

variable "FLASK_DEBUG" {
  type        = string
  description = "Flask debug flag"
}

variable "ASSISTANT_ID" {
  type        = string
  description = "Default assistant identifier for the agent"
}

variable "DB_HOST" {
  type        = string
  description = "Database host name"
}

variable "DB_PORT" {
  type        = string
  description = "Database port"
}

variable "DB_NAME" {
  type        = string
  description = "Database name"
}

variable "DB_USER" {
  type        = string
  description = "Database user"
}

variable "DB_PASSWORD" {
  type        = string
  sensitive   = true
  description = "Database user password"
}

variable "API_KEY" {
  type        = string
  sensitive   = true
  description = "Generic external API key"
}

variable "SECRET_KEY" {
  type        = string
  sensitive   = true
  description = "Flask secret key"
}

# --- Logging & Observability ---
variable "LOG_LEVEL" {
  type        = string
  description = "Application log level"
}

# --- Cross-Origin Configuration ---
variable "CORS_ALLOWED_ORIGINS" {
  type        = string
  description = "Comma-separated list of allowed CORS origins"
}

# --- External Integrations ---
variable "EXTERNAL_SERVICE_URL" {
  type        = string
  description = "URL for the external service integration"
}
