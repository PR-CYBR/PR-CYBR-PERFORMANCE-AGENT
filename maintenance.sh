#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
# shellcheck source=scripts/common.sh
source "${SCRIPT_DIR}/scripts/common.sh"

NON_INTERACTIVE=false
FORCE_ACTIONS=false
RETENTION_DAYS=30
DRY_RUN=false

usage() {
    cat <<'USAGE'
Usage: maintenance.sh [options]

Perform routine maintenance tasks for the PR-CYBR Performance agent.

Options:
  --non-interactive        Run without prompts; actions needing confirmation are
                           skipped unless --force or --yes is provided.
  -y, --yes, --force       Auto-confirm prompts (implies --non-interactive).
  --retention-days <days>  Remove logs older than <days> (default: 30).
  --dry-run                Show what would be cleaned without deleting files.
  --help                   Show this help message and exit.
USAGE
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --non-interactive)
            NON_INTERACTIVE=true
            ;;
        -y|--yes|--assume-yes|--force)
            NON_INTERACTIVE=true
            FORCE_ACTIONS=true
            set_prompt_mode "auto-yes"
            ;;
        --retention-days)
            shift || { echo "Missing value for --retention-days" >&2; exit 2; }
            if ! [[ "$1" =~ ^[0-9]+$ ]]; then
                echo "Invalid retention days: $1" >&2
                exit 2
            fi
            RETENTION_DAYS="$1"
            ;;
        --dry-run)
            DRY_RUN=true
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            usage
            exit 2
            ;;
    esac
    shift
done

if [[ "$NON_INTERACTIVE" == true ]]; then
    if [[ "$FORCE_ACTIONS" == true ]]; then
        set_prompt_mode "auto-yes"
    else
        set_prompt_mode "auto-no"
    fi
fi

initialize_script "maintenance" "Operations Maintenance"

SCRIPT_STATUS="success"
ERROR_CONTEXT=""

on_error() {
    local exit_code="$1"
    local line="$2"
    SCRIPT_STATUS="failed"
    ERROR_CONTEXT="line ${line} (exit code ${exit_code})"
    log_error "Maintenance encountered an error at ${ERROR_CONTEXT}."
    add_report_line "Failure encountered at ${ERROR_CONTEXT}."
}

on_exit() {
    local exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        SCRIPT_STATUS="failed"
    fi
    if [[ "$SCRIPT_STATUS" == "success" ]]; then
        log_info "Maintenance completed successfully."
        add_report_line "Maintenance completed without errors."
    else
        log_error "Maintenance failed; see ${LOG_FILE} for details."
    fi
    finalize_report "$SCRIPT_STATUS"
}

trap 'on_error $? $LINENO' ERR
trap 'on_exit' EXIT

add_report_line "Repository root: ${PROJECT_ROOT}"
add_report_line "Log retention: ${RETENTION_DAYS} day(s)"
add_report_line "Dry run: ${DRY_RUN}"
if [[ "$NON_INTERACTIVE" == true ]]; then
    if [[ "$FORCE_ACTIONS" == true ]]; then
        add_report_line "Mode: non-interactive (auto-confirm)"
    else
        add_report_line "Mode: non-interactive (safe defaults)"
    fi
else
    add_report_line "Mode: interactive"
fi

