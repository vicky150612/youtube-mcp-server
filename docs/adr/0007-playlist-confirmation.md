# ADR 0007: Two-phase playlist confirmation

- **Status:** Proposed
- **Date:** 2026-11-08
- **Decision owners:** Person 3 (MCP server, playlist planner/creator and `video-to-playlist`,
  per `docs/development-plan.md`)
- **Approval record:** The approach (design, requirements and negative test specification now;
  executable tests after `OD-01`) was approved in principle by the requesting maintainer (Git
  user `ChadDadChag`) on 2026-11-08. The design itself is pending team review through a pull
  request. Open parameters are tracked as `OD-16`.
- **Related requirements:** `FR-05`, `AC-05.3`…`AC-05.14`, `NFR-04.2`, `NFR-04.3` (proposed),
  `NFR-06.1`, `NFR-02.2`, `SK-05`, `TQ-03`, `TQ-04`; Stage 1 audit issue C6
- **Relevant Brain notes:**
  [MCP Tools and Resources](../../brain/resources/MCP-Tools-and-Resources.md),
  [MCP Architecture](../../brain/resources/MCP-Architecture.md),
  [YouTube Playlist Resource](../../brain/resources/YouTube-Playlist-Resource.md)

## Context

`FR-05` requires explicit user confirmation before a playlist is created. MCP tools are
**model-controlled**: the model chooses when to call a tool and with which arguments. A tool
argument such as `confirmed=true`, or a second tool call issued by the model, is model output
and is not evidence that the user approved anything. Video titles, descriptions and tags are
untrusted and may contain instructions (`NFR-04.2`).

MCP specification `2026-07-28` (verified 2026-11-08 at
<https://modelcontextprotocol.io/specification/2026-07-28/client/elicitation>) provides
**elicitation**: while processing a request such as `tools/call`, a server returns an
`InputRequiredResult` containing an `elicitation/create` request, and the client retries the
call with the user's response. Relevant rules:

- Clients that support it **MUST** declare the `elicitation` capability (modes `form` and/or
  `url`) on each request; servers **MUST NOT** use a mode the client did not declare.
- Clients **MUST** make clear which server is asking, provide clear decline and cancel options
  and, for form mode, let the user review responses before sending.
- Responses are `accept`, `decline` (explicit refusal) or `cancel` (dismissed without a choice).
- In **URL mode** the user opens a server-provided URL; the interaction happens out of band and
  does not pass through the client or the model. Servers must verify that the user completing
  the URL interaction is the user who started it.
- The protocol does not mandate a specific user-interface pattern, and servers must handle
  decline, cancel and client failure.

## Decision

### Phase 1: propose (no writes)

Tool `propose_playlist` (name indicative; the tool list is frozen with the interface contracts):

1. Parse the natural-language request into `PlaylistConstraints` and validate them.
2. Run the quota pre-check for the read workflow, find candidates and select videos.
3. Validate the result against every constraint.
4. Store a **proposal record** server-side: a random, unguessable `proposal_id` (at least 128
   bits); the canonical, immutable content (ordered video IDs with durations, title,
   description, privacy status, parsed constraints, total duration, constraint-check results);
   a SHA-256 **digest** of that canonical content; the authorised account it belongs to;
   `created_at` and `expires_at`; the estimated write cost; and `state = proposed`.
5. Return the full proposal for display, the `proposal_id` and a short fingerprint of the
   digest. The tool performs **no** YouTube write calls.

### Phase 2: confirm and create

Tool `create_playlist_from_proposal(proposal_id)` is the only path to `playlists.insert` and
`playlistItems.insert`. It accepts **only** a proposal ID: no content and no `confirmed` flag.

1. Reject unless the record exists, belongs to the current authorised account, is in state
   `proposed`, has not expired, and its stored content still matches its digest.
2. Run the quota pre-check for the write workflow (`playlists.insert` plus one
   `playlistItems.insert` per video) before asking the user, so the user is not asked to
   approve something that cannot run.
3. If the request does not declare the `elicitation` capability, **fail closed** with a typed
   `confirmation_unavailable` error (see Fallback). Nothing is created and the proposal is not
   consumed.
4. Otherwise obtain **user-mediated confirmation** through elicitation:
   - **Preferred: URL mode.** The server serves a confirmation page (for the local `stdio`
     deployment, on a loopback address with a single-use nonce) that shows the full proposal
     and its fingerprint with Confirm and Decline buttons. The user's choice reaches the server
     directly, outside the client and the model.
   - **Otherwise: form mode.** The elicitation message shows the full proposal and fingerprint;
     the schema asks the user to type the fingerprint and choose confirm or reject, with no
     default values, so a default-accepting client cannot submit consent unintentionally.
5. `accept` (and, in URL mode, a recorded confirmation from the page for this nonce) moves the
   record atomically from `proposed` to `creating` under a per-proposal lock. Only one request
   can win; concurrent or repeated calls are rejected or receive the stored outcome.
   `decline` moves it to `cancelled` (terminal). `cancel` leaves it `proposed` so the user can
   be asked again until it expires.
6. Create the playlist, store its ID on the record immediately, then add items. A retry of the
   same proposal resumes adding missing items to the stored playlist and never creates a
   second playlist (**idempotency**). On partial failure the record becomes
   `partially_created` and the result reports exactly which videos were and were not added
   (`AC-05.8`).
7. On success the record becomes `created` (terminal) and the result returns the playlist ID,
   URL and a summary. Replaying the call returns the stored result.

### Changes, cancellation and expiry

- A proposal is immutable. Any change (swapping a video, changing the title) is a new
  `propose_playlist` call with a new ID; the old proposal becomes `superseded`.
- Tool `cancel_playlist_proposal(proposal_id)` marks a proposal `cancelled`.
- Proposals expire after a fixed period (proposed default 15 minutes, `OD-16`); expired
  proposals cannot be confirmed.
- `youtubeSignupRequired` (account without a channel) and expired credentials are reported as
  typed errors; no partial state is created (`NFR-06.1`, `NFR-03.3`).

### Fallback for clients without trustworthy confirmation

The server never creates a playlist without elicitation. When elicitation is unavailable it
returns the proposal with a typed `confirmation_unavailable` error and an export (title and
ordered video URLs) so the user can create the playlist manually in YouTube. A separate
out-of-band confirmation channel for such clients (for example a command the user runs in a
terminal) is possible but is **not** part of this decision; it would need its own review.

## Alternatives considered

- **`confirmed=true` argument or a second model-issued call.** Model output, not consent;
  trivially triggered by prompt injection. Rejected.
- **Trust the host's generic tool-approval dialog.** Not guaranteed by the protocol, not
  visible to the server, and approves a call rather than a specific proposal. Rejected as the
  sole mechanism.
- **Form mode only.** Simpler, but the response passes through the client. Kept as the
  secondary path; URL mode preferred.
- **Auto-create for clients without elicitation.** Violates `FR-05`. Rejected.

## Consequences

- The server keeps short-lived proposal state, bound to the authorised account. MCP
  `2026-07-28` allows this but requires the state to be protected and bound to the user.
- **Residual risk:** a server cannot cryptographically prove that a human, rather than a
  non-conforming client, answered an elicitation. URL mode limits this to the user's browser;
  form mode relies on the client meeting its MCP obligations. The demo client (`OD-02`) must be
  checked for elicitation support before Stage 4.
- The negative test specification lives in `docs/testing/README.md`. Executable tests are
  written once `OD-01` is decided and the playlist module exists; until then no test is
  claimed to pass.
