from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.validate_brain import validate_brain
from scripts.validate_skills import validate_skill, validate_skills

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
VALID_SKILL = """---
name: valid-skill
description: A valid skill description.
---
Instructions.
"""
VALID_NOTE = """---
title: Research note
type: research
sources:
  - https://example.test/source
---
Note body.
"""


class SkillValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.skill_directory = self.root / "skills" / "valid-skill"
        self.skill_directory.mkdir(parents=True)
        self.skill_file = self.skill_directory / "SKILL.md"

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_valid_skill_passes(self) -> None:
        self.skill_file.write_text(VALID_SKILL, encoding="utf-8")
        self.assertEqual(validate_skill(self.skill_file), [])

    def test_missing_frontmatter_fails(self) -> None:
        self.skill_file.write_text("No frontmatter.\n", encoding="utf-8")
        self.assertTrue(
            any("frontmatter" in error for error in validate_skill(self.skill_file))
        )

    def test_invalid_yaml_fails(self) -> None:
        self.skill_file.write_text("---\nname: [\n---\n", encoding="utf-8")
        self.assertTrue(
            any("invalid YAML" in error for error in validate_skill(self.skill_file))
        )

    def test_missing_required_field_fails(self) -> None:
        self.skill_file.write_text("---\nname: valid-skill\n---\n", encoding="utf-8")
        self.assertTrue(
            any("description" in error for error in validate_skill(self.skill_file))
        )

    def test_invalid_name_fails(self) -> None:
        content = VALID_SKILL.replace("name: valid-skill", "name: Invalid_Name")
        self.skill_file.write_text(content, encoding="utf-8")
        self.assertTrue(
            any("field 'name'" in error for error in validate_skill(self.skill_file))
        )

    def test_name_must_match_directory(self) -> None:
        content = VALID_SKILL.replace("name: valid-skill", "name: another-skill")
        self.skill_file.write_text(content, encoding="utf-8")
        self.assertTrue(
            any(
                "match containing directory" in error
                for error in validate_skill(self.skill_file)
            )
        )

    def test_empty_skills_directory_is_reported_as_initial_state(self) -> None:
        files, errors = validate_skills(self.root)
        self.assertEqual(files, [])
        self.assertEqual(errors, [])

    def test_missing_skills_directory_is_reported_as_initial_state(self) -> None:
        root_without_skills = self.root / "no-skills"
        root_without_skills.mkdir()
        files, errors = validate_skills(root_without_skills)
        self.assertEqual(files, [])
        self.assertEqual(errors, [])

    def test_invalid_skill_cli_exits_nonzero(self) -> None:
        self.skill_file.write_text("Missing frontmatter.\n", encoding="utf-8")
        result = subprocess.run(
            [
                sys.executable,
                str(REPOSITORY_ROOT / "scripts" / "validate_skills.py"),
                "--root",
                str(self.root),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("frontmatter", result.stderr)


class BrainValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.brain = self.root / "brain"
        self.brain.mkdir()

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def write_note(self, relative_path: str, content: str) -> Path:
        path = self.brain / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def test_valid_research_note_passes(self) -> None:
        self.write_note("resources/Research.md", VALID_NOTE)
        self.assertEqual(validate_brain(self.root), (1, 0, []))

    def test_missing_required_metadata_fails(self) -> None:
        self.write_note(
            "resources/Research.md",
            "---\ntitle: Research note\n---\nBody.\n",
        )
        _, _, errors = validate_brain(self.root)
        self.assertTrue(any("required field 'type'" in error for error in errors))
        self.assertTrue(any("required field 'sources'" in error for error in errors))

    def test_malformed_yaml_fails(self) -> None:
        self.write_note("resources/Research.md", "---\ntitle: [\n---\nBody.\n")
        _, _, errors = validate_brain(self.root)
        self.assertTrue(any("invalid YAML" in error for error in errors))

    def test_valid_wikilink_passes(self) -> None:
        self.write_note("resources/Target.md", VALID_NOTE)
        source = VALID_NOTE.replace("Note body.", "See [[Target]].")
        self.write_note("projects/Source.md", source)
        _, link_count, errors = validate_brain(self.root)
        self.assertEqual(link_count, 1)
        self.assertEqual(errors, [])

    def test_broken_wikilink_fails(self) -> None:
        self.write_note(
            "projects/Source.md",
            VALID_NOTE.replace("Note body.", "See [[Missing Note]]."),
        )
        _, _, errors = validate_brain(self.root)
        self.assertTrue(
            any("broken wikilink '[[Missing Note]]'" in error for error in errors)
        )

    def test_alias_wikilink_passes(self) -> None:
        self.write_note("resources/Target.md", VALID_NOTE)
        source = VALID_NOTE.replace("Note body.", "See [[Target|display name]].")
        self.write_note("projects/Source.md", source)
        _, _, errors = validate_brain(self.root)
        self.assertEqual(errors, [])

    def test_external_markdown_link_is_not_a_wikilink(self) -> None:
        source = VALID_NOTE.replace(
            "Note body.",
            "[External reference](https://example.test/reference).",
        )
        self.write_note("projects/Source.md", source)
        self.assertEqual(validate_brain(self.root), (1, 0, []))

    def test_case_insensitive_extension_and_nested_path_resolve(self) -> None:
        self.write_note("resources/Nested/Target.MD", VALID_NOTE)
        source = VALID_NOTE.replace("Note body.", "See [[resources/nested/target.md]].")
        self.write_note("projects/Source.md", source)
        _, _, errors = validate_brain(self.root)
        self.assertEqual(errors, [])

    def test_index_and_log_are_schema_exempt_but_links_are_checked(self) -> None:
        self.write_note("resources/Target.md", VALID_NOTE)
        self.write_note("index.md", "Start here: [[Target]].\n")
        self.write_note("log.md", "Run log: [[Target|target note]].\n")
        note_count, link_count, errors = validate_brain(self.root)
        self.assertEqual(note_count, 1)
        self.assertEqual(link_count, 2)
        self.assertEqual(errors, [])

    def test_broken_brain_link_cli_exits_nonzero(self) -> None:
        self.write_note(
            "projects/Source.md",
            VALID_NOTE.replace("Note body.", "See [[Missing]]."),
        )
        result = subprocess.run(
            [
                sys.executable,
                str(REPOSITORY_ROOT / "scripts" / "validate_brain.py"),
                "--root",
                str(self.root),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("broken wikilink", result.stderr)


class CiCommandTests(unittest.TestCase):
    def test_failing_test_makes_unittest_command_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            test_file = Path(temporary_directory) / "test_failure.py"
            test_file.write_text(
                "import unittest\n"
                "class ExpectedFailure(unittest.TestCase):\n"
                "    def test_failure(self):\n"
                "        self.fail('intentional CI command probe')\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "unittest",
                    "discover",
                    "-s",
                    temporary_directory,
                ],
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertNotEqual(result.returncode, 0)

    def test_lint_error_makes_ruff_command_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            source_file = Path(temporary_directory) / "unused_import.py"
            source_file.write_text("import os\n", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "ruff",
                    "check",
                    "--isolated",
                    "--select",
                    "F401",
                    str(source_file),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
