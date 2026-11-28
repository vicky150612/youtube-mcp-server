"""Launch a fixture stdio server and exercise a 2026-07-28 MCP read-only tool."""
import asyncio
import sys

from mcp import Client, StdioServerParameters


async def main():
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "youtube_mcp.server", "--fixtures", "tests/fixtures/provider.json"],
    )
    async with asyncio.timeout(30), Client(params) as client:
        assert client.protocol_version == "2026-07-28"
        result = await client.call_tool("get_video_details", {"video_ref": "Fixture0001"})
        assert not result.is_error, result.content
        payload = result.structured_content
        assert payload and payload["ok"]
        assert payload["data"]["video_id"] == "Fixture0001"


if __name__ == "__main__":
    asyncio.run(main())
