"""Shared safe YAML frontmatter parsing for repository validators."""

from __future__ import annotations

from pathlib import Path

import yaml


def load_frontmatter(path: Path) -> tuple[dict[str, object] | None, str | None]:
    try:
        text = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as error:
        return None, f"cannot read file: {error}"
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, "YAML frontmatter is missing or does not start with '---'"

    closing_line = next(
        (index for index in range(1, len(lines)) if lines[index].strip() in {"---", "..."}),
        None,
    )
    if closing_line is None:
        return None, "YAML frontmatter has no closing '---' or '...' delimiter"

    source = "\n".join(lines[1:closing_line])
    try:
        metadata = yaml.safe_load(source)
    except yaml.YAMLError as error:
        mark = getattr(error, "problem_mark", None)
        line = f" at line {mark.line + 2}" if mark is not None else ""
        problem = getattr(error, "problem", None) or str(error).splitlines()[0]
        return None, f"invalid YAML frontmatter{line}: {problem}"
    except ValueError as error:
        # PyYAML's timestamp constructor raises ValueError for impossible dates such as
        # 2026-13-01 instead of a YAMLError; report it rather than crashing the validator.
        return None, f"invalid YAML frontmatter: {error}"

    if not isinstance(metadata, dict):
        return None, "YAML frontmatter must be a mapping"

    return metadata, None
