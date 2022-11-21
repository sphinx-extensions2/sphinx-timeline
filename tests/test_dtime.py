import pytest

from sphinx_timeline import dtime


@pytest.mark.parametrize(
    "start,duration,kwargs,expected",
    [
        ("2021-02-03 22:00", "", {}, "Wed 3rd Feb 2021, 10:00 PM (UTC)"),
        ("2021-02-03", "", {"day_name": False}, "3rd Feb 2021"),
        ("2021-02-03", "", {"abbr": False}, "Wednesday 3rd February 2021"),
        ("2021-02-03", "", {"short_date": True}, "Wed 03/02/2021"),
        ("2021-02-03", "", {"short_date": True, "short_delim": "-"}, "Wed 03-02-2021"),
        ("2021-02-03 22:00", "", {"clock12": False}, "Wed 3rd Feb 2021, 22:00 (UTC)"),
        ("2021-02-03", "1 day", {}, "Wed 3rd - Thu 4th Feb 2021"),
        ("2021-02-03", "1 month", {}, "Wed 3rd Feb - Wed 3rd Mar 2021"),
        ("2021-02-03", "1 year", {}, "Wed 3rd Feb 2021 - Thu 3rd Feb 2022"),
        (
            "2021-02-03 22:00",
            "1 day",
            {},
            "Wed 3rd, 10:00 PM - Thu 4th Feb 2021, 10:00 PM (UTC)",
        ),
        (
            "2021-02-03 22:00",
            "1 year",
            {},
            "Wed 3rd Feb 2021, 10:00 PM - Thu 3rd Feb 2022, 10:00 PM (UTC)",
        ),
        (
            "2021-02-03 22:00",
            "1 hour 1min",
            {},
            "Wed 3rd Feb 2021, 10:00 PM - 11:01 PM (UTC)",
        ),
    ],
)
def test_fmt_daterange(start, duration, kwargs, expected):
    """Test formatting of date range."""
    dt = dtime.to_datetime(start)
    rng = dtime.parse_duration(duration)
    assert dtime.fmt_daterange(dt, rng, **kwargs) == expected
