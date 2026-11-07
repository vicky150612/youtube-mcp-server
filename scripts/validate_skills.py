"""Validate all Agent Skills in the repository."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

if __package__:
    from .frontmatter import load_frontmatter
else:
    from frontmatter import load_frontmatter

SKILL_NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def validate_skill(path: Path) -> list[str]:
    metadata, frontmatter_error = load_frontmatter(path)
    if frontmatter_error is not None:
        return [f"{path}: {frontmatter_error}"]
    if metadata is None:
        return [f"{path}: YAML frontmatter must be a mapping"]

    errors: list[str] = []
    name = metadata.get("name")
    if not isinstance(name, str) or not name:
        errors.append(f"{path}: required field 'name' must be a non-empty string")
    else:
        if len(name) > 64 or SKILL_NAME.fullmatch(name) is None:
            errors.append(
                f"{path}: field 'name' must be 1-64 lowercase letters, numbers, "
                "or single hyphen-separated segments"
            )
        if name != path.parent.name:
            errors.append(
                f"{path}: field 'name' must match containing directory '{path.parent.name}'"
            )

    description = metadata.get("description")
    if not isinstance(description, str) or not description.strip():
        errors.append(
            f"{path}: required field 'description' must be a non-empty string"
        )
    elif len(description) > 1024:
        errors.append(f"{path}: field 'description' must not exceed 1024 characters")

    compatibility = metadata.get("compatibility")
    if compatibility is not None and (
        not isinstance(compatibility, str) or not 1 <= len(compatibility) <= 500
    ):
        errors.append(
            f"{path}: field 'compatibility' must be a string of 1-500 characters"
        )

    license_name = metadata.get("license")
    if license_name is not None and (
        not isinstance(license_name, str) or not license_name.strip()
    ):
        errors.append(f"{path}: field 'license' must be a non-empty string")

    extra_metadata = metadata.get("metadata")
    if extra_metadata is not None and (
        not isinstance(extra_metadata, dict)
        or any(
            not isinstance(key, str) or not isinstance(value, str)
            for key, value in extra_metadata.items()
        )
    ):
        errors.append(
            f"{path}: field 'metadata' must be a mapping of strings to strings"
        )

    allowed_tools = metadata.get("allowed-tools")
    if allowed_tools is not None and not isinstance(allowed_tools, str):
        errors.append(f"{path}: field 'allowed-tools' must be a string")

    return errors


def validate_skills(root: Path) -> tuple[list[Path], list[str]]:
    skills_directory = root / "skills"
    if not skills_directory.is_dir():
        return [], []

    skill_files = sorted(skills_directory.rglob("SKILL.md"))
    errors = [error for path in skill_files for error in validate_skill(path)]
    return skill_files, errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=REPOSITORY_ROOT,
        help="repository root (defaults to the repository containing this script)",
    )
    arguments = parser.parse_args(argv)

    skill_files, errors = validate_skills(arguments.root.resolve())
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        print(f"Skill validation failed: {len(errors)} error(s).", file=sys.stderr)
        return 1

    if skill_files:
        print(
            f"Skill validation passed: {len(skill_files)} SKILL.md file(s) validated."
        )
    else:
        print(
            "Skill validation passed: no SKILL.md files exist yet; "
            "the initial repository state has nothing to validate."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
