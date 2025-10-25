# Agent Documentation

This document provides operational guidance for collaborating with the performance agent and its integrations.

## Overview

- The performance agent now ships with a modular Notion sync runner that emits structured JSON logs for every operation and aggregates failures into a final summary. This prevents a single exception from halting the entire sync loop while still surfacing actionable diagnostics.
- Dry-run support (`DRY_RUN=true`) allows contributors to exercise handlers locally or in CI without contacting the Notion API. The CLI lives at `python -m notion_sync.cli` and respects both CLI flags and the environment variable.

## Setup Instructions

1. Install dependencies via `pip install -r requirements.txt`.
2. Register any custom Notion operations in `notion_sync/registry.py` before invoking the CLI or workflows.
3. Use the provided `Makefile` recipes (`make notion-test`, `make notion-dry-run`) to keep local workflows aligned with CI expectations.

## Usage

- Trigger the `setup-dry-run` GitHub Actions workflow with `workflow_dispatch` when validating new Notion handlers against staging or sample payloads.
- Monitor GitHub Actions logs and the Notion activity feed during the initial production rollout. If repeated failures appear, configure an alerting integration such as a Slack webhook to notify the on-call channel.
- Always work from a feature branch that follows the spec-bootstrap branching model (for example, `feature/<feature-name>`) before opening a pull request into the long-lived branches.
