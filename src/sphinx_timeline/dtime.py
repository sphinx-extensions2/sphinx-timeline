"""Utilities for parsing and formatting dates and times."""
from __future__ import annotations

from datetime import date, datetime, time, timezone
import re

from dateutil.relativedelta import relativedelta

try:
    import zoneinfo
except ImportError:
    from backports import zoneinfo  # noqa: F401


RE_ISO_TZ = re.compile(r"(?P<dt>.+)\((?P<tz>[^)]+)\)\s*$")


def to_datetime(value: str | date | datetime, default_tz=timezone.utc) -> datetime:
    """Convert to a timezone-aware datetime object."""
    final: datetime
    if isinstance(value, str):
        # find timezone name suffix in parentheses
        tz_match = RE_ISO_TZ.match(value)
        if tz_match:
            # parse datetime with timezone
            final = datetime.fromisoformat(tz_match.group("dt").strip())
            try:
                tz = zoneinfo.ZoneInfo(tz_match.group("tz"))
            except Exception as exc:
                raise ValueError(f"Invalid timezone: {tz_match.group('tz')!r}: {exc}")
            final = final.replace(tzinfo=tz)
        else:
            # parse datetime without timezone
            final = datetime.fromisoformat(value.strip())
    elif isinstance(value, date):
        final = datetime(value.year, value.month, value.day)
    elif not isinstance(value, datetime):
        raise TypeError(f"invalid type: {type(value)}")
    # if not timezone aware, assume UTC
    if final.tzinfo is None:
        final = final.replace(tzinfo=default_tz)
    return final


def parse_duration(value: str) -> relativedelta:
    """Parse a duration string."""
    if not isinstance(value, str):
        raise TypeError(f"not str: {type(value)}")
    delta = {}
    if year_match := re.search(r"(\d+)\s?y", value):
        delta["years"] = int(year_match.group(1))
    if month_match := re.search(r"(\d+)\s?mon", value):
        delta["months"] = int(month_match.group(1))
    if day_match := re.search(r"(\d+)\s?d", value):
        delta["days"] = int(day_match.group(1))
    if hour_match := re.search(r"(\d+)\s?h", value):
        delta["hours"] = int(hour_match.group(1))
    if minute_match := re.search(r"(\d+)\s?min", value):
        delta["minutes"] = int(minute_match.group(1))
    if second_match := re.search(r"(\d+)\s?s", value):
        delta["seconds"] = int(second_match.group(1))
    return relativedelta(**delta)


def fmt_daterange(
    start: datetime,
    duration: relativedelta | None = None,
    *,
    day_name=True,
    short_date=False,
    short_delim="/",
    abbr=True,
    clock12=True,
) -> str:
    """Format a datetime span.

    :param start: start datetime
    :param duration: duration of span
    :param day_name: include day name (e.g. "Monday")
    :param short_date: use short date format (e.g. "01/01/2021")
    :param short_delim: delimiter for short date format
    :param abbr: use abbreviated day/month name (e.g. "Mon")
    :param clock12: use AM/PM time format
    """
    day_name_code = ("%a " if abbr else "%A ") if day_name else ""
    day_code = f"%d{short_delim}" if short_date else "%D "
    month_code = f"%m{short_delim}" if short_date else ("%b " if abbr else "%B ")
    time_code = "%I:%M %p" if clock12 else "%H:%M"
    tz_code = " (%Z)" if start.tzinfo else ""

    start_fmt = f"{day_name_code}{day_code}{month_code}%Y, {time_code}{tz_code}"
    end_fmt = f"{day_name_code}{day_code}{month_code}%Y, {time_code}{tz_code}"

    if duration is None:
        end = start
    else:
        end = start + duration

    if start == end:
        if start.time() == time(0):
            # remove time from start format
            start_fmt = start_fmt.split(",")[0]
        return fmt_datetime(start, start_fmt)

    # remove timezone from start format
    start_fmt = start_fmt.replace(tz_code, "")

    if start.date() == end.date():
        # remove date from end format
        end_fmt = end_fmt.split(",")[1].lstrip()
        return f"{fmt_datetime(start, start_fmt)} - {fmt_datetime(end, end_fmt)}"

    # assume if the start time is 00:00:00, it was set without a time
    if start.time() == time(0) and start.time() == end.time():
        # remove time from start and end format
        start_fmt = start_fmt.split(",")[0]
        end_fmt = end_fmt.split(",")[0]

    if not short_date and start.year == end.year:
        start_fmt = start_fmt.replace(" %Y", "")
        if start.month == end.month:
            start_fmt = start_fmt.replace(f"{month_code}", "")

    return f"{fmt_datetime(start, start_fmt)} - {fmt_datetime(end, end_fmt)}"


def _ord_suffix(n: int):
    """Return ordinal suffix for a number."""
    return (
        "th" if 11 <= (n % 100) <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    )


def fmt_datetime(dt: datetime, fmt: str) -> str:
    """Format a datetime.

    Extended strftime codes:
    - %D: day number with ordinal suffix (e.g. 1st, 2nd, 3rd, 4th, etc.)
    """
    # TODO deal with locales (for day names, month names, etc.)
    fmt = fmt.replace("%D", str(dt.day) + _ord_suffix(dt.day))
    return dt.strftime(fmt)


def fmt_delta(delta: relativedelta | None) -> str:
    """Format a relativedelta object."""
    if delta is None:
        return ""

    string = []

    if delta.years:
        string.append(f"{delta.years} Year{_s(delta.years)}")
    if delta.months:
        string.append(f"{delta.months} Month{_s(delta.months)}")
    if delta.days:
        string.append(f"{delta.days} Day{_s(delta.days)}")
    if delta.hours:
        string.append(f"{delta.hours} Hour{_s(delta.hours)}")
    if delta.minutes:
        string.append(f"{delta.minutes} Minute{_s(delta.minutes)}")
    if delta.seconds:
        string.append(f"{delta.seconds} Second{_s(delta.seconds)}")
    return " ".join(string)


def _s(n: int):
    """Return "s" if number is not 1."""
    return "s" if n != 1 else ""


class DtRangeStr:
    """A datetime range string format."""

    def __init__(self, start: datetime, duration: relativedelta | None = None) -> None:
        self._start = start
        self._duration = duration
        self._default = fmt_daterange(start, duration)

    def __str__(self) -> str:
        return self._default

    def __call__(self, **kwargs) -> str:
        return fmt_daterange(self._start, self._duration, **kwargs)
