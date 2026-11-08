"""Validate repository Markdown outside the Second Brain.

Rules (docs/adr/0003-linking-naming-and-requirement-references.md):
- no Obsidian wikilinks outside code formatting;
- relative Markdown links and their #anchors must resolve;
- requirement IDs must be canonical and defined in docs/srs.md;
- every ADR must cite at least one Brain note (SRS SB-03).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

if __package__:
    from .markdown_links import (
        check_relative_link,
        line_number,
        load_defined_requirement_ids,
        markdown_links,
        requirement_id_errors,
        wikilinks,
    )
else:
    from markdown_links import (
        check_relative_link,
        line_number,
        load_defined_requirement_ids,
        markdown_links,
        requirement_id_errors,
        wikilinks,
    )

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_EXTENSIONS = {".md", ".markdown"}
# Directories that are not repository documentation: the Brain has its own validator; the
# others are tool or environment directories.
SKIPPED_DIRECTORIES = {".git", "brain", ".obsidian", ".venv", "node_modules", ".ruff_cache"}
ADR_FILE = re.compile(r"\d{4}-.+\.md\Z")


def documentation_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if any(part in SKIPPED_DIRECTORIES for part in relative.parts[:-1]):
            continue
        if path.is_file() and path.suffix.casefold() in MARKDOWN_EXTENSIONS:
            files.append(path)
    return files


def _cites_brain_note(path: Path, text: str, root: Path) -> bool:
    brain = (root / "brain").resolve()
    for _, target in markdown_links(text):
        path_part = target.partition("#")[0]
        if not path_part or "://" in target:
            continue
        resolved = (path.parent / path_part).resolve()
        if resolved.suffix == ".md" and brain in resolved.parents and resolved.is_file():
            return True
    return False


def validate_docs(root: Path) -> tuple[int, list[str]]:
    files = documentation_files(root)
    if not files:
        return 0, [f"{root}: no Markdown documentation files found"]
    defined_ids = load_defined_requirement_ids(root)
    errors: list[str] = []
    for path in files:
        relative = path.relative_to(root).as_posix()
        try:
            text = path.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError) as error:
            errors.append(f"{relative}: cannot read Markdown file: {error}")
            continue
        for offset, link_text in wikilinks(text):
            errors.append(
                f"{relative}:{line_number(text, offset)}: Obsidian wikilink '[[{link_text}]]' "
                "is not allowed outside brain/; use a relative Markdown link"
            )
        for offset, target in markdown_links(text):
            problem = check_relative_link(path, target, root)
            if problem:
                errors.append(f"{relative}:{line_number(text, offset)}: {problem}")
        for offset, message in requirement_id_errors(text, defined_ids):
            errors.append(f"{relative}:{line_number(text, offset)}: {message}")
        if path.parent == root / "docs" / "adr" and ADR_FILE.match(path.name):
            if not _cites_brain_note(path, text, root):
                errors.append(
                    f"{relative}: ADR must cite at least one Brain note with a relative link (SB-03)"
                )
    return len(files), errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=REPOSITORY_ROOT,
        help="repository root (defaults to the repository containing this script)",
    )
    arguments = parser.parse_args(argv)

    file_count, errors = validate_docs(arguments.root.resolve())
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        print(f"Documentation validation failed: {len(errors)} error(s).", file=sys.stderr)
        return 1
    print(f"Documentation validation passed: {file_count} Markdown file(s) checked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
