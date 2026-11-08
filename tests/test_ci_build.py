"""Tests for the structural/syntax build check (C4)."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.ci_build import REQUIRED_DIRECTORIES, check_build

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class BuildCheckTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        for directory in REQUIRED_DIRECTORIES:
            (self.root / directory).mkdir(parents=True)
        (self.root / "scripts" / "tool.py").write_text("VALUE = 1\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def run_cli(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(REPOSITORY_ROOT / "scripts" / "ci_build.py"),
                "--root",
                str(self.root),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_complete_layout_passes(self) -> None:
        self.assertEqual(check_build(self.root), (1, []))

    def test_each_missing_required_directory_fails(self) -> None:
        for directory in REQUIRED_DIRECTORIES:
            with self.subTest(directory=directory):
                # Omitting a directory also omits the required directories nested inside it
                # (for example, tests/fixtures inside tests); each must be reported.
                omitted = [
                    candidate
                    for candidate in REQUIRED_DIRECTORIES
                    if candidate == directory or candidate.startswith(f"{directory}/")
                ]
                with tempfile.TemporaryDirectory() as other:
                    root = Path(other)
                    for present in REQUIRED_DIRECTORIES:
                        if present not in omitted:
                            (root / present).mkdir(parents=True, exist_ok=True)
                    self.assertFalse((root / directory).exists())
                    _, errors = check_build(root)
                    self.assertEqual(
                        errors,
                        [f"required directory is missing: {root / name}" for name in omitted],
                    )

    def test_python_syntax_error_fails(self) -> None:
        broken = self.root / "src" / "broken.py"
        broken.write_text("def broken(:\n", encoding="utf-8")
        _, errors = check_build(self.root)
        self.assertEqual(len(errors), 1)
        self.assertIn(str(broken), errors[0])

    def test_every_syntax_error_is_reported(self) -> None:
        for directory in ("src", "tests"):
            (self.root / directory / "broken.py").write_text("if True\n", encoding="utf-8")
        _, errors = check_build(self.root)
        self.assertEqual(len(errors), 2)

    def test_python_files_outside_checked_directories_are_ignored(self) -> None:
        (self.root / "brain" / "inbox" / "not_code.py").write_text("def (:\n", encoding="utf-8")
        self.assertEqual(check_build(self.root), (1, []))

    def test_cli_passes_on_complete_layout(self) -> None:
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("1 Python file(s) parsed", result.stdout)

    def test_cli_exits_nonzero_for_missing_directory(self) -> None:
        (self.root / "brain" / "archive").rmdir()
        result = self.run_cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("required directory is missing", result.stderr)
        self.assertIn("archive", result.stderr)

    def test_cli_exits_nonzero_for_syntax_error(self) -> None:
        (self.root / "tests" / "broken.py").write_text("def broken(:\n", encoding="utf-8")
        result = self.run_cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("broken.py", result.stderr)


if __name__ == "__main__":
    unittest.main()
