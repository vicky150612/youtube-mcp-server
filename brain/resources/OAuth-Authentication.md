---
title: OAuth 2.0 Authentication
type: research
aliases:
  - OAuth Authentication
tags:
  - research
  - youtube-mcp
  - oauth
  - security
sources:
  - "https://developers.google.com/identity/protocols/oauth2"
  - "https://developers.google.com/youtube/v3/guides/auth/server-side-web-apps"
  - "https://developers.google.com/youtube/v3/guides/auth/installed-apps"
  - "https://developers.google.com/identity/protocols/oauth2/scopes"
author:
  - Person 3
created: 2026-11-07
---

# OAuth 2.0 Authentication

## Overview

OAuth 2.0 lets an application obtain limited, user-approved access to resources without asking for or handling the user's Google password. For this project it is the authorization mechanism for YouTube account data and operations performed on a user's behalf.

## Key Concepts

- **Authorization Code flow:** The application redirects the user to Google's authorization endpoint with its client identity, redirect URI and requested scopes. After the user authenticates and grants consent, Google redirects back with an authorization code. The application exchanges that code server-side for an access token and, when offline access is requested and granted, a refresh token. Google's web-server guide recommends using a `state` value to help verify that the callback corresponds to an authorization request initiated by the application.
- **Access token:** A short-lived credential sent with API requests, preferably in the HTTP `Authorization` header. Its scopes restrict the resources and operations it permits.
- **Refresh token:** A longer-lived credential used to obtain new access tokens without asking the user to repeat consent. It must be kept in secure long-term storage and can stop working.
- **Scopes and consent:** Scopes describe the requested permissions. Google's guidance recommends requesting only needed scopes and, where appropriate, requesting them incrementally. The application should check which scopes were actually granted and disable features that require permissions it did not receive.

## Important Findings

- Google recommends using well-tested OAuth client libraries to implement the flow and token lifecycle.
- A web-server application's redirect URI must match an authorized URI configured for its OAuth client. The app should protect authorization codes and keep client-secret files outside publicly accessible locations and source control.
- The server-side web-app guide recommends offline access when the application needs to refresh tokens without asking the user to re-consent.
- Access tokens have limited lifetimes. When one expires, the application can use a valid refresh token to obtain another access token. If usable credentials are unavailable, the user must authorize again.
- **Project constraint:** the SRS records that refresh tokens issued while Google's OAuth consent screen is in Testing mode expire after seven days; the implementation must provide a clear re-authorisation path (`NFR-03.3`). Google's OAuth overview confirms this: an external-user-type project in "Testing" status receives refresh tokens that expire in 7 days unless only basic profile scopes are requested. Refresh tokens also stop working when revoked, after six months unused, or when the limit of 100 refresh tokens per Google Account per OAuth client is exceeded (the oldest is invalidated without warning).

### Installed (desktop) applications — added 2026-11-08

The findings above describe the web-server flow. A locally run MCP server (stdio transport) is an installed application, for which Google's installed-app guide states:

- Desktop apps "are public clients and cannot keep secrets confidential"; the client secret is not treated as confidential (it must still not be committed).
- The **loopback IP address** redirect, with an HTTP listener on a random available port, is the recommended mechanism on Windows, macOS and Linux.
- **PKCE is required** ("Always use PKCE"), with the S256 method recommended.
- The manual copy/paste (out-of-band) and custom URI scheme methods are no longer supported.

### YouTube scopes

Google's scope list describes `youtube.readonly` as "View your YouTube account", `youtube` as "Manage your YouTube account" and `youtube.force-ssl` as "See, edit, and permanently delete your YouTube videos, ratings, comments and captions". `playlists.insert` and `playlistItems.insert` each accept `youtubepartner`, `youtube` or `youtube.force-ssl`.

## Relevance to Our Project

The project needs user authorization for personal library access and playlist creation. Use the OAuth client type appropriate to the eventual application architecture, store tokens securely outside the repository and logs, request only the scopes required by each supported operation, and report expired, revoked or insufficiently scoped credentials clearly. The project's proposed choice (desktop client, PKCE, loopback redirect, `youtube.readonly` for reads, `youtube` requested incrementally for playlist creation, refresh token in the operating system credential store) is recorded in the project's ADR 0008 and awaits team approval; it depends on the transport decision (`OD-15`).

## Related Requirements

`FR-03`, `FR-04` (library reads), `FR-05` (writes in the authorised user's account), `NFR-03.1`, `NFR-03.2`, `NFR-03.3`, `TQ-04`. Requirement source: [SRS](../../docs/srs.md).

## Sources

- **OAuth 2.0** — Google Identity, Google for Developers. https://developers.google.com/identity/protocols/oauth2 (accessed 2026-11-07; publication/update date not stated on the page).
- **Using OAuth 2.0 for Web Server Applications** — Google Identity, Google for Developers. https://developers.google.com/youtube/v3/guides/auth/server-side-web-apps (redirects to Google's web-server OAuth guide; accessed 2026-11-07; publication/update date not stated on the page).
- **OAuth 2.0 for Mobile & Desktop Apps** — Google for Developers. https://developers.google.com/youtube/v3/guides/auth/installed-apps (accessed 2026-11-08).
- **OAuth 2.0 Scopes for Google APIs** — Google for Developers. https://developers.google.com/identity/protocols/oauth2/scopes (accessed 2026-11-08).
- **YouTube MCP Server SRS** — project-specific seven-day Testing-mode token constraint, `NFR-03.3`. [SRS](../../docs/srs.md).

## Related Notes

- [[YouTube-Data-API|YouTube Data API]]
- [[YouTube-API-Quota-Management|YouTube API Quota Management]]
- [[YouTube-Playlist-Resource|YouTube Playlist Resource]]
- [[MCP-Architecture|MCP Architecture]]
