import pytest

from unprompted.durations import describe_duration, format_clock, parse_duration


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("30s", 30),
        ("30 s", 30),
        ("45 sec", 45),
        ("5m", 300),
        ("5 min", 300),
        ("5", 300),
        ("  2M ", 120),
        ("90S", 90),
    ],
)
def test_parse_duration_accepts_valid_formats(text, expected):
    assert parse_duration(text) == expected


@pytest.mark.parametrize("text", ["", "abc", "-5", "1.5", "5h", "m", "5 minutes"])
def test_parse_duration_rejects_invalid_formats(text):
    with pytest.raises(ValueError):
        parse_duration(text)


def test_describe_duration():
    assert describe_duration(300) == "5 min"
    assert describe_duration(15) == "15 s"
    assert describe_duration(90) == "90 s"


def test_format_clock():
    assert format_clock(0) == "00:00"
    assert format_clock(65) == "01:05"
    assert format_clock(3600) == "60:00"
    assert format_clock(-4) == "00:00"
