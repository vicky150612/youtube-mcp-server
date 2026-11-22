import dataclasses
from datetime import UTC, date, datetime

import pytest

import youtube_mcp.models as models
from youtube_mcp.models import (
    AuthStatus,
    Channel,
    ConstraintCheck,
    CreatedPlaylist,
    DurationBucket,
    EngagementReport,
    Filters,
    Library,
    LikedVideo,
    Period,
    PeriodSummary,
    PlaylistConstraints,
    PlaylistItem,
    PlaylistProposal,
    QuotaCost,
    QuotaStatus,
    RankedEntry,
    ScoredChannel,
    ScoredVideo,
    SourceCounts,
    Subscription,
    TrendPoint,
    UserPlaylist,
    Video,
)

NOW = datetime(2026, 11, 22, 12, 0, tzinfo=UTC)


def make_video(**overrides):
    fields = {"video_id": "abcdefghijk", "title": "Intro to OS", "channel_id": "UC" + "x" * 22}
    fields.update(overrides)
    return Video(**fields)


def make_proposal(**overrides):
    fields = {
        "proposal_id": "p" * 32,
        "digest": "0" * 64,
        "owner": "fingerprint",
        "constraints": PlaylistConstraints(topic="os", total_duration_s=3600, max_video_s=600),
        "videos": (make_video(duration_s=600),),
        "total_duration_s": 600,
        "checks": (ConstraintCheck("max_video_length", True, "all <= 600 s"),),
        "unknown_language": (),
        "write_cost": 100,
        "expires_at": NOW,
    }
    fields.update(overrides)
    return PlaylistProposal(**fields)


def test_every_exported_model_is_a_frozen_dataclass():
    exported = [getattr(models, name) for name in models.__all__]
    classes = [obj for obj in exported if isinstance(obj, type) and dataclasses.is_dataclass(obj)]
    assert len(classes) == 24
    for cls in classes:
        assert cls.__dataclass_params__.frozen, cls.__name__


def test_video_unknown_optionals_default_to_none_not_zero_or_empty():
    video = make_video()
    assert video.tags == ()
    assert video.available is True
    for name in ("description", "duration_s", "category_id", "language", "published_at", "channel_title"):
        assert getattr(video, name) is None, name


def test_channel_hidden_statistics_default_to_none():
    channel = Channel(channel_id="UC" + "y" * 22, title="OS Channel")
    assert channel.subscriber_count is None
    assert channel.video_count is None
    assert channel.topics == () and channel.keywords == () and channel.recent_uploads == ()


def test_models_are_immutable():
    video = make_video()
    with pytest.raises(dataclasses.FrozenInstanceError):
        video.title = "changed"  # type: ignore[misc]
    proposal = make_proposal()
    with pytest.raises(dataclasses.FrozenInstanceError):
        proposal.videos = ()  # type: ignore[misc]


def test_equal_content_gives_equal_and_hashable_models():
    assert make_video(tags=("os", "linux")) == make_video(tags=("os", "linux"))
    assert hash(make_proposal()) == hash(make_proposal())


def test_playlist_constraint_defaults_follow_srs():
    constraints = PlaylistConstraints(topic="os", total_duration_s=7200, max_video_s=1200)
    assert constraints.privacy == "private"
    assert constraints.allow_unknown_language is False
    assert constraints.tolerance == pytest.approx(0.10)
    assert constraints.language is None


def test_library_keeps_sources_separate_and_unknown_timestamps():
    video = make_video()
    library = Library(
        liked=(LikedVideo(video=video, added_at=None),),
        subscriptions=(Subscription(channel_id="UC" + "z" * 22, channel_title="Z", subscribed_at=NOW),),
        playlists=(UserPlaylist(playlist_id="PL1", title="Mine", item_count=None),),
        playlist_items=(PlaylistItem(playlist_id="PL1", video=video, added_at=NOW),),
    )
    assert library.liked[0].added_at is None
    assert library.playlists[0].item_count is None
    assert len(library.subscriptions) == len(library.playlist_items) == 1


def test_engagement_report_shape():
    counts = SourceCounts(likes=2, subscriptions=1, playlist_items=3)
    summary = PeriodSummary(
        period=None,
        totals=counts,
        top_channels=(RankedEntry(key="UC" + "z" * 22, label="Z", distinct_items=4, sources=counts),),
        top_categories=(),
        duration_buckets=DurationBucket(short_count=1, medium_count=2, long_count=0, unknown_count=1),
        trend=(TrendPoint(month="2026-11", sources=counts), TrendPoint(month=None, sources=counts)),
    )
    report = EngagementReport(overall=summary, periods=(), comparison=None, definition="...")
    assert report.overall.trend[-1].month is None
    assert Period(start=date(2026, 1, 1), end=date(2026, 1, 31)).end.day == 31


def test_small_value_models():
    assert QuotaCost() == QuotaCost(general=0, search=0)
    assert QuotaStatus(general_remaining=10_000, search_remaining=100, resets_at=NOW).search_remaining == 100
    assert Filters() == Filters(max_duration_s=None, language=None)
    assert AuthStatus(state="needs_authorisation", scopes=()).scopes == ()
    assert ScoredVideo(video=make_video(), score=0.5, reason="r").score == 0.5
    assert ScoredChannel(channel=Channel(channel_id="UC" + "y" * 22, title="t"), score=1.0, reason="r").reason == "r"
    created = CreatedPlaylist(playlist_id="PL1", url="https://www.youtube.com/playlist?list=PL1", added=("a",), failed=())
    assert created.failed == ()
