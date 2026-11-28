"""Stdio entry point and provider composition for team MCP integration."""
import argparse
from dataclasses import asdict
import json
import logging
import os
from pathlib import Path
import re
from urllib.parse import parse_qs, urlsplit

from platformdirs import user_state_path

from youtube_mcp.auth.oauth import DesktopClient, OAuthManager
from youtube_mcp.auth.tokens import KeyringTokenStore, ProtectedFileTokenStore
from youtube_mcp.errors import AppError, ProviderError, UnavailableError, ValidationError
from youtube_mcp.providers.cached import CachingProvider
from youtube_mcp.providers.fixture import FixtureProvider
from youtube_mcp.providers.live import LiveProvider
from youtube_mcp.quota.ledger import QuotaLedger
from youtube_mcp.quota.manager import QuotaManager


def _desktop(path):
    with open(path, encoding="utf-8") as stream:
        installed = json.load(stream)["installed"]
    return DesktopClient(installed["client_id"], installed["client_secret"])


def build_live():
    state = user_state_path("youtube-mcp", ensure_exists=True)
    project = os.environ.get("YOUTUBE_QUOTA_PROJECT", "")
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", project):
        raise ProviderError("Set YOUTUBE_QUOTA_PROJECT to your Google Cloud project ID.")
    read_path = os.environ.get("YOUTUBE_READ_CLIENT_FILE")
    write_path = os.environ.get("YOUTUBE_WRITE_CLIENT_FILE")
    oauth = None
    if read_path and write_path:
        read, write = _desktop(read_path), _desktop(write_path)
        if read.client_id == write.client_id:
            raise ProviderError("Use separate desktop clients for read and write consent.")
        if os.environ.get("YOUTUBE_TOKEN_STORE") == "protected-file":
            store = ProtectedFileTokenStore(state / "credentials" / project)
            write_store = store
        else:
            store = KeyringTokenStore(read.client_id)
            write_store = KeyringTokenStore(write.client_id)
        oauth = OAuthManager(read, write, store, write_store=write_store)
    elif read_path or write_path:
        raise ProviderError("Both desktop client file paths are required for OAuth.")
    quota = QuotaManager(QuotaLedger(state / f"quota-{project}.sqlite3"))
    key = os.environ.get("YOUTUBE_API_KEY")
    live = LiveProvider(quota, api_key=key, oauth=oauth)
    provider = CachingProvider(live) if key else live
    return provider, quota, oauth


def video_details(provider, quota, video_ref):
    if not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_ref):
        try:
            url = urlsplit(video_ref)
            if url.scheme in {"https", "http"}:
                if url.netloc == "youtu.be":
                    video_ref = url.path.removeprefix("/")
                elif url.netloc in {"youtube.com", "www.youtube.com", "m.youtube.com"}:
                    if url.path == "/watch":
                        values = parse_qs(url.query).get("v", [])
                        video_ref = values[0] if len(values) == 1 else ""
                    elif url.path.startswith("/shorts/"):
                        video_ref = url.path.removeprefix("/shorts/")
        except ValueError:
            raise ValidationError("Use a valid YouTube video ID or URL.") from None
    if not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_ref):
        raise ValidationError("Use a valid YouTube video ID or URL.")
    with quota.tool_scope():
        quota.check(quota.cost_of("videos.list"))
        videos = provider.get_videos([video_ref])
    if not videos or not videos[0].available:
        raise UnavailableError("The requested video is private, deleted, or unavailable.")
    return videos[0]


def create_server(provider, quota):
    from mcp.server import MCPServer
    from mcp.types import ToolAnnotations

    server = MCPServer("YouTube MCP")

    @server.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def auth_status() -> dict:
        """Report YouTube authorisation state and granted scopes."""
        try:
            return {"ok": True, "data": asdict(provider.auth_status()), "summary": "YouTube auth status."}
        except AppError as error:
            return {"ok": False, "error": error.as_dict()}

    @server.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_quota_status() -> dict:
        """Report locally tracked quota and next Pacific reset."""
        status = quota.status()
        data = asdict(status)
        data["resets_at"] = status.resets_at.isoformat()
        return {"ok": True, "data": data, "summary": "Local quota status."}

    @server.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_video_details(video_ref: str) -> dict:
        """Retrieve public details for a video ID, watch URL, short URL or Shorts URL."""
        try:
            video = video_details(provider, quota, video_ref)
            return {"ok": True, "data": asdict(video), "summary": "Public video metadata."}
        except AppError as error:
            return {"ok": False, "error": error.as_dict()}

    return server


def main():
    logging.getLogger("httpx").setLevel(logging.WARNING)
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixtures", type=Path)
    parser.add_argument("--authorise", action="store_true")
    parser.add_argument("--sign-out", action="store_true")
    args = parser.parse_args()
    if args.authorise and args.sign_out or args.fixtures and (args.authorise or args.sign_out):
        parser.error("Choose fixture mode, authorisation, sign-out, or live server mode.")
    try:
        if args.fixtures:
            provider = FixtureProvider.from_json(args.fixtures)
            quota = QuotaManager(QuotaLedger())
        else:
            provider, quota, oauth = build_live()
            if args.authorise:
                if oauth is None:
                    raise ProviderError("Configure both Desktop OAuth clients.")
                oauth.authorise()
                print("YouTube read consent granted.")
                return
            if args.sign_out:
                provider.sign_out()
                print("Signed out of YouTube.")
                return
        create_server(provider, quota).run(transport="stdio")
    except AppError as error:
        parser.exit(1, f"{error.code}: {error.message}\n")


if __name__ == "__main__":
    main()
