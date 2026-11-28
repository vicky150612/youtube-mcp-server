---
title: OAuth Testing mode expiry
created: 2026-11-28
source: https://developers.google.com/identity/protocols/oauth2#expiration
requirements: [NFR-03]
issues: [17]
author: Jithamanyu404
---

# OAuth Testing mode expiry

An external app in Testing receives seven-day refresh tokens for
YouTube scopes. Revocation can invalidate a grant earlier. Upon
`invalid_grant`, clear the affected credential and report reauthorisation.
Keep access tokens in memory and use the native OS store for refresh tokens.

[[brain/projects/youtube-mcp/overview]]