cleanup_old_logs() {
    ensure_workspace

    mapfile -t old_logs < <(find "$LOG_DIR" -type f -name '*.log' -mtime +"$RETENTION_DAYS" -print 2>/dev/null | sort)
    local count=${#old_logs[@]}

    if (( count == 0 )); then
        add_report_line "Log rotation: no files required deletion."
        log_info "No log files older than ${RETENTION_DAYS} day(s)."
        return 0
    fi

    if [[ "$DRY_RUN" == true ]]; then
        add_report_line "Log rotation dry-run identified ${count} file(s)."
        log_info "Dry run: the following log files would be removed:"
        printf '  %s\n' "${old_logs[@]}" | tee -a "$LOG_FILE"
        return 0
    fi

    if ! confirm_action "Remove ${count} log file(s) older than ${RETENTION_DAYS} day(s)?" "N"; then
        add_report_line "Log rotation skipped by operator."
        add_warning "Log rotation skipped; ${count} old file(s) remain."
        return 0
    fi

    local removed=0
    local file
    for file in "${old_logs[@]}"; do
        if rm -f "$file"; then
            ((removed++))
        else
            add_warning "Failed to remove ${file}"
        fi
    done

    add_report_line "Log rotation removed ${removed} file(s)."
    log_info "Removed ${removed} old log file(s)."
}

summarize_disk_usage() {
    ensure_workspace
    local log_usage="0"
    local report_usage="0"
    if [[ -d "$LOG_DIR" ]]; then
        log_usage=$(du -sh "$LOG_DIR" 2>/dev/null | awk '{print $1}')
    fi
    if [[ -d "$REPORT_DIR" ]]; then
        report_usage=$(du -sh "$REPORT_DIR" 2>/dev/null | awk '{print $1}')
    fi
    add_report_line "Disk usage - logs: ${log_usage}, reports: ${report_usage}"
    log_info "Current disk usage -> logs: ${log_usage}, reports: ${report_usage}."
}

generate_git_snapshot() {
    if ! command -v git >/dev/null 2>&1; then
        add_warning "Git is not available; skipping repository snapshot."
        return 0
    fi
    if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        add_warning "Not executing inside a Git repository; skipping snapshot."
        return 0
    fi

    if command -v python3 >/dev/null 2>&1; then
        local snapshot
        snapshot=$(python3 <<'PY'
import json
import subprocess


def safe_output(cmd, default="unknown"):
    try:
        return subprocess.check_output(cmd, text=True).strip()
    except subprocess.CalledProcessError:
        return default


branch = safe_output(["git", "rev-parse", "--abbrev-ref", "HEAD"])
commit = safe_output(["git", "rev-parse", "HEAD"])

try:
    status_raw = subprocess.check_output(["git", "status", "--short"], text=True)
    status_lines = [line.rstrip() for line in status_raw.splitlines()]
except subprocess.CalledProcessError:
    status_lines = []

snapshot = {
    "branch": branch,
    "commit": commit,
    "dirty": bool(status_lines),
    "status": status_lines,
}

print(json.dumps(snapshot, indent=2))
PY
)
        local snapshot_file
        snapshot_file=$(create_json_snapshot "maintenance-git" "$snapshot")
        local relative
        relative=$(relative_to_project "$snapshot_file")
        add_report_line "Repository snapshot saved to ${relative}."
        log_info "Repository snapshot written to ${relative}."
    else
        local status_lines
        status_lines=$(git status --short 2>/dev/null || true)
        local dirty="clean"
        if [[ -n "$status_lines" ]]; then
            dirty="dirty"
        fi
        local text_file="${REPORT_DIR}/maintenance-git-$(timestamp_for_file).txt"
        {
            echo "Branch: $(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)"
            echo "Commit: $(git rev-parse HEAD 2>/dev/null || echo unknown)"
            echo "State: ${dirty}"
            echo "Status:"
            if [[ -n "$status_lines" ]]; then
                while IFS= read -r line; do
                    printf '  %s\n' "$line"
                done <<< "$status_lines"
            else
                echo "  (clean)"
            fi
        } > "$text_file"
        local relative
        relative=$(relative_to_project "$text_file")
        add_report_line "Repository snapshot saved to ${relative}."
        log_info "Repository snapshot written to ${relative}."
    fi
}

collect_service_health() {
    local health_file
    health_file="${REPORT_DIR}/maintenance-health-$(timestamp_for_file).txt"
    {
        echo "Timestamp: $(timestamp)"
        echo "Hostname: $(hostname)"
        echo "Uptime:"
        uptime || echo "uptime command unavailable"
    } > "$health_file"
    local relative
    relative=$(relative_to_project "$health_file")
    add_report_line "Health summary written to ${relative}."
    log_info "Health summary generated at ${relative}."
}

main() {
    cleanup_old_logs
    summarize_disk_usage
    generate_git_snapshot
    collect_service_health
}

main
