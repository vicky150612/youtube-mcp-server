---
title: "Model Context Protocol (MCP) — Architecture"
type: research
author:
  - Person 2
created: 2026-11-07
aliases:
  - "MCP Architecture"
tags:
  - research
  - youtube-mcp
  - mcp
sources:
  - "https://modelcontextprotocol.io/docs/learn/architecture"
---

# Model Context Protocol (MCP) — Architecture

> **Protocol version:** everything in this note describes MCP as documented for protocol version **`2026-07-28`**. Earlier protocol versions behave differently and are not covered here.

## Overview

The Model Context Protocol (MCP) is a protocol for exchanging context between AI applications and the programs that provide that context. It uses a client-server architecture. An AI application (the **host**) connects to one or more **servers** through dedicated **clients**, and they exchange JSON-RPC 2.0 messages over a transport such as stdio or Streamable HTTP.

According to the official documentation, MCP covers **only the protocol for context exchange**. It does not dictate how AI applications use LLMs or manage the context they receive.

It matters to us because our YouTube MCP Server is an MCP server. This architecture defines how hosts discover and call its capabilities.

## Key Concepts

- **MCP Host**: the AI application that coordinates and manages one or more MCP clients (e.g. Claude Code, Claude Desktop, Visual Studio Code).
- **MCP Client**: a component that maintains a connection to an MCP server and obtains context from it for the host to use.
- **MCP Server**: a program that provides context to MCP clients, regardless of whether it runs locally or remotely.
- **Data layer**: the inner layer. A JSON-RPC 2.0 based protocol that defines message structure and semantics, discovery, primitives and notifications.
- **Transport layer**: the outer layer. Handles connection establishment, message framing and authorisation.
- **Primitives**: what clients and servers can offer each other (server: tools, resources, prompts; client: elicitation).
- **Capabilities**: the features and operations a client or server supports (e.g. tools, resources, prompts).
- **`_meta`**: the per-request metadata field that carries the protocol version, client capabilities and client identity.
- **Stateless**: every request contains all the information needed to process it. Servers infer nothing from previous requests.

## Important Findings

> This section reflects the **official MCP documentation** for protocol version `2026-07-28`.

### Scope

The Model Context Protocol includes:

- **MCP Specification**: implementation requirements for clients and servers.
- **MCP SDKs**: language-specific implementations of MCP.
- **MCP Development Tools**: e.g. the MCP Inspector.
- **MCP Reference Server Implementations**.

### Participants

- A host creates **one MCP client per MCP server**. Each client maintains a **dedicated connection** to its server.
- Example from the docs: when VS Code connects to the Sentry MCP server and the local filesystem server, it instantiates a separate client object for each connection.
- **Local** servers use the **stdio** transport and typically serve a **single** client.
- **Remote** servers use the **Streamable HTTP** transport and typically serve **many** clients.

### Layers

**Data layer** (JSON-RPC 2.0 based) includes:

- **Discovery**: clients can query a server's supported protocol versions, capabilities and identity via `server/discover`.
- **Server features**: tools, resources and prompts.
- **Client features**: elicitation (servers can request user input). Sampling is deprecated as of `2026-07-28`.
- **Utility features**: notifications for real-time updates and progress tracking for long-running operations.

**Transport layer** supports two mechanisms:

- **Stdio transport**: standard input/output streams between local processes on the same machine, with no network overhead.
- **Streamable HTTP transport**: HTTP POST for client-to-server messages, with optional Server-Sent Events for streaming. Supports standard HTTP authentication (bearer tokens, API keys, custom headers). MCP recommends using **OAuth** to obtain authentication tokens.

The transport layer abstracts communication details, so the **same JSON-RPC 2.0 message format** is used across all transports.

### JSON-RPC relationship

- MCP uses **JSON-RPC 2.0** as its underlying RPC protocol.
- Clients and servers send **requests** to each other and receive **responses**. A unique `id` correlates each request with its response.
- **Notifications** are messages with no `id`. No response is expected or sent.

### Statelessness and discovery (`2026-07-28`)

- MCP is **stateless**: every request carries the information needed to process it on its own.
- Every request's `_meta` field carries:
  - `io.modelcontextprotocol/protocolVersion` (required).
  - `io.modelcontextprotocol/clientCapabilities` (required).
  - `io.modelcontextprotocol/clientInfo` (should be included unless the client is configured not to).
- **Every server must implement `server/discover`.**
- **Clients are not required to call `server/discover`** before other requests. Calling it is optional; a client may send any request directly and handle a version error if one comes back. Discovery is a convenient way to fetch identity, capabilities and supported versions in one request.
- The `server/discover` response contains `supportedVersions`, `capabilities`, `serverInfo` (in `_meta`), and the caching hints `ttlMs` and `cacheScope`. The response is typically cacheable.
- **Version mismatch:** if a server does not support the requested version, it rejects the request with an `UnsupportedProtocolVersionError` listing the versions it supports, and the client retries with a mutually supported version.
- Capability exchange tells each party which primitives the other supports and whether change notifications are available, so unsupported operations are never attempted.

### Primitives

**Server primitives:**

- **Tools**: executable functions that AI applications invoke to perform actions (e.g. file operations, API calls, database queries).
- **Resources**: data sources that provide contextual information (e.g. file contents, database records, API responses).
- **Prompts**: reusable templates that help structure interactions with language models (e.g. system prompts, few-shot examples).

