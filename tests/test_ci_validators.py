from __future__ import annotations

import datetime
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.validate_brain import validate_brain
from scripts.validate_skills import validate_skill, validate_skills

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
BRAIN_INGEST_TEMPLATE = (
    REPOSITORY_ROOT / ".claude" / "skills" / "brain-ingest" / "assets" / "research-note.tmpl"
)
VALID_SKILL = """---
name: valid-skill
description: A valid skill description. Use when testing the validator.
---
# Valid skill

## Purpose
Test the validator. Background: [Target note](../../../brain/resources/Target.md).

## Inputs
None.

## Workflow
1. Run.

## Outputs
A result.

## Limitations
None.
"""
VALID_NOTE = """---
title: Research note
type: research
author:
  - Person 1
created: 2026-11-07
tags:
  - research
sources:
  - https://example.test/source
---
Note body.
"""


class SkillValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.skills_root = self.root / ".claude" / "skills"
        self.skill_directory = self.skills_root / "valid-skill"
        self.skill_directory.mkdir(parents=True)
        self.skill_file = self.skill_directory / "SKILL.md"
        brain_note = self.root / "brain" / "resources" / "Target.md"
        brain_note.parent.mkdir(parents=True)
        brain_note.write_text(VALID_NOTE, encoding="utf-8")

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def errors_for(self, content: str) -> list[str]:
        self.skill_file.write_text(content, encoding="utf-8")
        return validate_skill(self.skill_file, self.root)

    def test_valid_skill_passes(self) -> None:
        self.assertEqual(self.errors_for(VALID_SKILL), [])

    def test_missing_frontmatter_fails(self) -> None:
        self.assertTrue(
            any("frontmatter" in error for error in self.errors_for("No frontmatter.\n"))
        )

    def test_invalid_yaml_fails(self) -> None:
        errors = self.errors_for("---\nname: [\n---\n")
        self.assertTrue(any("invalid YAML" in error for error in errors))

    def test_missing_required_field_fails(self) -> None:
        errors = self.errors_for(VALID_SKILL.replace("description: A valid", "summary: A valid"))
        self.assertTrue(any("description" in error for error in errors))

    def test_invalid_name_fails(self) -> None:
        errors = self.errors_for(VALID_SKILL.replace("name: valid-skill", "name: Invalid_Name"))
        self.assertTrue(any("field 'name'" in error for error in errors))

    def test_name_must_match_directory(self) -> None:
        errors = self.errors_for(VALID_SKILL.replace("name: valid-skill", "name: another-skill"))
        self.assertTrue(any("match containing directory" in error for error in errors))

    # The two tests below previously asserted that an empty or missing skills directory passed.
    # ADR 0001 makes both a validation failure so that CI cannot pass vacuously.
    def test_empty_skills_directory_fails(self) -> None:
        self.skill_directory.rmdir()
        files, errors = validate_skills(self.root)
        self.assertEqual(files, [])
        self.assertTrue(any("no Agent Skills found" in error for error in errors))

    def test_missing_skills_directory_fails(self) -> None:
        root_without_skills = self.root / "no-skills"
        root_without_skills.mkdir()
        files, errors = validate_skills(root_without_skills)
        self.assertEqual(files, [])
        self.assertTrue(any("skill directory does not exist" in error for error in errors))

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

    def test_discovered_skill_passes(self) -> None:
        self.skill_file.write_text(VALID_SKILL, encoding="utf-8")
        files, errors = validate_skills(self.root, ["valid-skill"])
        self.assertEqual(files, [self.skill_file])
        self.assertEqual(errors, [])

    def test_missing_required_skill_fails(self) -> None:
        self.skill_file.write_text(VALID_SKILL, encoding="utf-8")
        _, errors = validate_skills(self.root, ["brain-ingest"])
        self.assertTrue(any("required skill 'brain-ingest' is missing" in e for e in errors))

    def test_wrong_case_skill_file_fails(self) -> None:
        (self.skill_directory / "Skill.md").write_text(VALID_SKILL, encoding="utf-8")
        _, errors = validate_skills(self.root)
        self.assertTrue(any("missing SKILL.md" in error for error in errors))

    def test_file_directly_in_skills_root_fails(self) -> None:
        self.skill_file.write_text(VALID_SKILL, encoding="utf-8")
        (self.skills_root / "SKILL.md").write_text(VALID_SKILL, encoding="utf-8")
        _, errors = validate_skills(self.root)
        self.assertTrue(any("unexpected file" in error for error in errors))

    def test_missing_required_section_fails(self) -> None:
        errors = self.errors_for(VALID_SKILL.replace("## Limitations\nNone.\n", ""))
        self.assertTrue(any("section for limitations" in error for error in errors))

    def test_empty_body_fails(self) -> None:
        errors = self.errors_for("---\nname: valid-skill\ndescription: Something.\n---\n")
        self.assertTrue(any("body" in error for error in errors))

    def test_broken_supporting_file_link_fails(self) -> None:
        content = VALID_SKILL.replace("A result.", "See [template](assets/missing.tmpl).")
        errors = self.errors_for(content)
        self.assertTrue(any("does not exist" in error for error in errors))

    def test_existing_supporting_file_link_passes(self) -> None:
        (self.skill_directory / "assets").mkdir()
        (self.skill_directory / "assets" / "note.tmpl").write_text("x\n", encoding="utf-8")
        content = VALID_SKILL.replace("A result.", "See [template](assets/note.tmpl).")
        self.assertEqual(self.errors_for(content), [])

    def test_missing_brain_citation_fails(self) -> None:
        content = VALID_SKILL.replace(
            " Background: [Target note](../../../brain/resources/Target.md).", ""
        )
        errors = self.errors_for(content)
        self.assertTrue(any("SB-03" in error for error in errors))

    def test_repository_skill_is_discovered_and_valid(self) -> None:
        files, errors = validate_skills(REPOSITORY_ROOT, ["brain-ingest"])
        self.assertIn("brain-ingest", [path.parent.name for path in files])
        self.assertEqual(errors, [])


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

    def errors_for_metadata(self, old: str, new: str) -> list[str]:
        self.write_note("resources/Research.md", VALID_NOTE.replace(old, new))
        return validate_brain(self.root)[2]

    def copy_srs(self) -> None:
        (self.root / "docs").mkdir(exist_ok=True)
        shutil.copy(REPOSITORY_ROOT / "docs" / "srs.md", self.root / "docs" / "srs.md")

    def test_valid_research_note_passes(self) -> None:
        self.write_note("resources/Research.md", VALID_NOTE)
        self.assertEqual(validate_brain(self.root), (1, 0, []))

    def test_missing_required_metadata_fails(self) -> None:
        self.write_note(
            "resources/Research.md",
            "---\ntitle: Research note\n---\nBody.\n",
        )
        _, _, errors = validate_brain(self.root)
        for field in ("type", "author", "created", "tags", "sources"):
            self.assertTrue(any(f"required field '{field}'" in error for error in errors), field)

    def test_malformed_yaml_fails(self) -> None:
        self.write_note("resources/Research.md", "---\ntitle: [\n---\nBody.\n")
        _, _, errors = validate_brain(self.root)
        self.assertTrue(any("invalid YAML" in error for error in errors))

    def test_unknown_field_fails(self) -> None:
        errors = self.errors_for_metadata("type: research\n", "type: research\nsource: x\n")
        self.assertTrue(any("field 'source' is not part of the note schema" in e for e in errors))

    def test_sources_as_single_string_fails(self) -> None:
        errors = self.errors_for_metadata(
            "sources:\n  - https://example.test/source\n", "sources: https://example.test/source\n"
        )
        self.assertTrue(any("'sources' must be a non-empty list" in e for e in errors))

    def test_empty_sources_list_fails(self) -> None:
        errors = self.errors_for_metadata(
            "sources:\n  - https://example.test/source\n", "sources: []\n"
        )
        self.assertTrue(any("'sources' must be a non-empty list" in e for e in errors))

    def test_source_that_is_neither_url_nor_existing_path_fails(self) -> None:
        errors = self.errors_for_metadata("https://example.test/source", "docs/missing.md")
        self.assertTrue(any("does not exist" in e for e in errors))
        errors = self.errors_for_metadata("https://example.test/source", "ftp://example.test/x")
        self.assertTrue(any("http(s) URL" in e for e in errors))

    def test_existing_repository_path_source_passes(self) -> None:
        (self.root / "AGENTS.md").write_text("Agents.\n", encoding="utf-8")
        self.assertEqual(self.errors_for_metadata("https://example.test/source", "AGENTS.md"), [])

    def test_author_must_be_a_list_without_email_addresses(self) -> None:
        errors = self.errors_for_metadata("author:\n  - Person 1\n", "author: Person 1\n")
        self.assertTrue(any("'author' must be a non-empty list" in e for e in errors))
        errors = self.errors_for_metadata("- Person 1", "- someone@example.test")
        self.assertTrue(any("not email addresses" in e for e in errors))

    def test_created_must_be_an_iso_date(self) -> None:
        for value in ("07/11/2026", '"2026-13-01"', "2026-11-07T10:00:00"):
            with self.subTest(value=value):
                errors = self.errors_for_metadata("created: 2026-11-07", f"created: {value}")
                self.assertTrue(any("'created' must be a date" in e for e in errors))
        self.assertEqual(self.errors_for_metadata("2026-11-07", '"2026-11-07"'), [])

    def test_impossible_unquoted_date_is_reported_not_raised(self) -> None:
        # Regression: PyYAML raises ValueError (not YAMLError) for 2026-13-01, which previously
        # crashed scripts/frontmatter.py instead of producing a validation error.
        errors = self.errors_for_metadata("created: 2026-11-07", "created: 2026-13-01")
        self.assertTrue(any("invalid YAML frontmatter" in e for e in errors))

    def test_type_and_status_values_are_restricted(self) -> None:
        errors = self.errors_for_metadata("type: research", "type: stage-review")
        self.assertTrue(any("'type' must be one of" in e for e in errors))
        errors = self.errors_for_metadata("type: research\n", "type: research\nstatus: done\n")
        self.assertTrue(any("'status' must be one of" in e for e in errors))
        valid = "type: research\nstatus: draft\naliases:\n  - Alias\n"
        self.assertEqual(self.errors_for_metadata("type: research\n", valid), [])

    def test_ai_session_note_passes(self) -> None:
        self.assertEqual(self.errors_for_metadata("type: research", "type: ai-session"), [])

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
        self.assertTrue(any("broken wikilink '[[Missing Note]]'" in error for error in errors))

    def test_alias_wikilink_passes(self) -> None:
        self.write_note("resources/Target.md", VALID_NOTE)
        source = VALID_NOTE.replace("Note body.", "See [[Target|display name]].")
        self.write_note("projects/Source.md", source)
        _, _, errors = validate_brain(self.root)
        self.assertEqual(errors, [])

    def test_frontmatter_alias_is_not_a_link_target(self) -> None:
        target = VALID_NOTE.replace("type: research\n", "type: research\naliases:\n  - Nice Name\n")
        self.write_note("resources/Target.md", target)
        self.write_note(
            "projects/Source.md", VALID_NOTE.replace("Note body.", "See [[Nice Name]].")
        )
        _, _, errors = validate_brain(self.root)
        self.assertTrue(any("broken wikilink '[[Nice Name]]'" in error for error in errors))

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

    def test_wikilinks_in_code_are_literal_text(self) -> None:
        body = "Quoted: `[[Old Name]]`.\n\n```markdown\n[[Example Note]]\n```\n"
        self.write_note("log.md", body)
        note_count, link_count, errors = validate_brain(self.root)
        self.assertEqual((link_count, errors), (0, []))

    def test_heading_links_are_checked(self) -> None:
        self.write_note("resources/Target.md", VALID_NOTE + "\n## Key Concepts\n")
        self.write_note("log.md", "[[Target#Key Concepts]] and [[Target#Missing Heading]]\n")
        _, _, errors = validate_brain(self.root)
        self.assertEqual(len(errors), 1)
        self.assertIn("heading that does not exist", errors[0])

    def test_relative_markdown_links_must_resolve(self) -> None:
        self.write_note("log.md", "[SRS](../docs/srs.md)\n")
        _, _, errors = validate_brain(self.root)
        self.assertTrue(any("does not exist" in error for error in errors))
        self.copy_srs()
        self.assertEqual(validate_brain(self.root)[2], [])

    def test_requirement_ids_must_be_canonical_and_defined(self) -> None:
        self.copy_srs()
        self.write_note("log.md", "Uses FR-1, `FR-01`, `NFR-02.1` and `FR-99`. Quoted: `FR-2`.\n")
        _, _, errors = validate_brain(self.root)
        self.assertEqual(len(errors), 2, errors)
        self.assertTrue(any("'FR-1' is not in canonical" in error for error in errors))
        self.assertTrue(any("'FR-99' is not defined" in error for error in errors))

    def test_requirement_ids_without_srs_are_reported(self) -> None:
        self.write_note("log.md", "See `FR-01`.\n")
        _, _, errors = validate_brain(self.root)
        self.assertTrue(any("cannot be checked" in error for error in errors))

    def test_brain_ingest_template_produces_a_valid_note(self) -> None:
        self.copy_srs()
        self.write_note("resources/Existing-Note.md", VALID_NOTE)
        template = BRAIN_INGEST_TEMPLATE.read_text(encoding="utf-8")
        filled = (
            template.replace("{{title}}", "Example research topic")
            .replace("{{author}}", "Person 2")
            .replace("{{created}}", datetime.date(2026, 11, 8).isoformat())
            .replace("{{source_url}}", "https://example.test/official-source")
            .replace("{{related_note}}", "Existing-Note")
        )
        self.assertNotIn("{{", filled)
        self.write_note("resources/Example-Research-Topic.md", filled)
        self.assertEqual(validate_brain(self.root)[2], [])

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
