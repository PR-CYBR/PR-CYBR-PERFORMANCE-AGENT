############################################################
# Terraform Cloud Workspace Variable Definitions for Agent #
# Populate these values within Terraform Cloud; placeholders #
# below document the required variable names and intent.     #
############################################################

# --- Docker / Registry ---
DOCKERHUB_TOKEN          = "set-in-tfc"
DOCKERHUB_USERNAME       = "set-in-tfc"
PR_CYBR_DOCKER_USER      = "set-in-tfc"
PR_CYBR_DOCKER_PASS      = "set-in-tfc"
DOCKER_USERNAME          = "set-in-tfc"
DOCKER_PASSWORD          = "set-in-tfc"

# --- Global Infrastructure URIs ---
GLOBAL_DOMAIN            = "example.pr-cybr.local"
GLOBAL_ELASTIC_URI       = "https://elastic.pr-cybr.local"
GLOBAL_GRAFANA_URI       = "https://grafana.pr-cybr.local"
GLOBAL_KIBANA_URI        = "https://kibana.pr-cybr.local"
GLOBAL_PROMETHEUS_URI    = "https://prometheus.pr-cybr.local"

# --- Networking / Security ---
GLOBAL_TAILSCALE_AUTHKEY   = "set-in-tfc"
GLOBAL_TRAEFIK_ACME_EMAIL  = "ops@pr-cybr.io"
GLOBAL_TRAEFIK_ENTRYPOINTS = "web,websecure"
GLOBAL_ZEROTIER_NETWORK_ID = "set-in-tfc"

# --- GitHub / Terraform Automation ---
GITHUB_TOKEN = "set-in-tfc"
TFC_TOKEN    = "set-in-tfc"

# --- Agent Tokens ---
AGENT_ACTIONS = "set-in-tfc"
AGENT_COLLAB  = "set-in-tfc"

# --- Application Configuration ---
FLASK_ENV             = "development"
FLASK_DEBUG           = "1"
ASSISTANT_ID          = "your_default_assistant_id_here"
DB_HOST               = "localhost"
DB_PORT               = "5432"
DB_NAME               = "agent_db"
DB_USER               = "agent_user"
DB_PASSWORD           = "set-in-tfc"
API_KEY               = "set-in-tfc"
SECRET_KEY            = "set-in-tfc"

# --- Logging & Observability ---
LOG_LEVEL = "INFO"

# --- Cross-Origin Configuration ---
CORS_ALLOWED_ORIGINS = "http://localhost:3000,http://yourdomain.com"

# --- External Integrations ---
EXTERNAL_SERVICE_URL = "https://api.external-service.com"
