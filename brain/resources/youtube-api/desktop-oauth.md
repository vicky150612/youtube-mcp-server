---
title: Desktop OAuth and PKCE
created: 2026-11-28
source: https://developers.google.com/identity/protocols/oauth2/native-app
requirements: [NFR-03]
issues: [17]
author: Jithamanyu404
---

# Desktop OAuth and PKCE

Use Desktop loopback and PKCE S256 with an unpredictable state.
Google's Desktop flow lacks incremental authorization. The proposed
adaptation uses separate read and on-demand write grants. Both grants
must select the same YouTube channel before writes are enabled.

[[brain/projects/youtube-mcp/overview]]
