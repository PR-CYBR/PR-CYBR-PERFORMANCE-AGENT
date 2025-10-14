#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
# shellcheck source=scripts/common.sh
source "${SCRIPT_DIR}/scripts/common.sh"

NON_INTERACTIVE=false
FORCE_ACTIONS=false

usage() {
    cat <<'USAGE'
Usage: setup.sh [options]

Prepare the PR-CYBR Performance agent workspace for local or CI automation.

Options:
  --non-interactive    Run without prompting; operations that require
                       confirmation are skipped unless --force is also set.
  -y, --yes, --force   Auto-confirm prompts (implies --non-interactive).
  --help               Show this message and exit.
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

initialize_script "setup" "Environment Setup"

SCRIPT_STATUS="success"
ERROR_CONTEXT=""

on_error() {
    local exit_code="$1"
    local line="$2"
    SCRIPT_STATUS="failed"
    ERROR_CONTEXT="line ${line} (exit code ${exit_code})"
    log_error "Setup encountered an error at ${ERROR_CONTEXT}."
    add_report_line "Failure encountered at ${ERROR_CONTEXT}."
}

on_exit() {
    local exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        SCRIPT_STATUS="failed"
    fi
    if [[ "$SCRIPT_STATUS" == "success" ]]; then
        log_info "Setup completed successfully."
        add_report_line "Environment setup completed without errors."
    else
        log_error "Setup failed; see ${LOG_FILE} for details."
    fi
    finalize_report "$SCRIPT_STATUS"
}

trap 'on_error $? $LINENO' ERR
trap 'on_exit' EXIT

add_report_line "Repository root: ${PROJECT_ROOT}"
if [[ "$NON_INTERACTIVE" == true ]]; then
    if [[ "$FORCE_ACTIONS" == true ]]; then
        add_report_line "Mode: non-interactive (auto-confirm)"
    else
        add_report_line "Mode: non-interactive (safe defaults)"
    fi
else
    add_report_line "Mode: interactive"
fi

check_dependencies() {
    local missing=()
    local dependency
    local dependencies=("python3" "pip" "git")

    for dependency in "${dependencies[@]}"; do
        if command -v "$dependency" >/dev/null 2>&1; then
            log_info "Dependency '${dependency}' is available."
        else
            missing+=("$dependency")
        fi
    done

    if ((${#missing[@]} > 0)); then
        local missing_list
        missing_list=$(IFS=", "; echo "${missing[*]}")
        add_warning "Missing dependencies: ${missing_list}"
        add_report_line "Missing dependencies detected: ${missing_list}"
        if [[ "$NON_INTERACTIVE" == true ]] && [[ "$FORCE_ACTIONS" != true ]]; then
            log_error "Cannot continue without required dependencies in non-interactive mode."
            return 1
        fi
        if ! confirm_action "Continue without installing missing dependencies?" "N"; then
            log_error "User aborted due to missing dependencies."
            return 1
        fi
        add_report_line "Continuing despite missing dependencies: ${missing_list}"
    else
        add_report_line "All required dependencies are available."
    fi
}

verify_repository_layout() {
    local paths=("config" "scripts" "src" "tests" "requirements.txt" "setup.py")
    local missing_paths=()
    local path

    for path in "${paths[@]}"; do
        if [[ -e "${PROJECT_ROOT}/${path}" ]]; then
            log_info "Verified presence of ${path}."
        else
            missing_paths+=("$path")
        fi
    done

    if ((${#missing_paths[@]} > 0)); then
        local missing_list
        missing_list=$(IFS=", "; echo "${missing_paths[*]}")
        add_warning "Repository components missing: ${missing_list}"
        add_report_line "Missing repository components: ${missing_list}"
        return 1
    fi

    add_report_line "Repository layout verified."
}

capture_python_environment() {
    if ! command -v python3 >/dev/null 2>&1; then
        add_warning "Python3 not available; skipping environment capture."
        return 0
    fi

    local snapshot
    snapshot=$(python3 <<'PY'
import json
import platform
import sys

data = {
    "python_version": sys.version.split()[0],
    "implementation": platform.python_implementation(),
    "platform": platform.platform(),
}

print(json.dumps(data, indent=2))
PY
)

    local snapshot_file
    snapshot_file=$(create_json_snapshot "setup-environment" "$snapshot")
    local relative
    relative=$(relative_to_project "$snapshot_file")
    add_report_line "Environment snapshot saved to ${relative}."
    log_info "Captured Python environment details at ${relative}."
}

summarize_requirements() {
    local requirements_file="${PROJECT_ROOT}/requirements.txt"
    if [[ ! -f "$requirements_file" ]]; then
        add_warning "requirements.txt not found; skipping dependency summary."
        return 0
    fi

    local total
    total=$(grep -Ecv '^\s*(#|$)' "$requirements_file" || true)
    add_report_line "requirements.txt entries: ${total}"
    log_info "Detected ${total} requirement entries."
}

create_workspace_directories() {
    ensure_workspace
    add_report_line "Verified log directory: ${LOG_DIR}"
    add_report_line "Verified report directory: ${REPORT_DIR}"
}

main() {
    create_workspace_directories
    check_dependencies
    verify_repository_layout
    capture_python_environment
    summarize_requirements
}

main
