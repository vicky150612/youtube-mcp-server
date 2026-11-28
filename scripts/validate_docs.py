"""Validate existing Brain and skill metadata, wikilinks, and local doc links."""
from pathlib import Path
import re

import yaml

WIKILINK = re.compile(r"\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]")
LINK = re.compile(r"\]\(([^ )]+)\)")
REQUIRED = {"title", "created", "source", "requirements", "issues"}


def frontmatter(text):
    match = re.match(r"---\n(.*?)\n---(?:\n|$)", text, re.DOTALL)
    return yaml.safe_load(match[1]) if match else {}


def main():
    errors = []
    brain = Path("brain")
    paths = sorted(brain.rglob("*.md"))
    paths += sorted(Path("docs").rglob("*.md"))
    paths += [Path("README.md"), Path("AGENTS.md")]
    skills = sorted(Path("skills").glob("*/SKILL.md"))
    for file in paths + skills:
        text = file.read_text(encoding="utf-8-sig")
        data = frontmatter(text)
        if file in skills and (data.get("name") != file.parent.name
                               or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", file.parent.name)
                               or not data.get("description")):
            errors.append(f"{file}: invalid skill metadata")
        if file.is_relative_to(brain) and file.name != "note-template.md":
            if REQUIRED - data.keys() or not data.get("title") or not data.get("source"):
                errors.append(f"{file}: invalid Brain note metadata")
        for target in WIKILINK.findall(text):
            if target == "...":
                continue
            candidate = Path(target.removesuffix(".md") + ".md")
            if not candidate.is_file() and not (brain / candidate).is_file():
                matches = list(brain.rglob(candidate.name)) if len(candidate.parts) == 1 else []
                if len(matches) != 1:
                    errors.append(f"{file}: unresolved wikilink {target}")
        for target in LINK.findall(text):
            if "://" in target or target.startswith(("#", "mailto:")):
                continue
            if not (file.parent / target.split("#")[0]).exists():
                errors.append(f"{file}: broken local link {target}")
    if errors:
        print("\n".join(errors))
        return 1
    print("PASS Brain notes, skill frontmatter, and local documentation links.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
