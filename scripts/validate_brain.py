"""Validate Second Brain note metadata, wikilinks, relative links and requirement IDs.

The note schema is defined in docs/adr/0002-brain-note-schema.md and the link and
requirement-reference conventions in docs/adr/0003-linking-naming-and-requirement-references.md.
"""

from __future__ import annotations

import argparse
import datetime
import re
import sys
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse

if __package__:
    from .frontmatter import load_frontmatter
    from .markdown_links import (
        check_relative_link,
        headings,
        line_number,
        load_defined_requirement_ids,
        markdown_links,
        requirement_id_errors,
        wikilinks,
    )
else:
    from frontmatter import load_frontmatter
    from markdown_links import (
        check_relative_link,
        headings,
        line_number,
        load_defined_requirement_ids,
        markdown_links,
        requirement_id_errors,
        wikilinks,
    )

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_EXTENSIONS = {".md", ".markdown"}
EXEMPT_NOTE_PATHS = {Path("index.md"), Path("log.md")}
REQUIRED_FIELDS = ("title", "type", "author", "created", "tags", "sources")
OPTIONAL_FIELDS = ("aliases", "status")
NOTE_TYPES = ("research", "ai-session")
NOTE_STATUSES = ("draft", "ingested")
ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}\Z")


def _markdown_files(brain_directory: Path) -> list[Path]:
    return sorted(
        path
        for path in brain_directory.rglob("*")
        if path.is_file()
        and path.suffix.casefold() in MARKDOWN_EXTENSIONS
        and ".obsidian" not in path.relative_to(brain_directory).parts
    )


def _is_string_list(value: object) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(isinstance(item, str) and item.strip() for item in value)
    )


def _valid_date(value: object) -> bool:
    if isinstance(value, datetime.datetime):
        return False
    if isinstance(value, datetime.date):
        return True
    if isinstance(value, str) and ISO_DATE.match(value):
        try:
            datetime.date.fromisoformat(value)
        except ValueError:
            return False
        return True
    return False


def _source_error(source: str, root: Path) -> str | None:
    parsed = urlparse(source)
    if parsed.scheme in {"http", "https"}:
        return None if parsed.netloc else f"source '{source}' is not a valid URL"
    if parsed.scheme:
        return f"source '{source}' must be an http(s) URL or a repository-relative path"
    candidate = PurePosixPath(source)
    if candidate.is_absolute() or ".." in candidate.parts:
        return f"source '{source}' must be a repository-relative path inside the repository"
    if not (root / Path(*candidate.parts)).exists():
        return f"source path '{source}' does not exist"
    return None


def _note_metadata_errors(path: Path, root: Path) -> list[str]:
    display = path.relative_to(root).as_posix()
    metadata, frontmatter_error = load_frontmatter(path)
    if frontmatter_error is not None:
        return [f"{display}: {frontmatter_error}"]
    if metadata is None:
        return [f"{display}: YAML frontmatter must be a mapping"]

    errors: list[str] = []
    unknown = sorted(str(key) for key in metadata if key not in REQUIRED_FIELDS + OPTIONAL_FIELDS)
    for key in unknown:
        errors.append(f"{display}: field '{key}' is not part of the note schema (ADR 0002)")
    missing = [field for field in REQUIRED_FIELDS if field not in metadata]
    for field in missing:
        errors.append(f"{display}: required field '{field}' is missing")

    title = metadata.get("title")
    if "title" in metadata and (not isinstance(title, str) or not title.strip()):
        errors.append(f"{display}: required field 'title' must be a non-empty string")

    note_type = metadata.get("type")
    if "type" in metadata and note_type not in NOTE_TYPES:
        errors.append(f"{display}: required field 'type' must be one of: {', '.join(NOTE_TYPES)}")

    author = metadata.get("author")
    if "author" in metadata:
        if not _is_string_list(author):
            errors.append(f"{display}: required field 'author' must be a non-empty list of strings")
        elif any("@" in name for name in author):
            errors.append(
                f"{display}: field 'author' must use role names or Git usernames, not email addresses"
            )

    if "created" in metadata and not _valid_date(metadata.get("created")):
        errors.append(f"{display}: required field 'created' must be a date in YYYY-MM-DD form")

    if "tags" in metadata and not _is_string_list(metadata.get("tags")):
        errors.append(f"{display}: required field 'tags' must be a non-empty list of strings")

    sources = metadata.get("sources")
    if "sources" in metadata:
        if not _is_string_list(sources):
            errors.append(
                f"{display}: required field 'sources' must be a non-empty list of strings"
            )
        else:
            for source in sources:
                problem = _source_error(source.strip(), root)
                if problem:
                    errors.append(f"{display}: {problem}")

    if "aliases" in metadata and not _is_string_list(metadata.get("aliases")):
        errors.append(f"{display}: field 'aliases' must be a non-empty list of strings")

    if "status" in metadata and metadata.get("status") not in NOTE_STATUSES:
        errors.append(f"{display}: field 'status' must be one of: {', '.join(NOTE_STATUSES)}")

    return errors


