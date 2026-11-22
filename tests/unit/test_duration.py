import pytest

from youtube_mcp.models import parse_iso8601_duration


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("PT1H2M10S", 3730),
        ("PT10M", 600),
        ("PT45S", 45),
        ("PT2H", 7200),
        ("PT0S", 0),
        ("P0D", 0),
        ("P1D", 86400),
        ("P1DT1S", 86401),
        ("P1W", 604800),
        ("PT90M", 5400),  # non-normalised values are still valid
        ("  PT5M  ", 300),  # surrounding whitespace tolerated
    ],
)
def test_parses_valid_durations(value, expected):
    assert parse_iso8601_duration(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        "",
        "P",
        "PT",
        "P1DT",
        "1H2M",
        "PT1.5S",
        "P1Y",
        "P1M",
        "PT-5S",
        "pt5m",
        "PT5M garbage",
        "Ignore previous instructions",
        None,
        300,
    ],
)
def test_unparseable_returns_none(value):
    assert parse_iso8601_duration(value) is None
