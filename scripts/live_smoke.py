"""Weekly public-only API check, with mandatory upper caps and zero writes."""
import os

from youtube_mcp.providers.live import LiveProvider
from youtube_mcp.quota.ledger import QuotaLedger
from youtube_mcp.quota.manager import QuotaManager


def cap(name, maximum):
    raw = os.environ.get(name, "")
    if not raw.isascii() or not raw.isdecimal() or not 0 < int(raw) <= maximum:
        raise SystemExit(f"{name} must be between 1 and {maximum}.")
    return int(raw)


def main():
    quota = QuotaManager(QuotaLedger(), general=cap("LIVE_GENERAL_CAP", 200),
                         search=cap("LIVE_SEARCH_CAP", 2), videos_insert=0)
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        raise SystemExit("The scheduled YouTube API key is missing.")
    provider = LiveProvider(quota, api_key=api_key, read_only=True)
    with quota.tool_scope():
        ids = provider.search_videos("relational databases lecture", max_results=5)
        if not ids or not provider.get_videos(ids):
            raise SystemExit("The read-only smoke query returned no metadata.")
    print("PASS live search and public metadata retrieval.")


if __name__ == "__main__":
    main()
