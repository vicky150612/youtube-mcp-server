import httpx
import pytest

from youtube_mcp.errors import AuthRequiredError
from youtube_mcp.providers.live import LiveProvider
from youtube_mcp.quota.ledger import QuotaLedger
from youtube_mcp.quota.manager import QuotaManager


class OAuth:
    def token(self, *, write=False):
        return "fixture-write" if write else "fixture-read"

    def ensure_write_scope(self):
        pass


def test_likes_fallback_unknown_time_and_unavailable_video():
    def response(request):
        assert request.headers["Authorization"] == "Bearer fixture-read"
        resource = request.url.path.rsplit("/", 1)[-1]
        params = request.url.params
        if resource == "channels":
            return httpx.Response(200, json={"items": [{"id": "FixtureChannel"}]})
        if resource == "videos" and params.get("myRating") == "like":
            return httpx.Response(200, json={"items": [{"id": "Fixture0001"}]})
        if resource == "videos":
            assert params["id"] == "Fixture0001"
        return httpx.Response(200, json={"items": []})

    quota = QuotaManager(QuotaLedger())
    provider = LiveProvider(quota, oauth=OAuth(),
                            http=httpx.Client(transport=httpx.MockTransport(response)))
    library = provider.get_library()
    assert library.liked[0].added_at is None
    assert library.liked[0].video.video_id == "Fixture0001"
    assert library.liked[0].video.available is False
    assert quota.status().general_remaining == 9995


def test_read_and_write_grants_must_select_same_channel():
    def response(request):
        assert request.method == "GET"
        return httpx.Response(200, json={"items": [{"id": request.headers["Authorization"]}]})

    quota = QuotaManager(QuotaLedger())
    provider = LiveProvider(quota, oauth=OAuth(),
                            http=httpx.Client(transport=httpx.MockTransport(response)))
    with pytest.raises(AuthRequiredError):
        provider.ensure_write_scope()
    with pytest.raises(AuthRequiredError):
        provider.create_playlist("Synthetic")
    assert quota.status().general_remaining == 9998


def test_verified_writes_are_private_and_accounted_for():
    import json

    writes = []

    def response(request):
        if request.method == "GET":
            return httpx.Response(200, json={"items": [{"id": "FixtureChannel"}]})
        assert request.headers["Authorization"] == "Bearer fixture-write"
        writes.append(json.loads(request.content))
        return httpx.Response(200, json={"id": "PLfixture"})

    quota = QuotaManager(QuotaLedger())
    provider = LiveProvider(quota, oauth=OAuth(),
                            http=httpx.Client(transport=httpx.MockTransport(response)))
    with quota.tool_scope():
        provider.ensure_write_scope()
        playlist_id = provider.create_playlist("Synthetic")
        provider.add_playlist_item(playlist_id, "Fixture0001")
    assert writes[0]["status"]["privacyStatus"] == "private"
    assert writes[1]["snippet"]["resourceId"]["videoId"] == "Fixture0001"
    assert quota.status().general_remaining == 9898
