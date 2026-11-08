"""Tests for repository documentation validation (ADR 0003, I-6, N-3, SB-03)."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.markdown_links import github_anchor, heading_anchors, mask_code
from scripts.validate_docs import validate_docs

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class MarkdownHelperTests(unittest.TestCase):
    def test_mask_code_preserves_offsets_and_removes_code(self) -> None:
        text = "a `[[x]]` b\n```\n[[y]]\n```\nc"
        masked = mask_code(text)
        self.assertEqual(len(masked), len(text))
        self.assertNotIn("[[", masked)
        self.assertEqual(masked.count("\n"), text.count("\n"))

    def test_github_anchor_rules(self) -> None:
        self.assertEqual(github_anchor("9. Open decisions (OD)"), "9-open-decisions-od")
        self.assertEqual(
            github_anchor("Appendix A — Reference: YouTube API quota"),
            "appendix-a--reference-youtube-api-quota",
        )
        self.assertEqual(heading_anchors("# A\n## A\n"), {"a", "a-1"})


class DocumentationValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        (self.root / "docs" / "adr").mkdir(parents=True)
        shutil.copy(REPOSITORY_ROOT / "docs" / "srs.md", self.root / "docs" / "srs.md")
        note = self.root / "brain" / "resources" / "Note.md"
        note.parent.mkdir(parents=True)
        note.write_text("# Note\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def write(self, relative_path: str, content: str) -> None:
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def errors(self) -> list[str]:
        return validate_docs(self.root)[1]

    def test_valid_documentation_passes(self) -> None:
        self.write(
            "README.md",
            "See [SRS](docs/srs.md#9-open-decisions-od), [note](brain/resources/Note.md) "
            "and `FR-01`. Example syntax: `[[Note]]`.\n",
        )
        self.assertEqual(self.errors(), [])

    def test_wikilink_outside_code_fails(self) -> None:
        self.write("docs/guide.md", "See [[CI Pipeline]].\n")
        self.assertTrue(any("Obsidian wikilink" in error for error in self.errors()))

    def test_broken_relative_link_and_anchor_fail(self) -> None:
        self.write("docs/guide.md", "[a](missing.md) [b](srs.md#no-such-heading)\n")
        errors = self.errors()
        self.assertTrue(any("does not exist" in error for error in errors))
        self.assertTrue(any("no heading matching" in error for error in errors))

    def test_external_links_are_not_checked(self) -> None:
        self.write("docs/guide.md", "[Google](https://developers.google.com/youtube/v3)\n")
        self.assertEqual(self.errors(), [])

    def test_requirement_ids_are_checked(self) -> None:
        self.write("docs/guide.md", "Uses FR-1 and `NFR-42`.\n")
        errors = self.errors()
        self.assertTrue(any("'FR-1' is not in canonical" in error for error in errors))
        self.assertTrue(any("'NFR-42' is not defined" in error for error in errors))

    def test_adr_must_cite_a_brain_note(self) -> None:
        self.write("docs/adr/0001-example.md", "# ADR 0001\n\nNo citation.\n")
        self.assertTrue(any("SB-03" in error for error in self.errors()))
        self.write("docs/adr/0001-example.md", "# ADR\n[Note](../../brain/resources/Note.md)\n")
        self.assertEqual(self.errors(), [])

    def test_brain_directory_is_left_to_the_brain_validator(self) -> None:
        self.write("brain/index.md", "[[Note]]\n")
        self.assertEqual(self.errors(), [])

    def test_no_documentation_fails(self) -> None:
        empty = self.root / "empty"
        empty.mkdir()
        self.assertTrue(validate_docs(empty)[1])

    def test_cli_exits_nonzero_on_error(self) -> None:
        self.write("docs/guide.md", "See [[Missing]].\n")
        result = subprocess.run(
            [
                sys.executable,
                str(REPOSITORY_ROOT / "scripts" / "validate_docs.py"),
                "--root",
                str(self.root),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Obsidian wikilink", result.stderr)

    def test_repository_documentation_is_valid(self) -> None:
        file_count, errors = validate_docs(REPOSITORY_ROOT)
        self.assertGreater(file_count, 0)
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
