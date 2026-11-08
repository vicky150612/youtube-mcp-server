"""Check that credential files are ignored and that none are tracked (I-13, NFR-05.1)."""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]

# Synthetic file names only; these files are never created.
CREDENTIAL_PATHS = (
    ".env",
    ".env.local",
    ".env.production",
    "config/.env",
    "client_secret.json",
    "client_secret_1234-example.apps.googleusercontent.com.json",
    "credentials.json",
    "credentials-oauth.json",
    "service-account.json",
    "service-account-ci.json",
    "token.json",
    "token-youtube.json",
    "certs/private.pem",
    "keystore.p12",
    "signing.key",
)

FILES_THAT_MUST_STAY_TRACKABLE = (
    ".env.example",
    "README.md",
    "docs/srs.md",
    "scripts/ci_build.py",
    "tests/test_repository_hygiene.py",
)


def _git(*arguments: str, stdin: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *arguments],
        cwd=REPOSITORY_ROOT,
        input=stdin,
        capture_output=True,
        text=True,
        check=False,
    )


def _ignored(paths: tuple[str, ...] | list[str]) -> set[str]:
    """Return the subset of paths matched by the repository's ignore rules.

    ``--no-index`` evaluates the rules even for paths that are already tracked.
    NUL-separated input/output (``-z``) avoids path quoting and the newline
    translation that text-mode pipes perform on Windows.
    """
    result = _git("check-ignore", "--no-index", "-z", "--stdin", stdin="\0".join(paths) + "\0")
    # Exit status 0 means at least one match, 1 means no match; anything else is an error.
    if result.returncode not in (0, 1):
        raise AssertionError(f"git check-ignore failed: {result.stderr.strip()}")
    return {path for path in result.stdout.split("\0") if path}


class CredentialIgnoreRulesTests(unittest.TestCase):
    def test_credential_files_are_ignored(self) -> None:
        not_ignored = sorted(set(CREDENTIAL_PATHS) - _ignored(CREDENTIAL_PATHS))
        self.assertEqual(not_ignored, [], f"credential paths not ignored: {not_ignored}")

    def test_safe_files_are_not_ignored(self) -> None:
        wrongly_ignored = sorted(_ignored(FILES_THAT_MUST_STAY_TRACKABLE))
        self.assertEqual(wrongly_ignored, [], f"paths wrongly ignored: {wrongly_ignored}")

    def test_obsidian_workspace_configuration_is_ignored(self) -> None:
        paths = (".obsidian/workspace.json", "brain/.obsidian/app.json")
        self.assertEqual(sorted(_ignored(paths)), sorted(paths))

    def test_no_tracked_file_matches_an_ignore_rule(self) -> None:
        listing = _git("ls-files", "-z")
        self.assertEqual(listing.returncode, 0, listing.stderr)
        tracked = [path for path in listing.stdout.split("\0") if path]
        self.assertTrue(tracked, "git ls-files returned no tracked files")
        matched = sorted(_ignored(tracked))
        self.assertEqual(matched, [], f"tracked files match ignore rules: {matched}")


if __name__ == "__main__":
    unittest.main()
