#!/usr/bin/env python3
"""Generate a commit summary suitable for posting to a discussion thread."""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple


def run_git(args: List[str]) -> str:
    result = subprocess.run(["git", *args], check=True, capture_output=True, text=True)
    return result.stdout.strip()


def determine_range(base: str | None, head: str) -> Tuple[str, str]:
    if base and set(base) != {"0"}:
        return base, head
    # fallback to previous commit
    try:
        previous = run_git(["rev-parse", f"{head}^" ])
    except subprocess.CalledProcessError:
        previous = run_git(["hash-object", "-t", "tree", "/dev/null"])
    return previous, head


def parse_functions(base: str, head: str, file_path: str) -> List[str]:
    try:
        diff_output = run_git([
            "diff",
            "--unified=0",
            f"{base}",
            f"{head}",
            "--",
            file_path,
        ])
    except subprocess.CalledProcessError:
        return []

    functions: List[str] = []
    for line in diff_output.splitlines():
        if line.startswith("@@"):
            signature = line.split("@@")[-1].strip()
            if signature:
                functions.append(signature)
    return functions


def summarize_changes(base: str, head: str) -> Dict[str, List[str]]:
    output = run_git(["diff", "--name-only", f"{base}", f"{head}"])
    files = [line for line in output.splitlines() if line]
    summary: Dict[str, List[str]] = {}

    for file_path in files:
        functions = parse_functions(base, head, file_path)
        if not functions:
            summary[file_path] = ["General updates"]
        else:
            summary[file_path] = sorted(set(functions))
    return summary


def gather_performance_notes(base: str, head: str) -> List[str]:
    stats = run_git(["diff", "--shortstat", f"{base}", f"{head}"])
    notes: List[str] = []
    if stats:
        notes.append(f"Diff footprint: {stats}.")

    perf_related = run_git(["log", "--format=%s", f"{base}..{head}"])
    if any(keyword in perf_related.lower() for keyword in ("perf", "speed", "optimiz")):
        notes.append("Commit messages indicate potential performance-oriented work.")

    if not notes:
        notes.append("No explicit performance considerations detected; monitor runtime metrics after deployment.")
    return notes


def build_summary(base: str, head: str, short_sha: str) -> str:
    file_summaries = summarize_changes(base, head)
    perf_notes = gather_performance_notes(base, head)

    lines = [f"📈 [A-08] Code Update Summary — {short_sha}", ""]
    if file_summaries:
        lines.append("**Files Updated**")
        for file_path, functions in sorted(file_summaries.items()):
            function_list = ", ".join(functions)
            lines.append(f"- `{file_path}` → {function_list}")
    else:
        lines.append("No files changed in this push.")

    lines.append("")
    lines.append("**Performance Notes**")
    for note in perf_notes:
        lines.append(f"- {note}")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=False)
    parser.add_argument("--head", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    base, head = determine_range(args.base, args.head)
    short_sha = run_git(["rev-parse", "--short", head])
    summary = build_summary(base, head, short_sha)

    args.output.write_text(summary, encoding="utf-8")


if __name__ == "__main__":
    main()
