from pathlib import Path

import pytest

from youtube_mcp.errors import OverBudgetError, UnavailableError, ValidationError
from youtube_mcp.providers.fixture import FixtureProvider
from youtube_mcp.quota.ledger import QuotaLedger
from youtube_mcp.quota.manager import QuotaManager
from youtube_mcp.server import video_details


@pytest.fixture
def provider():
    return FixtureProvider.from_json(Path(__file__).parents[1] / "fixtures" / "provider.json")


def test_over_budget_tool_makes_zero_provider_calls(provider):
    quota = QuotaManager(QuotaLedger(), general=0)
    with pytest.raises(OverBudgetError):
        video_details(provider, quota, "Fixture0001")
    assert provider.calls == []


def test_malformed_tool_input_makes_zero_provider_calls(provider):
    quota = QuotaManager(QuotaLedger())
    with pytest.raises(ValidationError):
        video_details(provider, quota, "https://example.org/watch?v=Fixture0001")
    assert provider.calls == []


@pytest.mark.parametrize("ref", [
    "Fixture0001", "https://www.youtube.com/watch?v=Fixture0001",
    "https://youtu.be/Fixture0001?si=synthetic", "https://youtube.com/shorts/Fixture0001",
])
def test_known_video_formats_resolve(provider, ref):
    quota = QuotaManager(QuotaLedger())
    assert video_details(provider, quota, ref).video_id == "Fixture0001"


def test_private_or_deleted_video_is_unavailable(provider):
    quota = QuotaManager(QuotaLedger())
    with pytest.raises(UnavailableError):
        video_details(provider, quota, "Fixture9999")
