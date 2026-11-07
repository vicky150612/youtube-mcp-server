"""Run structural and Python syntax checks until an application build exists."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_DIRECTORIES = ("src", "tests", "scripts")


def main() -> int:
    missing = [
        REPOSITORY_ROOT / directory
        for directory in REQUIRED_DIRECTORIES
        if not (REPOSITORY_ROOT / directory).is_dir()
    ]
    if missing:
        for directory in missing:
            print(
                f"Build check failed: required directory is missing: {directory}",
                file=sys.stderr,
            )
        return 1

    python_files = sorted(
        path
        for directory in REQUIRED_DIRECTORIES
        for path in (REPOSITORY_ROOT / directory).rglob("*.py")
    )
    for path in python_files:
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (OSError, SyntaxError) as error:
            print(f"Build check failed: {path}: {error}", file=sys.stderr)
            return 1

    print(
        f"Structural/syntax build check passed: {len(python_files)} Python file(s) parsed. "
        "No application build target is configured in this repository yet."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
