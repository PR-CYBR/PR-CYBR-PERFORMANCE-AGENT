#!/usr/bin/env bash

# Shared utilities for PR-CYBR agent scripts.
# This file is intended to be sourced by bash scripts and therefore should not
# use `set -e` or similar options.

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
LOG_DIR_DEFAULT="${PROJECT_ROOT}/logs"
REPORT_DIR_DEFAULT="${PROJECT_ROOT}/reports"

LOG_DIR="${LOG_DIR:-$LOG_DIR_DEFAULT}"
REPORT_DIR="${REPORT_DIR:-$REPORT_DIR_DEFAULT}"

CURRENT_SCRIPT=""
CURRENT_DESCRIPTION=""
LOG_FILE=""
REPORT_FILE=""

PROMPT_MODE="${PROMPT_MODE:-ask}"

# shellcheck disable=SC2034
REPORT_LINES=()
WARNINGS=()

ensure_workspace() {
    mkdir -p "$LOG_DIR" "$REPORT_DIR"
}

timestamp() {
    date -u '+%Y-%m-%dT%H:%M:%SZ'
}

timestamp_for_file() {
    date -u '+%Y%m%d-%H%M%S'
}

set_prompt_mode() {
    PROMPT_MODE="$1"
}

confirm_action() {
    local prompt="$1"
    local default_choice="${2:-N}"
    local response

    case "$PROMPT_MODE" in
        auto-yes)
            log_info "${prompt} -> auto-confirmed (yes)"
            return 0
            ;;
        auto-no)
            log_warn "${prompt} -> auto-declined (no)"
            return 1
            ;;
        *)
            read -r -p "${prompt} [${default_choice}] " response
            response="${response:-$default_choice}"
            case "$response" in
                [Yy]*)
                    return 0
                    ;;
                *)
                    return 1
                    ;;
            esac
            ;;
    esac
}

log_base() {
    local level="$1"
    shift
    local message="$*"
    local ts
    ts="$(timestamp)"
    local formatted="${ts} [${level}] ${message}"

    if [[ -n "$LOG_FILE" ]]; then
        if [[ "$level" == "ERROR" ]]; then
            echo "$formatted" | tee -a "$LOG_FILE" >&2
        else
            echo "$formatted" | tee -a "$LOG_FILE"
        fi
    else
        if [[ "$level" == "ERROR" ]]; then
            echo "$formatted" >&2
        else
            echo "$formatted"
        fi
    fi
}

log_info() {
    log_base "INFO" "$@"
}

log_warn() {
    log_base "WARN" "$@"
}

log_error() {
    log_base "ERROR" "$@"
}

add_report_line() {
    REPORT_LINES+=("$1")
}

add_warning() {
    WARNINGS+=("$1")
    log_warn "$1"
}

initialize_script() {
    local script_name="$1"
    local description="$2"

    CURRENT_SCRIPT="$script_name"
    CURRENT_DESCRIPTION="$description"

    ensure_workspace

    local ts
    ts="$(timestamp_for_file)"

    LOG_FILE="${LOG_DIR}/${script_name}-${ts}.log"
    REPORT_FILE="${REPORT_DIR}/${script_name}-${ts}.md"

    : > "$LOG_FILE"

    REPORT_LINES=()
    WARNINGS=()

    log_info "Initialized ${description} workflow. Log file: ${LOG_FILE}"
}

finalize_report() {
    local status="$1"

    {
        echo "# ${CURRENT_DESCRIPTION} Report"
        echo ""
        echo "- Script: ${CURRENT_SCRIPT}.sh"
        echo "- Status: ${status}"
        echo "- Generated: $(timestamp)"
        echo ""
        if ((${#REPORT_LINES[@]} > 0)); then
            echo "## Summary"
            for line in "${REPORT_LINES[@]}"; do
                echo "- ${line}"
            done
            echo ""
        fi
        if ((${#WARNINGS[@]} > 0)); then
            echo "## Warnings"
            for warning in "${WARNINGS[@]}"; do
                echo "- ${warning}"
            done
            echo ""
        fi
        echo "## Artifacts"
        echo "- Log file: ${LOG_FILE}"
    } > "$REPORT_FILE"

    log_info "Report written to ${REPORT_FILE}"
}

create_json_snapshot() {
    local name="$1"
    local content="$2"
    local snapshot_file="${REPORT_DIR}/${name}-$(timestamp_for_file).json"
    printf '%s\n' "$content" > "$snapshot_file"
    echo "$snapshot_file"
}

relative_to_project() {
    local absolute_path="$1"
    if [[ "$absolute_path" == "$PROJECT_ROOT"* ]]; then
        echo ".${absolute_path#$PROJECT_ROOT}"
    else
        echo "$absolute_path"
    fi
}

