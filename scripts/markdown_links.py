"""Shared Markdown link, heading and requirement-ID helpers for repository validators.

Conventions are defined in docs/adr/0003-linking-naming-and-requirement-references.md.
"""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote

FENCE = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,})")
# An inline code span may wrap lines but, as in CommonMark, never crosses a blank line; otherwise
# a stray backtick would hide everything up to the next backtick from validation.
INLINE_CODE = re.compile(r"(`+)((?:(?!\n[ \t]*\n).)+?)\1", re.DOTALL)
WIKILINK = re.compile(r"\[\[([^\]\n]+)\]\]")
# [text](target) or ![alt](target), with an optional "title". Targets with spaces must be
# written as <target>.
MARKDOWN_LINK = re.compile(
    r"!?\[(?:[^\]\n]|\][^(\n])*?\]\(\s*(<[^>\n]+>|[^)\s]+)(?:\s+\"[^\"\n]*\")?\s*\)"
)
HEADING = re.compile(r"^[ \t]{0,3}(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*$")
URL_SCHEME = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")

REQUIREMENT_PREFIXES = "FR|NFR|SK|TQ|SE|SB|AIP|OD"
CANONICAL_ID = re.compile(rf"\b(?:(?:{REQUIREMENT_PREFIXES})-\d{{2}}(?:\.\d+)?|AC-\d{{2}}\.\d+)\b")
UNPADDED_ID = re.compile(rf"\b(?:{REQUIREMENT_PREFIXES})-\d(?![\d])(?:\.\d+)?\b")
DEFINITION_PATTERNS = (
    # Table row whose first cell is the ID, optionally bold: | NFR-02.1 | ... or | **NFR-01** |
    re.compile(rf"^\|\s*\**((?:{REQUIREMENT_PREFIXES})-\d{{2}}(?:\.\d+)?)\**\s*\|", re.MULTILINE),
    # Heading that starts with the ID: ### FR-01 — Similar Videos
    re.compile(rf"^#{{2,6}}\s+((?:{REQUIREMENT_PREFIXES})-\d{{2}}(?:\.\d+)?)\b", re.MULTILINE),
    # Acceptance criterion bullet: - AC-01.1 ...
    re.compile(r"^\s*[-*]\s+(AC-\d{2}\.\d+)\b", re.MULTILINE),
)


def mask_code(text: str) -> str:
    """Return text with fenced code blocks and inline code replaced by spaces.

    Newlines and character offsets are preserved so that line numbers stay correct.
    """
    lines = text.split("\n")
    masked: list[str] = []
    fence: str | None = None
    for line in lines:
        match = FENCE.match(line)
        if fence is None and match:
            fence = match.group(1)[0] * 3
            masked.append(" " * len(line))
            continue
        if fence is not None:
            if match and match.group(1).startswith(fence):
                fence = None
            masked.append(" " * len(line))
            continue
        masked.append(line)
    without_fences = "\n".join(masked)
    return INLINE_CODE.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), without_fences)


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def github_anchor(heading: str) -> str:
    """Approximate GitHub's heading anchor: lowercase, drop punctuation, spaces to hyphens."""
    text = re.sub(r"`([^`]*)`", r"\1", heading)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = text.strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def headings(text: str) -> list[str]:
    """Return heading texts outside code blocks, in document order."""
    found: list[str] = []
    for line in mask_code(text).split("\n"):
        match = HEADING.match(line)
        if match:
            found.append(match.group(2).strip())
    return found


def heading_anchors(text: str) -> set[str]:
    """Return GitHub-style anchors, including -1, -2 suffixes for duplicate headings."""
    anchors: set[str] = set()
    counts: dict[str, int] = {}
    for heading in headings(text):
        base = github_anchor(heading)
        count = counts.get(base, 0)
        anchors.add(base if count == 0 else f"{base}-{count}")
        counts[base] = count + 1
    return anchors


def wikilinks(text: str) -> list[tuple[int, str]]:
    """Return (offset, inner text) for wikilinks outside code."""
    return [(match.start(), match.group(1)) for match in WIKILINK.finditer(mask_code(text))]


def markdown_links(text: str) -> list[tuple[int, str]]:
    """Return (offset, target) for Markdown links outside code."""
    links = []
    for match in MARKDOWN_LINK.finditer(mask_code(text)):
        target = match.group(1)
        if target.startswith("<") and target.endswith(">"):
            target = target[1:-1]
        links.append((match.start(), target.strip()))
    return links


def is_external(target: str) -> bool:
    return bool(URL_SCHEME.match(target)) or target.startswith("//")


def check_relative_link(source: Path, target: str, root: Path) -> str | None:
    """Return an error message if a relative Markdown link does not resolve, else None."""
    if is_external(target):
        return None
    path_part, _, anchor = target.partition("#")
    path_part = unquote(path_part)
    if path_part:
        resolved = (source.parent / path_part).resolve()
        try:
            resolved.relative_to(root.resolve())
        except ValueError:
            return f"link target '{target}' points outside the repository"
        if not resolved.exists():
            return f"link target '{target}' does not exist"
    else:
        resolved = source
    if anchor and resolved.is_file() and resolved.suffix.casefold() in {".md", ".markdown"}:
        anchors = heading_anchors(resolved.read_text(encoding="utf-8-sig"))
        if unquote(anchor).lower() not in anchors:
            return f"link target '{target}' has no heading matching '#{anchor}'"
    return None


def defined_requirement_ids(srs_text: str) -> set[str]:
    """Return requirement IDs defined in the SRS (table rows, headings, AC bullets)."""
    ids: set[str] = set()
    for pattern in DEFINITION_PATTERNS:
        ids.update(pattern.findall(srs_text))
    return ids


def requirement_id_errors(text: str, defined: set[str] | None) -> list[tuple[int, str]]:
    """Return (offset, message) for unpadded IDs (outside code) and undefined canonical IDs.

    ``defined`` is None when the SRS is unavailable; canonical IDs are then reported as
    uncheckable rather than silently accepted.
    """
    errors: list[tuple[int, str]] = []
    for match in UNPADDED_ID.finditer(mask_code(text)):
        errors.append(
            (
                match.start(),
                f"requirement ID '{match.group(0)}' is not in canonical zero-padded form",
            )
        )
    for match in CANONICAL_ID.finditer(text):
        identifier = match.group(0)
        if defined is None:
            errors.append(
                (match.start(), f"requirement ID '{identifier}' cannot be checked: SRS not found")
            )
        elif identifier not in defined:
            errors.append(
                (match.start(), f"requirement ID '{identifier}' is not defined in docs/srs.md")
            )
    return errors


def load_defined_requirement_ids(root: Path) -> set[str] | None:
    srs = root / "docs" / "srs.md"
    if not srs.is_file():
        return None
    return defined_requirement_ids(srs.read_text(encoding="utf-8-sig"))
