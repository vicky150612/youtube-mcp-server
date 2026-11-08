# GitHub development workflow

## Issue to merge

1. Create a GitHub issue for each task or defect. Record the relevant requirement IDs and
   acceptance criteria. Do not put credentials or personal data in issues.
2. Branch from the current `main` using an issue-linked name, for example
   `feature/123-video-search`, `fix/123-invalid-duration`, `docs/123-srs-traceability`, or
   `ci/123-required-checks`. Use the real issue number.
3. Keep the change focused. Add/update tests and documentation; Brain and skill changes
   also require a PR.
4. Open a PR to `main`, reference the issue (for example `Closes #123`), and complete the
   existing [PR template](../../.github/PULL_REQUEST_TEMPLATE.md).
5. Obtain at least one approval from someone other than the author. Resolve review threads
   and confirm all required CI checks pass.
6. Merge only after approval and required checks pass. Do not make development commits
   directly to `main`, force-push to it, or bypass the review/check policy.

Do not invent an issue or PR identifier when work has not been filed. Keep issue, PR, test,
skill-evaluation, and Brain-note references in the
[traceability matrix](../traceability.md).

## Branch naming

`main` is the stable integration branch. Use the existing prefixes:

- `feature/*` for functionality.
- `fix/*` for defects.
- `docs/*` for documentation and Brain/skill work.
- `test/*` for test-only work.
- `ci/*` for CI and repository infrastructure.

Use the branch as a working area, not as a substitute for an issue or PR.

## Primary reviewers

| Author   | Primary reviewer |
| -------- | ---------------- |
| Person 1 | Person 2         |
| Person 2 | Person 3         |
| Person 3 | Person 1         |

The repository ruleset also requires one approval. Arrange a different qualified reviewer
if the listed reviewer is unavailable; the author is not their own approver.

## Main branch protection

As checked on 2026-11-07, GitHub has an active repository ruleset, **Protect main**, targeting
the default branch. It requires a pull request and one approval, and blocks branch deletion
and non-fast-forward updates. The ruleset currently has **no required status checks**, does
not require the branch to be up to date, and has a configured bypass actor. A separate
branch-protection endpoint returned 404 because this repository uses a ruleset. Therefore,
CI checks are not yet enforced for merge. The 2026-11-08 audit could not re-check the ruleset
because no authenticated GitHub access was available; the state above may have changed.

Repository maintainers should review **Settings → Rules → Rulesets → Protect main** and:

1. Add the seven CI job checks after they have appeared at least once on GitHub and are
   consistently green: `Build`, `Lint`, `Automated tests`, `Secret scanning`,
   `Skill validation`, `Brain validation` and `Documentation validation`.
   Select the actual displayed check-run contexts if GitHub prefixes them with the workflow
   name.
2. Enable required status checks and, where appropriate, require the branch to be up to
   date before merge.
3. Keep pull requests and at least one approval required; prevent force pushes and deletion
   of `main`.
4. Review the configured bypass actor and restrict bypass to an explicitly approved
   emergency/admin process; routine development must use PRs and checks.
5. Save the ruleset and verify its active state and rules in GitHub settings/API.

The workflow file alone does not configure branch protection. No claim is made that CI
checks are required until the ruleset is updated and verified.

## Release and changelog

1. Update `CHANGELOG.md` with the actual user-visible changes and release date/version.
2. Run the required local checks, review the final diff, and merge the release PR after
   approval and all required CI checks pass.
3. Create and push a version tag using the team's agreed version scheme (for example,
   `vX.Y.Z`) only after the release commit is merged and verified.
4. Record the tag, release notes, and verification evidence. Do not tag unfinished or
   unverified work. No release tag is created by this workflow documentation.
