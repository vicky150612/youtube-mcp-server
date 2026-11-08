"""Line-ending policy checks (Stage 1 audit N-5)."""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def _index_line_endings() -> list[tuple[str, str]]:
    """Return (index line-ending info, path) for every tracked file."""
    result = subprocess.run(
        ["git", "ls-files", "--eol", "-z"],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    entries = []
    for entry in result.stdout.split("\0"):
        if not entry:
            continue
        info, _, path = entry.partition("\t")
        entries.append((info.split()[0], path))
    return entries


class LineEndingTests(unittest.TestCase):
    def test_gitattributes_normalises_text_to_lf(self) -> None:
        attributes = (REPOSITORY_ROOT / ".gitattributes").read_text(encoding="utf-8")
        self.assertIn("* text=auto eol=lf", attributes.splitlines())

    def test_no_tracked_text_file_is_stored_with_crlf(self) -> None:
        entries = _index_line_endings()
        self.assertTrue(entries, "git ls-files returned no tracked files")
        offending = sorted(path for info, path in entries if info in {"i/crlf", "i/mixed"})
        self.assertEqual(offending, [], f"files stored with CRLF or mixed endings: {offending}")


if __name__ == "__main__":
    unittest.main()
