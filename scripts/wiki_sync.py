#!/usr/bin/env python3
"""Synchronize documentation to the repository wiki.

This script copies Markdown files from the project `docs/` tree into the
checked-out wiki working tree, recreating the directory structure and updating
sidebar navigation based on the available documents. Any files that no longer
exist in `docs/` are removed from the wiki mirror.
"""
from __future__ import annotations

import argparse
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


@dataclass
class DocEntry:
    """Represents a documentation file and its relative path within docs."""

    relative_path: Path

    @property
    def wiki_link(self) -> str:
        parts = [p.replace(" ", "-") for p in self.relative_path.with_suffix("").parts]
        return "/".join(parts)

    @property
    def display_name(self) -> str:
        stem = self.relative_path.stem.replace("-", " ")
        return " ".join(word.capitalize() for word in stem.split())

    def sidebar_line(self, indent_level: int) -> str:
        indent = " " * (indent_level * 2)
        link = self.wiki_link
        name = self.display_name
        return f"{indent}- [[{link}|{name}]]"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mirror docs into wiki")
    parser.add_argument("--docs", type=Path, required=True, help="Path to docs directory")
    parser.add_argument("--wiki", type=Path, required=True, help="Path to checked out wiki repository")
    return parser.parse_args()


def collect_entries(docs_root: Path) -> List[DocEntry]:
    entries: List[DocEntry] = []
    for path in sorted(docs_root.rglob("*.md")):
        relative = path.relative_to(docs_root)
        entries.append(DocEntry(relative))
    return entries


def clean_removed_files(entries: Iterable[DocEntry], wiki_root: Path) -> None:
    valid_paths = {wiki_root / entry.relative_path for entry in entries}
    preserved = {wiki_root / "_Sidebar.md", wiki_root / "Home.md"}
    valid_paths.update(preserved)
    for path in wiki_root.rglob("*.md"):
        if path not in valid_paths:
            path.unlink()

    # remove now-empty directories
    for directory in sorted({p.parent for p in valid_paths}, reverse=True):
        if directory.exists():
            try:
                directory.rmdir()
            except OSError:
                pass


def mirror_docs(entries: Iterable[DocEntry], docs_root: Path, wiki_root: Path) -> None:
    for entry in entries:
        source = docs_root / entry.relative_path
        destination = wiki_root / entry.relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

    readme = docs_root / "README.md"
    if readme.exists():
        home_target = wiki_root / "Home.md"
        shutil.copy2(readme, home_target)


def build_sidebar(entries: Iterable[DocEntry]) -> str:
    lines: List[str] = ["# Documentation"]
    top_level = {}

    for entry in entries:
        parts = list(entry.relative_path.parts)
        if len(parts) == 1:
            top_level.setdefault("_root", []).append(entry)
        else:
            top_level.setdefault(parts[0], []).append(entry)

    if "_root" in top_level:
        lines.append("## Overview")
        for doc in top_level["_root"]:
            lines.append(doc.sidebar_line(indent_level=0))

    for section in sorted(k for k in top_level.keys() if k != "_root"):
        section_entries = sorted(top_level[section], key=lambda d: d.relative_path)
        section_title = section.replace("-", " ").replace("_", " ")
        lines.append(f"## {section_title.title()}")
        for doc in section_entries:
            indent = max(0, doc.relative_path.parts.__len__() - 2)
            lines.append(doc.sidebar_line(indent_level=indent))

    lines.append("\n> _Automatically generated. Do not edit manually._")
    return "\n".join(lines) + "\n"


def write_sidebar(wiki_root: Path, content: str) -> None:
    sidebar = wiki_root / "_Sidebar.md"
    sidebar.write_text(content, encoding="utf-8")


def main() -> None:
    args = parse_args()
    docs_root: Path = args.docs.resolve()
    wiki_root: Path = args.wiki.resolve()

    if not docs_root.exists():
        raise FileNotFoundError(f"Docs directory not found: {docs_root}")
    if not wiki_root.exists():
        raise FileNotFoundError(f"Wiki directory not found: {wiki_root}")

    entries = collect_entries(docs_root)
    mirror_docs(entries, docs_root, wiki_root)
    clean_removed_files(entries, wiki_root)
    sidebar_content = build_sidebar(entries)
    write_sidebar(wiki_root, sidebar_content)


if __name__ == "__main__":
    main()
