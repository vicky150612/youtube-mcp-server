---
title: "MCP Tools and Resources"
type: research
aliases:
  - "MCP Tools and Resources"
tags:
  - research
  - youtube-mcp
  - mcp
source: "https://modelcontextprotocol.io/docs/learn/server-concepts"
sources:
  - "https://modelcontextprotocol.io/docs/learn/server-concepts"
  - "https://modelcontextprotocol.io/docs/learn/client-concepts"
protocol_version: "2026-07-28 (inferred from linked specification pages)"
---

# MCP Tools and Resources

> **Protocol version:** neither source page explicitly declares a protocol version. Version **`2026-07-28`** is **inferred** from the specification pages they link to, and from the client page's statement that Roots and Sampling are deprecated "as of protocol version `2026-07-28`".

## Overview

MCP servers expose capabilities to AI applications through three building blocks: **Tools**, **Resources** and **Prompts**. This note focuses on Tools and Resources, how they differ, and how MCP clients and hosts use them, including the client-side features (such as elicitation) that servers can rely on.

It matters to us because deciding what the YouTube MCP Server exposes as Tools versus Resources is a core design choice.

## Key Concepts

- **Tool**: a schema-defined function that the LLM can actively call to perform an action. **Model-controlled.**
- **Resource**: a passive data source providing **read-only** access to information for context, identified by a unique URI. **Application-controlled.**
- **Prompt**: a pre-built, parameterised instruction template that the user invokes explicitly. **User-controlled.**
- **`inputSchema`**: the JSON Schema that defines a tool's expected inputs.
- **Resource URI**: the unique identifier of a resource (e.g. `file:///path/to/document.md`).
- **MIME type**: the content type each resource declares so clients can handle its content appropriately.
- **Direct resource**: a resource with a fixed URI.
- **Resource template**: a parameterised URI pattern (e.g. `travel://activities/{city}/{category}`) for dynamic resources.
- **Parameter completion**: suggestions for valid parameter values in resource templates (and prompts).
- **Host**: the application users interact with (e.g. Claude.ai or an IDE); it coordinates multiple clients.
- **Client**: a protocol-level component instantiated by the host; each client handles one direct connection with one server.
- **Elicitation**: a client feature that lets servers request specific information from users during an interaction.
- **Multi Round-Trip Requests (MRTR)**: the pattern used to deliver elicitation requests.

## Important Findings

> This section reflects the **official MCP documentation** (server-concepts and client-concepts pages).

### Server primitives and who controls them

| Primitive | Description | Examples | Who controls it |
|---|---|---|---|
| **Tools** | Functions the LLM can actively call, deciding when to use them based on user requests. Can write to databases, call external APIs, modify files or trigger other logic. | Search flights, send messages, create calendar events | **Model** |
| **Resources** | Passive data sources that provide read-only access to information for context, such as file contents, database schemas or API documentation. | Retrieve documents, access knowledge bases, read calendars | **Application** |
| **Prompts** | Pre-built instruction templates that tell the model to work with specific tools and resources. | Plan a vacation, summarise meetings, draft an email | **User** |

### Tools

**Purpose**

- Tools enable AI models to **perform actions**.
- Each tool defines a **single operation** with typed inputs and outputs.
- The model requests tool execution based on context.

**Input schemas**

- Tools are schema-defined interfaces. MCP uses **JSON Schema** for validation.
- The documented example definition contains:
  - `name` (e.g. `searchFlights`).
  - `description` (e.g. "Search for available flights").
  - `inputSchema` with `type: "object"`, typed `properties` (each with a `description`), and a `required` list.

**Discovery and execution**

| Method | Purpose | Returns |
|---|---|---|
| `tools/list` | Discover available tools | Array of tool definitions with schemas |
| `tools/call` | Execute a specific tool | Tool execution result |

**Results**

- The server-concepts page describes the return value of `tools/call` only as a "tool execution result".
- The result structure (a `content` array of typed content objects, e.g. `"type": "text"`) is documented on the architecture page; see [[MCP-Architecture|MCP Architecture]].

**User interaction model**

