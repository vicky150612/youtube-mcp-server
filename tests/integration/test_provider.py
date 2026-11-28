from datetime import UTC, datetime, timedelta
from pathlib import Path

import httpx
import pytest

from youtube_mcp.errors import (
    AuthRequiredError, ChannelRequiredError, ForbiddenError, OverBudgetError,
    QuotaExceededError, RateLimitedError, UnknownCostError,
)
from youtube_mcp.models import QuotaCost
from youtube_mcp.providers.cached import CachingProvider
from youtube_mcp.providers.fixture import FixtureProvider
from youtube_mcp.providers.live import LiveProvider
from youtube_mcp.quota.ledger import QuotaLedger
from youtube_mcp.quota.manager import QuotaManager


class Clock:
    value = datetime(2026, 11, 28, 7, 59, tzinfo=UTC)

    def now(self):
        return self.value


def live(handler, **kwargs):
    limits = kwargs.pop("limits", {})
    quota = QuotaManager(QuotaLedger(), **limits)
    client = httpx.Client(transport=httpx.MockTransport(handler))
    return LiveProvider(quota, api_key="synthetic", http=client, wait=lambda _: None, **kwargs), quota


def test_video_batching_and_partial_fields():
    requests = []

    def response(request):
        requests.append(request)
        return httpx.Response(200, json={"items": [{
            "id": request.url.params["id"].split(",")[0],
            "snippet": {"title": "Synthetic", "channelId": "fixture", "defaultAudioLanguage": "EN-us"},
            "contentDetails": {"duration": "PT1M30S"},
        }]})

    provider, quota = live(response)
    results = provider.get_videos([f"Fixture{i:04d}" for i in range(51)])
    assert [video.video_id for video in results] == ["Fixture0000", "Fixture0050"]
    assert len(requests[0].url.params["id"].split(",")) == 50
    assert "fields" in requests[0].url.params and "key" not in requests[0].url.params
    assert results[0].tags == () and results[0].description is None
    assert (results[0].duration_s, results[0].language) == (90, "en")
    assert quota.status().general_remaining == 9998


def test_workflow_budget_precheck_issues_zero_http_requests():
    provider, _ = live(lambda _: pytest.fail("Unexpected HTTP call"), limits={"general": 1})
    with pytest.raises(OverBudgetError):
        provider.get_videos([f"Fixture{i:04d}" for i in range(51)])


def test_search_cap_spans_methods_and_pages():
    def response(request):
        suffix = "2" if "pageToken" in request.url.params else "1"
        return httpx.Response(200, json={
            "items": [{"id": {"videoId": "Fixture000" + suffix}}], "nextPageToken": "next",
        })

    provider, quota = live(response)
    with quota.tool_scope():
        assert provider.search_videos("example", pages=2) == ["Fixture0001", "Fixture0002"]
        with pytest.raises(OverBudgetError):
            provider.search_channels("example")
    assert quota.status().search_remaining == 98
    assert quota.status().general_remaining == 10_000


@pytest.mark.parametrize(("status", "reason", "expected"), [
    (403, "quotaExceeded", QuotaExceededError),
    (429, "rateLimitExceeded", RateLimitedError),
    (403, "youtubeSignupRequired", ChannelRequiredError),
    (401, "authError", AuthRequiredError),
    (403, "forbidden", ForbiddenError),
])
def test_safe_error_mapping_and_retry_policy(status, reason, expected):
    calls = []

    def response(request):
        calls.append(request)
        return httpx.Response(status, json={
            "error": {"message": "upstream sensitive text", "errors": [{"reason": reason}]},
        })

    provider, quota = live(response)
    with pytest.raises(expected) as error:
        provider.get_videos(["Fixture0001"])
    assert "sensitive" not in str(error.value)
    expected_calls = 2 if expected is RateLimitedError else 1
    assert len(calls) == expected_calls
    remaining = 0 if expected is QuotaExceededError else 10_000 - expected_calls
    assert quota.status().general_remaining == remaining


def test_pacific_reset_and_persisted_separate_buckets(tmp_path):
    path = tmp_path / "quota.sqlite"
    clock = Clock()
    primary = QuotaManager(QuotaLedger(path), clock)
    secondary = QuotaManager(QuotaLedger(path), clock)
    primary.record(primary.cost_of("videos.insert"))
    primary.record(primary.cost_of("search.list"))
    primary.record(primary.cost_of("playlistItems.insert", calls=2))
    status = secondary.status()
    assert (status.general_remaining, status.search_remaining, status.videos_insert_remaining) == (
        9900, 99, 99,
    )
    clock.value += timedelta(minutes=1)
    assert secondary.status().general_remaining == 10_000
    with pytest.raises(UnknownCostError):
        primary.cost_of("unknown.list")
    with pytest.raises(UnknownCostError):
        primary.check(QuotaCost(general=-1))


def test_cache_hits_expiry_and_library_bypass():
    path = Path(__file__).parents[1] / "fixtures" / "provider.json"
    fixture = FixtureProvider.from_json(path)
    clock = Clock()
    provider = CachingProvider(fixture, clock=clock)
    assert provider.get_videos(["Fixture0001"])[0].duration_s == 180
    provider.get_videos(["Fixture0001", "Fixture0002"])
    assert fixture.calls[-1] == ("get_videos", ("Fixture0002",))
    clock.value += timedelta(hours=24)
    provider.get_videos(["Fixture0001"])
    assert fixture.calls[-1] == ("get_videos", ("Fixture0001",))
    assert provider.get_library() == provider.get_library()
    assert fixture.calls[-2:] == [("get_library",), ("get_library",)]


def test_read_only_provider_rejects_writes_before_transport():
    provider, quota = live(lambda _: pytest.fail("Unexpected HTTP call"), read_only=True)
    with pytest.raises(ForbiddenError):
        provider.create_playlist("Fixture")
    assert quota.status().general_remaining == 10_000


def test_fixture_supports_typed_failures_and_tracks_attempted_calls():
    fixture = FixtureProvider(errors={"get_library": AuthRequiredError("Fixture expired.")})
    with pytest.raises(AuthRequiredError):
        fixture.get_library()
    assert fixture.calls == [("get_library",)]