def _normalized_target(target: str) -> str:
    normalized = target.replace("\\", "/").strip().lstrip("/")
    normalized = str(PurePosixPath(normalized)) if normalized else ""
    if normalized in {"", "."}:
        return ""
    suffix = PurePosixPath(normalized).suffix.casefold()
    if suffix in MARKDOWN_EXTENSIONS:
        normalized = normalized[: -len(suffix)]
    return normalized.casefold()


def _resolve_note(target: str, brain_directory: Path, notes: list[Path]) -> Path | None:
    normalized = _normalized_target(target)
    if not normalized:
        return None
    target_has_path = "/" in normalized
    for note in notes:
        relative = note.relative_to(brain_directory).as_posix()
        relative_without_extension = relative[: -len(note.suffix)]
        if target_has_path:
            if normalized in {relative.casefold(), relative_without_extension.casefold()}:
                return note
        elif normalized in {note.name.casefold(), note.stem.casefold()}:
            return note
    return None


def _wikilink_error(
    link_text: str, source: Path, brain_directory: Path, notes: list[Path]
) -> str | None:
    target = link_text.split("|", maxsplit=1)[0].strip()
    note_part, separator, reference = target.partition("#")
    block_part, block_separator, _ = note_part.partition("^")
    if block_separator:
        note_part = block_part
    if not note_part.strip() and separator:
        resolved: Path | None = source
    else:
        resolved = _resolve_note(note_part, brain_directory, notes)
    if resolved is None:
        return f"broken wikilink '[[{link_text}]]'"
    if separator and not reference.startswith("^"):
        wanted = reference.strip().casefold()
        available = {heading.casefold() for heading in headings(resolved.read_text("utf-8-sig"))}
        if wanted not in available:
            return f"wikilink '[[{link_text}]]' names a heading that does not exist"
    return None


def validate_brain(root: Path) -> tuple[int, int, list[str]]:
    brain_directory = root / "brain"
    if not brain_directory.is_dir():
        return 0, 0, [f"{brain_directory}: Brain directory does not exist"]

    notes = _markdown_files(brain_directory)
    applicable_notes = [
        path for path in notes if path.relative_to(brain_directory) not in EXEMPT_NOTE_PATHS
    ]
    errors = [error for path in applicable_notes for error in _note_metadata_errors(path, root)]
    defined_ids = load_defined_requirement_ids(root)

    link_count = 0
    for path in notes:
        relative_path = path.relative_to(root).as_posix()
        try:
            text = path.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError) as error:
            errors.append(f"{relative_path}: cannot read Markdown file: {error}")
            continue
        for offset, link_text in wikilinks(text):
            link_count += 1
            problem = _wikilink_error(link_text.strip(), path, brain_directory, notes)
            if problem:
                errors.append(f"{relative_path}:{line_number(text, offset)}: {problem}")
        for offset, target in markdown_links(text):
            problem = check_relative_link(path, target, root)
            if problem:
                errors.append(f"{relative_path}:{line_number(text, offset)}: {problem}")
        for offset, message in requirement_id_errors(text, defined_ids):
            errors.append(f"{relative_path}:{line_number(text, offset)}: {message}")

    return len(applicable_notes), link_count, errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=REPOSITORY_ROOT,
        help="repository root (defaults to the repository containing this script)",
    )
    arguments = parser.parse_args(argv)

    note_count, link_count, errors = validate_brain(arguments.root.resolve())
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        print(f"Brain validation failed: {len(errors)} error(s).", file=sys.stderr)
        return 1

    print(
        f"Brain validation passed: {note_count} note(s) checked for metadata; "
        f"{link_count} wikilink(s) resolved."
    )
    if note_count == 0:
        print(
            "Only explicitly exempt index.md/log.md files (or no notes) are present; "
            "no research-note metadata was silently skipped."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