- Tools are **model-controlled**: AI models can discover and invoke them automatically.
- Tools **may require user consent** prior to execution, so users keep control over actions taken by a model.
- MCP emphasises human oversight. Applications can implement user control through mechanisms such as:
  - Displaying available tools in the UI so users can decide whether a tool is available in specific interactions.
  - Approval dialogs for individual tool executions.
  - Permission settings for pre-approving certain safe operations.
  - Activity logs showing all tool executions and their results.

### Resources

**Purpose**

- Resources provide structured access to information that the AI application can retrieve and provide to models as **context**.
- They expose data from files, APIs, databases or any other source.
- The **application** decides how to use the data: selecting relevant portions, searching with embeddings, or passing it all to the model.

**URIs and MIME types**

- Each resource has a **unique URI** (e.g. `file:///path/to/document.md`).
- Each resource declares its **MIME type** for appropriate content handling.

**Discovery patterns**

- **Direct resources**: fixed URIs pointing to specific data.
  - Example: `calendar://events/2024` returns calendar availability for 2024.
- **Resource templates**: dynamic URIs with parameters for flexible queries.
  - Example template: `travel://activities/{city}/{category}`.
  - Example resolved URI: `travel://activities/barcelona/museums`.
  - Templates include metadata such as `title`, `description` and expected `mimeType`, making them discoverable and self-documenting.

Documented template example:

```json
{
  "uriTemplate": "weather://forecast/{city}/{date}",
  "name": "weather-forecast",
  "title": "Weather Forecast",
  "description": "Get weather forecast for any city and date",
  "mimeType": "application/json"
}
```

**Listing, reading and monitoring**

| Method | Purpose | Returns |
|---|---|---|
| `resources/list` | List available direct resources | Array of resource descriptors |
| `resources/templates/list` | Discover resource templates | Array of resource template definitions |
| `resources/read` | Retrieve resource contents | Resource data with metadata |
| `subscriptions/listen` | Monitor resource changes | Stream of update notifications |

- To watch specific resources, a client sends `subscriptions/listen` with the resource URIs in the `resourceSubscriptions` filter.
- The server then delivers `notifications/resources/updated` on that stream whenever a watched resource changes.

**Parameter completion**

- Dynamic resources support parameter completion.
- Example: typing "Par" for `weather://forecast/{city}` might suggest "Paris" or "Park City".
- This helps users discover valid values without knowing the exact format.

**User interaction model**

- Resources are **application-driven**. Common patterns include:
  - Tree or list views for browsing.
  - Search and filter interfaces.
  - Automatic context inclusion or smart suggestions.
  - Manual or bulk selection.
- The protocol does **not** mandate specific UI patterns.

### Prompts (brief, for contrast)

- Prompts are **user-controlled** and require explicit invocation rather than automatic triggering.
- They can reference available resources and tools, and support parameter completion.
- Methods: `prompts/list` (discover prompts) and `prompts/get` (retrieve a full prompt definition with arguments).
- Typical UI patterns: slash commands, command palettes, dedicated buttons, context menus.

### Tools vs Resources

| Aspect | Tools | Resources |
|---|---|---|
| Role | Perform actions | Provide context |
| Control | **Model-controlled** | **Application-controlled** |
| Access | May have side effects (write, call APIs, modify files) | **Read-only** |
| Identified by | Tool `name` | Unique **URI** |
| Inputs | JSON Schema `inputSchema` | URI template parameters (for templates) |
| Discovery | `tools/list` | `resources/list`, `resources/templates/list` |
| Use | `tools/call` | `resources/read` |

In the documentation's multi-server example, the user selects resources to include, the AI reads them to gather context, and then executes tools, requesting user approval where necessary.

### How clients and hosts use these capabilities

**Hosts and clients**

- The **host** is the application users interact with (e.g. Claude.ai or an IDE). It manages the user experience and coordinates multiple clients.
- **Clients** are protocol-level components instantiated by the host. Each client handles one direct communication with one server.
- Clients make use of context provided by servers (tools, resources, prompts) and may also provide features **to** servers.

**Client features**

| Feature | Status (as of `2026-07-28`) |
|---|---|
| **Elicitation** | Active |
| **Roots** | **Deprecated**, scheduled for removal |
| **Sampling** | **Deprecated**, scheduled for removal |

