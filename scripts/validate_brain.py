"""Validate Second Brain note metadata and internal Obsidian wikilinks."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path, PurePosixPath

if __package__:
    from .frontmatter import load_frontmatter
else:
    from frontmatter import load_frontmatter

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WIKILINK = re.compile(r"\[\[([^\]\n]+)\]\]")
MARKDOWN_EXTENSIONS = {".md", ".markdown"}
EXEMPT_NOTE_PATHS = {Path("index.md"), Path("log.md")}


def _markdown_files(brain_directory: Path) -> list[Path]:
    return sorted(
        path
        for path in brain_directory.rglob("*")
        if path.is_file() and path.suffix.casefold() in MARKDOWN_EXTENSIONS
    )


def _note_metadata_errors(path: Path) -> list[str]:
    metadata, frontmatter_error = load_frontmatter(path)
    if frontmatter_error is not None:
        return [f"{path}: {frontmatter_error}"]
    if metadata is None:
        return [f"{path}: YAML frontmatter must be a mapping"]

    errors: list[str] = []
    for field in ("title", "type"):
        value = metadata.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(
                f"{path}: required field '{field}' must be a non-empty string"
            )

    sources = metadata.get("sources")
    if isinstance(sources, str):
        valid_sources = bool(sources.strip())
    elif isinstance(sources, list):
        valid_sources = bool(sources) and all(
            isinstance(source, str) and source.strip() for source in sources
        )
    else:
        valid_sources = False
    if not valid_sources:
        errors.append(
            f"{path}: required field 'sources' must be a non-empty string or list of strings"
        )

    return errors


def _normalized_target(target: str) -> str:
    normalized = target.replace("\\", "/").strip().lstrip("/")
    normalized = re.split(r"[#^]", normalized, maxsplit=1)[0]
    normalized = str(PurePosixPath(normalized))
    if normalized in {"", "."}:
        return ""
    suffix = PurePosixPath(normalized).suffix.casefold()
    if suffix in MARKDOWN_EXTENSIONS:
        normalized = normalized[: -len(suffix)]
    return normalized.casefold()


def _link_resolves(target: str, brain_directory: Path, notes: list[Path]) -> bool:
    normalized = _normalized_target(target)
    if not normalized:
        return False

    target_has_path = "/" in normalized
    for note in notes:
        relative = note.relative_to(brain_directory).as_posix()
        relative_without_extension = relative[: -len(note.suffix)]
        if target_has_path:
            if normalized in {
                relative.casefold(),
                relative_without_extension.casefold(),
            }:
                return True
        else:
            if normalized in {
                note.name.casefold(),
                note.stem.casefold(),
            }:
                return True

    return False


def validate_brain(root: Path) -> tuple[int, int, list[str]]:
    brain_directory = root / "brain"
    if not brain_directory.is_dir():
        return 0, 0, [f"{brain_directory}: Brain directory does not exist"]

    notes = _markdown_files(brain_directory)
    applicable_notes = [
        path
        for path in notes
        if path.relative_to(brain_directory) not in EXEMPT_NOTE_PATHS
    ]
    errors = [
        error for path in applicable_notes for error in _note_metadata_errors(path)
    ]

    link_count = 0
    for path in notes:
        try:
            text = path.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError) as error:
            relative_path = path.relative_to(root).as_posix()
            errors.append(f"{relative_path}: cannot read Markdown file: {error}")
            continue
        for match in WIKILINK.finditer(text):
            link_count += 1
            link_text = match.group(1).strip()
            target = link_text.split("|", maxsplit=1)[0].strip()
            line = text.count("\n", 0, match.start()) + 1
            if not _link_resolves(target, brain_directory, notes):
                relative_path = path.relative_to(root).as_posix()
                errors.append(
                    f"{relative_path}:{line}: broken wikilink '[[{link_text}]]'"
                )

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
