# ADR 0006: Quota reference, accounting model and search capacity

- **Status:** Proposed
- **Date:** 2026-11-08
- **Decision owners:** Person 1 (YouTube provider and quota module, per
  `docs/development-plan.md`); Person 3 authored the quota research note
- **Approval record:** Pending team review through a pull request.
- **Related requirements:** `NFR-02.1`, `NFR-02.2`, `NFR-02.3` (proposed), `NFR-08.3`,
  `NFR-08.4` (proposed), `TQ-05`, `TQ-06`, `OD-09`, `OD-11`, `OD-13`; Stage 1 audit issues
  D-2, F-2, F-3, F-7, N-1
- **Relevant Brain notes:**
  [YouTube API Quota Management](../../brain/resources/YouTube-API-Quota-Management.md),
  [YouTube Data API](../../brain/resources/YouTube-Data-API.md)

## Context

The same quota figures were repeated in four places (SRS Appendix A, two API overview notes
and the quota note). The SRS labelled the separate `search.list` bucket `[DERIVED]` although
it is a fact from Google's documentation, and the original brief that states the 10,000-unit
default could not be compared because the brief PDFs are not in the repository. `AGENTS.md`
and the testing README contained rules stricter than the SRS (fail closed on unknown costs,
finite live-test caps, zero budget disables calls). The design also implied that the system
knows its remaining quota, which the API does not report.

Verified on 2026-11-08 against Google's pages
(<https://developers.google.com/youtube/v3/determine_quota_cost>,
<https://developers.google.com/youtube/v3/getting-started>,
<https://developers.google.com/youtube/v3/revision_history>):

- The default allocation is a general daily unit pool plus separate daily call buckets for
  `search.list` and `videos.insert`; the verified figures are recorded once, in
  [SRS Appendix A](../srs.md#appendix-a--reference-youtube-api-quota) (Decision 1).
- The revision history entry dated **June 1, 2026** states that `videos.insert` and
  `search.list` "will be charged to their own respective quota buckets".
- Every request, including invalid ones, costs at least one point; each additional page is
  charged again; daily quotas reset at midnight Pacific Time.
- The getting-started page directs users to the Cloud Console Quotas page to see usage; no
  YouTube Data API method for reading remaining quota is documented there.

## Decision

1. **One numeric reference.** SRS Appendix A is the canonical table of quota figures used by
   requirements, design and tests. The quota research note keeps the figures as its record of
   what was verified and when; all other documents (including the merged API overview note
   and the architecture overview) link to Appendix A instead of restating the table.
2. **Classification (F-7).** The 10,000-unit default remains a brief requirement
   (`[BRIEF-P]`). The separate `search.list`/`videos.insert` buckets are tagged `[EXTERNAL]`, a
   new SRS source tag for facts verified in official external documentation. This is an
   additional external constraint introduced by Google on 2026-06-01, not a replacement of the
   brief's requirement. Whether the brief mentions search costs cannot be checked until the
   brief PDFs are available.
3. **Accounting model (F-2).** Quota is tracked by a **local ledger of estimates**, per
   Pacific-Time day and per bucket. The ledger is not authoritative and must never be presented
   as a Google-provided remaining value. It is conservative: every attempted call is charged at
   its documented cost, including failed and invalid calls and every page. A `quotaExceeded`
   response is authoritative and sets the affected bucket to exhausted until the next reset.
   Drift sources are documented: other processes, users or live tests sharing the Cloud
   project, usage outside this server, and retries.
4. **Proposed SRS requirements (N-1).** `NFR-02.3`: a workflow whose operation cost is unknown
   is rejected before any API call (fail closed). `NFR-08.4`: live API tests require finite
   per-run caps for every applicable bucket; a missing cap fails closed and a zero cap disables
   calls. Both are tagged `[PROPOSED]` in the SRS until the team approves them; `AGENTS.md` and
   the testing README cite these IDs instead of stating independent rules.
5. **Search capacity (F-3).** With the daily `search.list` limit in SRS Appendix A and the `OD-09`
   proposal of at most 2 search calls per tool invocation, the project can serve **at most 50
   search-dependent tool invocations per day**, shared by every user, process and live test of
   the same Cloud project, and fewer if any invocation uses more searches or pages. The SRS
   therefore states that similarity, recommendation and playlist features are bounded by this
   budget, that candidate discovery prefers general-pool reads (channel uploads via
   `playlistItems.list`, batched `videos.list`, subscriptions) and caching, and that an
   exhausted search bucket produces a clear typed error rather than degraded silent results.

## Alternatives considered

- **Keep figures in every note.** Four copies had to be kept in sync by hand. Rejected.
- **Make the quota research note canonical.** Requirements should not depend on a lower-
  precedence Brain note. Rejected.
- **Query remaining quota from Google at run time.** No YouTube Data API method for this is
  documented; Cloud Monitoring metrics would add a new external dependency and credentials.
  Rejected (would also need an ADR under `AGENTS.md` §6).
- **Treat the search bucket as a change to the brief.** The brief's 10,000-unit statement is
  still true for general endpoints. Rejected.

## Consequences

- Product features cannot promise unlimited similarity searches or recommendations.
- The quota estimator needs a persisted, per-day ledger and a cost table that includes the
  search bucket; unknown costs are a hard failure.
- Figures must be re-verified before implementation (Google states defaults may change) and
  only Appendix A and the research note are updated when they do.
