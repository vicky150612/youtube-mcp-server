"""Validate the repository's Agent Skills.

Skills live in .claude/skills/<skill-name>/SKILL.md (docs/adr/0001-agent-skill-location.md).
Frontmatter rules follow the Agent Skills specification; the required body sections and the
Brain-note citation are project rules from AGENTS.md section 12 and SRS SB-03.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

if __package__:
    from .frontmatter import load_frontmatter
    from .markdown_links import check_relative_link, line_number, markdown_links
else:
    from frontmatter import load_frontmatter
    from markdown_links import check_relative_link, line_number, markdown_links

SKILL_NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIRECTORY = Path(".claude") / "skills"
SKILL_FILE = "SKILL.md"
# Each required section is satisfied by a level-2 heading containing one of the keywords.
REQUIRED_SECTIONS = {
    "purpose": ("purpose",),
    "inputs": ("input",),
    "workflow": ("workflow",),
    "outputs": ("output", "outcome"),
    "limitations": ("limitation",),
}
LEVEL_TWO_HEADING = re.compile(r"^##[ \t]+(.+?)[ \t]*#*[ \t]*$", re.MULTILINE)


def _body(path: Path) -> str:
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    closing = next(
        (index for index in range(1, len(lines)) if lines[index].strip() in {"---", "..."}), None
    )
    return "\n".join(lines[closing + 1 :]) if closing is not None else ""


def _frontmatter_errors(path: Path, display: str, metadata: dict[str, object]) -> list[str]:
    errors: list[str] = []
    name = metadata.get("name")
    if not isinstance(name, str) or not name:
        errors.append(f"{display}: required field 'name' must be a non-empty string")
    else:
        if len(name) > 64 or SKILL_NAME.fullmatch(name) is None:
            errors.append(
                f"{display}: field 'name' must be 1-64 lowercase letters, numbers, "
                "or single hyphen-separated segments"
            )
        if name != path.parent.name:
            errors.append(
                f"{display}: field 'name' must match containing directory '{path.parent.name}'"
            )

    description = metadata.get("description")
    if not isinstance(description, str) or not description.strip():
        errors.append(f"{display}: required field 'description' must be a non-empty string")
    elif len(description) > 1024:
        errors.append(f"{display}: field 'description' must not exceed 1024 characters")

    compatibility = metadata.get("compatibility")
    if compatibility is not None and (
        not isinstance(compatibility, str) or not 1 <= len(compatibility) <= 500
    ):
        errors.append(f"{display}: field 'compatibility' must be a string of 1-500 characters")

    license_name = metadata.get("license")
    if license_name is not None and (not isinstance(license_name, str) or not license_name.strip()):
        errors.append(f"{display}: field 'license' must be a non-empty string")

    extra_metadata = metadata.get("metadata")
    if extra_metadata is not None and (
        not isinstance(extra_metadata, dict)
        or any(
            not isinstance(key, str) or not isinstance(value, str)
            for key, value in extra_metadata.items()
        )
    ):
        errors.append(f"{display}: field 'metadata' must be a mapping of strings to strings")

    allowed_tools = metadata.get("allowed-tools")
    if allowed_tools is not None and not isinstance(allowed_tools, str):
        errors.append(f"{display}: field 'allowed-tools' must be a string")
    return errors


def validate_skill(path: Path, root: Path | None = None) -> list[str]:
    """Validate one SKILL.md. ``root`` is the repository root used to resolve links."""
    root = (root or REPOSITORY_ROOT).resolve()
    try:
        display = path.resolve().relative_to(root).as_posix()
    except ValueError:
        display = str(path)
    metadata, frontmatter_error = load_frontmatter(path)
    if frontmatter_error is not None:
        return [f"{display}: {frontmatter_error}"]
    if metadata is None:
        return [f"{display}: YAML frontmatter must be a mapping"]

    errors = _frontmatter_errors(path, display, metadata)

    body = _body(path)
    if not body.strip():
        errors.append(f"{display}: the skill body (instructions after the frontmatter) is empty")
        return errors

    section_titles = [title.casefold() for title in LEVEL_TWO_HEADING.findall(body)]
    for section, keywords in REQUIRED_SECTIONS.items():
        if not any(keyword in title for title in section_titles for keyword in keywords):
            errors.append(
                f"{display}: missing required '## ...' section for {section} "
                f"(heading containing: {', '.join(keywords)}; AGENTS.md section 12)"
            )

    text = path.read_text(encoding="utf-8-sig")
    cites_brain_note = False
    brain_directory = (root / "brain").resolve()
    for offset, target in markdown_links(text):
        problem = check_relative_link(path, target, root)
        if problem:
            errors.append(f"{display}:{line_number(text, offset)}: {problem}")
            continue
        path_part = target.partition("#")[0]
        if path_part and "://" not in target:
            resolved = (path.parent / path_part).resolve()
            if resolved.suffix == ".md" and brain_directory in resolved.parents:
                cites_brain_note = True
    if not cites_brain_note:
        errors.append(
            f"{display}: must cite at least one distilled Brain note with a relative link "
            "into brain/ (SB-03)"
        )
    return errors


def validate_skills(
    root: Path, required: tuple[str, ...] | list[str] = ()
) -> tuple[list[Path], list[str]]:
    skills_directory = root / SKILLS_DIRECTORY
    display_directory = SKILLS_DIRECTORY.as_posix()
    if not skills_directory.is_dir():
        return [], [f"{display_directory}: skill directory does not exist (ADR 0001)"]

    errors: list[str] = []
    skill_files: list[Path] = []
    for entry in sorted(skills_directory.iterdir()):
        relative = f"{display_directory}/{entry.name}"
        if not entry.is_dir():
            errors.append(f"{relative}: unexpected file; each skill must be a directory")
            continue
        names = {child.name for child in entry.iterdir()}
        if SKILL_FILE not in names:
            wrong_case = sorted(name for name in names if name.casefold() == SKILL_FILE.casefold())
            hint = f" (found '{wrong_case[0]}'; the name is case-sensitive)" if wrong_case else ""
            errors.append(f"{relative}: missing {SKILL_FILE}{hint}")
            continue
        skill_files.append(entry / SKILL_FILE)

    if not skill_files and not errors:
        errors.append(f"{display_directory}: no Agent Skills found")

    present = {path.parent.name for path in skill_files}
    for name in required:
        if name not in present:
            errors.append(f"{display_directory}/{name}: required skill '{name}' is missing")

    errors.extend(error for path in skill_files for error in validate_skill(path, root))
    return skill_files, errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=REPOSITORY_ROOT,
        help="repository root (defaults to the repository containing this script)",
    )
    parser.add_argument(
        "--require",
        action="append",
        default=[],
        metavar="NAME",
        help="name of a skill that must exist (repeatable)",
    )
    arguments = parser.parse_args(argv)

    skill_files, errors = validate_skills(arguments.root.resolve(), arguments.require)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        print(f"Skill validation failed: {len(errors)} error(s).", file=sys.stderr)
        return 1

    names = ", ".join(path.parent.name for path in skill_files)
    print(f"Skill validation passed: {len(skill_files)} SKILL.md file(s) validated ({names}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