Associated methods:

- `*/list`: discovery (e.g. `tools/list`, `resources/list`). Supports an optional `cursor` parameter for pagination.
- `*/get`: retrieval.
- `tools/call`: tool execution.
- `resources/read`: reading a resource.

Listings can be **dynamic**: clients use `*/list` to discover what is currently available.

**Client primitives:**

- **Elicitation**: servers request additional information or confirmation from the user with `elicitation/create`. It is delivered through the Multi Round-Trip Requests pattern.
- **Deprecated as of `2026-07-28`:**
  - **Sampling** (`sampling/createMessage`). New implementations should integrate directly with LLM provider APIs.
  - **Logging**. New implementations should log to `stderr` (stdio transport) or use OpenTelemetry.

**Extensions:** optional extensions build on the core protocol. For example, the **Tasks** extension lets servers return a durable handle for long-running requests so clients can poll for status and retrieve results later.

### Tool definitions and execution

Each tool returned by `tools/list` includes:

- **`name`**: unique identifier within the server. Should follow a clear naming pattern (e.g. `calculator_arithmetic` rather than `calculate`).
- **`title`**: human-readable display name.
- **`description`**: what the tool does and when to use it.
- **`inputSchema`**: a JSON Schema defining required and optional input parameters.

The `tools/list` result is marked `"resultType": "complete"` and can carry `ttlMs` (freshness hint in milliseconds) and `cacheScope` (who may reuse the response).

A `tools/call` request contains:

- **`name`**: must exactly match the name from discovery.
- **`arguments`**: parameters as defined by the tool's `inputSchema`.
- **`_meta`**: the standard per-request fields.

A tool result contains a **`content` array** of typed content objects (e.g. `"type": "text"`). MCP supports various content types (text, images, resources, etc.).

### Notifications

- Change notifications are **opt-in**. The client opens a long-lived **`subscriptions/listen`** stream with a `notifications` filter (e.g. `"toolsListChanged": true`).
- The server first sends **`notifications/subscriptions/acknowledged`**, listing the subset of the filter it agreed to honour.
- It then delivers notifications such as **`notifications/tools/list_changed`** on that stream.
- Every notification carries `io.modelcontextprotocol/subscriptionId` in `_meta`. Its value is the JSON-RPC `id` of the `subscriptions/listen` request.
- `notifications/tools/list_changed` is only available from servers that declared `"tools": {"listChanged": true}`.
- Delivery is **best effort**, particularly across transport reconnects. Clients should also rely on polling to keep results fresh.
- On receiving a list-changed notification, the client typically re-requests `tools/list`.

### Request flow (`2026-07-28`)

The documentation's worked example shows this sequence:

1. **Discovery (optional for the client):** `server/discover` returns supported versions, capabilities and server identity.
2. **Tool discovery:** `tools/list` returns tool definitions.
3. **Tool execution:** `tools/call` invokes a tool and returns a `content` array.
4. **Real-time updates:** `subscriptions/listen` → `notifications/subscriptions/acknowledged` → `notifications/tools/list_changed` → client re-requests `tools/list`.

On the host side, the docs describe the AI application combining tools from all connected servers into a unified tool registry for the LLM, then routing each LLM tool call to the correct MCP server and returning the result to the conversation.

## Relevance to Our Project

> The points below are **our team's interpretation** of the official documentation, not statements from the MCP documentation. They assume protocol version `2026-07-28`.

- **Our role:** the YouTube MCP Server is the **MCP Server** participant. A host such as Claude Code or Claude Desktop connects to it through its own dedicated MCP client.
- **Tools:** YouTube Data API capabilities (e.g. video lookup, search) map naturally to **Tools**. Each should have a clear, namespaced `name`, a description explaining when to use it, and a precise JSON Schema `inputSchema`. Validating inputs against the schema also helps avoid wasting YouTube API quota on invalid requests (see [[YouTube-Data-API|YouTube Data API]]).
- **Resources:** relatively static reference data could be exposed as **Resources**. Which data, if any, is still to be decided.
- **Transport:** a local **stdio** server suits a single-user setup. **Streamable HTTP** with OAuth matters only if we deploy remotely. No transport decision is recorded in the repository yet.
- **Logging:** use `stderr` (or OpenTelemetry) rather than the deprecated Logging primitive. With stdio, keeping stdout for protocol messages only is important.
- **Discovery:** we must implement `server/discover`; MCP SDKs may handle this for us, which needs confirming once an SDK is chosen.
- **Statelessness:** fits a server whose tools each make independent YouTube API calls.
- **Caching:** MCP's `ttlMs` / `cacheScope` hints for discovery and tool lists are separate from caching YouTube API responses for quota reasons.
- **Deprecated features:** we should not build on Sampling or Logging.

## Related Requirements

None assigned yet.

## Sources

- **Architecture overview**
  - Organisation: Model Context Protocol (modelcontextprotocol.io)
  - URL: https://modelcontextprotocol.io/docs/learn/architecture
  - Accessed: 2026-11-07
  - Protocol version documented: `2026-07-28`
  - Note: no author or publication date was visible on the page.

## Related Notes

- [[YouTube-Data-API|YouTube Data API]]
- [[MCP-Tools-and-Resources|MCP Tools and Resources]]
- [[OAuth-Authentication|OAuth 2.0 Authentication]]
- YouTube MCP Server project note (planned, not yet created)
