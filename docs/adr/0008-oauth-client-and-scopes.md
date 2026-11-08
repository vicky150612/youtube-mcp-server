# ADR 0008: OAuth client type, scopes and token handling

- **Status:** Proposed
- **Date:** 2026-11-08
- **Decision owners:** Person 1 (authentication module, per `docs/development-plan.md`);
  Person 3 authored the OAuth research note
- **Approval record:** Pending team review through a pull request. Depends on the transport
  decision (`OD-15`) and resolves the recommendation part of `OD-08`.
- **Related requirements:** `NFR-03.1`, `NFR-03.2`, `NFR-03.3`, `NFR-05.1`, `FR-03`, `FR-04`,
  `FR-05`, `OD-08`, `OD-14`, `OD-15`; Stage 1 audit issue F-1
- **Relevant Brain notes:** [OAuth 2.0 Authentication](../../brain/resources/OAuth-Authentication.md),
  [MCP Architecture](../../brain/resources/MCP-Architecture.md)

## Context

The OAuth research note described Google's **web-server** flow (registered redirect URI,
confidential client secret held by a server). The MCP Architecture note records that a local
server uses the **stdio** transport and typically serves a single client, and that no
transport decision exists. A locally run stdio server is an installed application, for which
Google documents a different flow. Scopes and token storage were undecided.

Verified on 2026-11-08:

- Google's installed-app guide
  (<https://developers.google.com/youtube/v3/guides/auth/installed-apps>): desktop apps "are
  public clients and cannot keep secrets confidential"; the loopback IP address redirect with
  an HTTP listener on a random port is the recommended mechanism on Windows, macOS and Linux;
  PKCE is required ("Always use PKCE"), with S256 recommended; the manual copy/paste (OOB) and
  custom URI scheme methods are no longer supported; refresh tokens are issued and stay valid
  until revoked or expired.
- Google's OAuth overview (<https://developers.google.com/identity/protocols/oauth2>): a project
  with an external user type and publishing status "Testing" receives refresh tokens that
  expire in 7 days (unless only basic profile scopes are requested); tokens also stop working
  if revoked, unused for six months, or when the limit of 100 refresh tokens per Google Account
  per OAuth client is exceeded (the oldest is invalidated without warning).
- YouTube scopes (<https://developers.google.com/identity/protocols/oauth2/scopes>):
  `youtube.readonly` ("View your YouTube account"), `youtube` ("Manage your YouTube account"),
  `youtube.force-ssl` ("See, edit, and permanently delete your YouTube videos, ratings,
  comments and captions"), `youtubepartner`, `youtube.upload` and others.
- `playlists.insert` and `playlistItems.insert` each require one of `youtubepartner`, `youtube`
  or `youtube.force-ssl`. The `playlistItems.list` samples use `youtube.readonly`. The
  `videos.list` (`myRating`) and `subscriptions.list` (`mine`) pages require an authorised
  request but do not list scopes.

## Decision

1. **Client type:** for the intended local `stdio` deployment, use a Google OAuth client of
   type **Desktop app** with the authorization-code flow, **PKCE (S256)** and the **loopback IP
   redirect** on a random port, through a well-tested Google OAuth client library. The client
   secret of a desktop client is not treated as confidential, but it is still never committed
   (`NFR-05.1`). If `OD-15` selects a remote Streamable HTTP deployment instead, this ADR must
   be revised; web-server and installed-app assumptions are not mixed.
2. **Scopes (least privilege, incremental):**
   - Request `https://www.googleapis.com/auth/youtube.readonly` for all read features
     (`FR-01`…`FR-04` personal-library reads).
   - Request `https://www.googleapis.com/auth/youtube` **incrementally**, only when the user
     first starts playlist creation (`FR-05`). It is the narrowest documented scope that permits
     `playlists.insert` and `playlistItems.insert`; `youtube.force-ssl` includes permanent
     deletion of videos and comments, and `youtubepartner` is for content owners.
   - Check the scopes actually granted and disable features whose scope was refused.
   - Because the `videos.list` (`myRating`) and `subscriptions.list` (`mine`) pages do not name
     scopes, confirm in the first capped live test that `youtube.readonly` suffices; record the
     result before relying on it.
3. **Token storage:** store the refresh token in the operating system's credential store
   (Windows Credential Manager, macOS Keychain, Linux Secret Service) through a maintained
   keyring library, never in the repository, logs, fixtures or MCP responses. Access tokens are
   kept in memory only. The exact library depends on `OD-01`.
4. **Refresh and re-authorisation:** refresh the access token when it expires. If the refresh
   fails (for example `invalid_grant` after the 7-day Testing-mode expiry, revocation or
   the 100-token limit), delete the stored token and return a typed `authorization_required`
   error that explains how to re-run consent; no protected operation proceeds (`NFR-03.3`).

## Alternatives considered

- **Web-server flow.** Needs a confidential client and a hosted redirect endpoint; does not fit
  a local stdio server. Rejected unless `OD-15` chooses remote deployment.
- **API key only.** Cannot read private library data or create playlists. Rejected for
  personal features (public reads could still use the OAuth token).
- **`youtube.force-ssl` for writes.** Broader than needed. Rejected.
- **Token file in the user's home directory.** Simpler but weaker protection than the OS
  credential store. Kept only as a fallback if a platform has no credential store, with file
  permissions restricted to the user; requires review.

## Consequences

- Users in Testing mode must re-consent at least every 7 days; the error message must say so.
- The OAuth research note is updated with the installed-app findings.
- Scope sufficiency for two read methods remains to be confirmed empirically.
- The per-user versus shared Cloud project question (`OD-14`) affects who registers the OAuth
  client and whose quota is used; it is tracked separately.
