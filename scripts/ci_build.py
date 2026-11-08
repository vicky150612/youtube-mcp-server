"""Run structural and Python syntax checks until an application build exists."""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
# Directories whose Python files are syntax-checked.
PYTHON_DIRECTORIES = ("src", "tests", "scripts")
# Directories every checkout must contain (AGENTS.md section 3 and section 11). Git does not
# track empty directories, so each one needs at least one tracked file.
REQUIRED_DIRECTORIES = (
    *PYTHON_DIRECTORIES,
    "tests/fixtures",
    "brain/inbox",
    "brain/projects",
    "brain/areas",
    "brain/resources",
    "brain/archive",
)


def check_build(root: Path) -> tuple[int, list[str]]:
    """Return the number of parsed Python files and any build-check errors."""
    missing = [
        root / directory for directory in REQUIRED_DIRECTORIES if not (root / directory).is_dir()
    ]
    if missing:
        return 0, [f"required directory is missing: {directory}" for directory in missing]

    python_files = sorted(
        path for directory in PYTHON_DIRECTORIES for path in (root / directory).rglob("*.py")
    )
    errors: list[str] = []
    for path in python_files:
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (OSError, SyntaxError, UnicodeError) as error:
            errors.append(f"{path}: {error}")
    return len(python_files), errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=REPOSITORY_ROOT,
        help="repository root (defaults to the repository containing this script)",
    )
    arguments = parser.parse_args(argv)

    file_count, errors = check_build(arguments.root.resolve())
    if errors:
        for error in errors:
            print(f"Build check failed: {error}", file=sys.stderr)
        return 1

    print(
        f"Structural/syntax build check passed: {file_count} Python file(s) parsed. "
        "No application build target is configured in this repository yet."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
