# Agent Documentation

This document provides information about the agent's functionality, setup, and usage.

## Overview

The PR-CYBR Performance Agent orchestrates telemetry collection, audits, and DevX reporting across the ecosystem. Supporting documents include workflow diagrams (`workflows/sync_map.mmd`) and Codex summaries for rapid situational awareness.

## Setup Instructions

- Review `reports/agent_sync_map.json` and accompanying templates before enabling automated runs.
- Install dashboard dependencies with `pip install -r requirements.txt` when exposing the FastAPI-based DevX UI.

## Usage

- Launch the dashboard locally via `uvicorn dashboard.app:app --reload` to validate synchronization data.
- Capture CI output in `reports/ci_logs/` and cross-reference audits in `reports/self_audit.md`.