**Elicitation**

- Lets servers request specific information from users on demand, instead of requiring everything up front or failing when data is missing.
- Two modes:
  - **Form mode**: the server asks the client to collect structured data. The request includes a schema that the client uses to build an input form and validate the response.
  - **URL mode**: the server provides a URL for the user to open. The interaction happens out of band and its data **never passes through the client**. Suitable for sensitive flows such as credential entry or third-party OAuth authorisation.
- Delivered via the **Multi Round-Trip Requests** pattern:
  1. While processing a request such as `tools/call`, the server responds with an `InputRequiredResult` whose `inputRequests` field carries one or more `elicitation/create` requests.
  2. The client gathers the input from the user.
  3. The client retries the original request, attaching the collected `inputResponses` and echoing back any `requestState` the server included.
- User options: provide the information, decline (with optional explanation), or cancel the entire operation. Clients validate responses against the provided schema before returning them.
- **URL handling**: clients show the full URL and gather explicit consent before opening it, and never fetch the URL automatically. The client only learns whether the user consented.
- **Security rule**: servers **must not** use form mode to request sensitive information such as **passwords, API keys, access tokens or payment credentials**. Those interactions belong in **URL mode**, which keeps the data out of band so it never passes through the client or the LLM context. Clients warn about suspicious requests and let users review form data before sending.

**Roots (deprecated)**

- File URIs (`file://` only) that communicate filesystem boundaries to servers.
- Advisory coordination only, **not** a security boundary; servers "SHOULD respect" them.
- New implementations should pass directories or files via tool parameters, resource URIs or server configuration instead.

**Sampling (deprecated)**

- Allowed servers to request LLM completions through the client.
- New implementations should integrate directly with LLM provider APIs instead.

## Relevance to Our Project

> The points below are **our team's interpretation** of the official documentation, not statements from the MCP documentation. They assume protocol version `2026-07-28`.

- **YouTube Data API calls as Tools:** search and video-detail lookups are operations the model decides to invoke, so they fit the **model-controlled Tools** primitive. Each tool should perform a single operation with a clear `name`, a description of when to use it, and a precise `inputSchema`.
- **Schema validation protects quota:** validating inputs against the `inputSchema` before calling YouTube avoids wasting quota, since invalid YouTube API requests still incur quota cost (see [[YouTube-Data-API|YouTube Data API]]).
- **Possible Resources:** read-only context could be exposed as **application-controlled Resources**, potentially via a resource template. A pattern such as `youtube://video/{videoId}` is **illustrative only, not a decision**.
- **Tools vs Resources trade-off (open question):** because Resources are application-controlled, how readily they reach the model depends on the host's UI. This may argue for Tools as the primary interface, with Resources as an optional addition. This needs a team decision.
- **Elicitation and credentials:** if we ever need OAuth, URL-mode elicitation is the documented route. We must **never** request a YouTube API key or other credential via form-mode elicitation.
- **Avoid deprecated features:** do not build on Roots or Sampling.
- **Human oversight:** hosts may show approval dialogs for our tools, so tool names and descriptions should be clear enough for users to understand what they approve.

## Related Requirements

None assigned yet.

## Sources

- **Understanding MCP servers** (Server concepts)
  - Organisation: Model Context Protocol (modelcontextprotocol.io)
  - URL: https://modelcontextprotocol.io/docs/learn/server-concepts
  - Accessed: 2026-11-07
- **Understanding MCP clients** (Client concepts)
  - Organisation: Model Context Protocol (modelcontextprotocol.io)
  - URL: https://modelcontextprotocol.io/docs/learn/client-concepts
  - Accessed: 2026-11-07
- Notes:
  - No author or publication date was visible on either page.
  - Protocol version `2026-07-28` is inferred from linked specification pages, not explicitly declared by either page.
  - Not covered by these sources: exact response formats of `resources/list` and `resources/read`, tool annotations, tool output schemas, and the parameter-completion method name.

## Related Notes

- [[MCP-Architecture|MCP Architecture]]
- [[YouTube-Data-API|YouTube Data API]]
- [[YouTube MCP Server]] *(planned — not yet created)*
- [[OAuth Authentication]] *(planned — not yet created)*
