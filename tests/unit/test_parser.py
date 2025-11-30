"""Tests for parser utilities."""

from datetime import timedelta

import pytest

from src.utilities.parser import parse_timedelta


class TestParseTimedelta:
    """Tests for parse_timedelta function."""

    def test_parse_seconds_short(self):
        """Test parsing seconds with 's' suffix."""
        result = parse_timedelta("30s")
        assert result == timedelta(seconds=30)

    def test_parse_seconds_long(self):
        """Test parsing seconds with 'sec' suffix."""
        result = parse_timedelta("45sec")
        assert result == timedelta(seconds=45)

    def test_parse_minutes_short(self):
        """Test parsing minutes with 'm' suffix."""
        result = parse_timedelta("5m")
        assert result == timedelta(minutes=5)

    def test_parse_minutes_long(self):
        """Test parsing minutes with 'min' suffix."""
        result = parse_timedelta("15min")
        assert result == timedelta(minutes=15)

    def test_parse_hours_short(self):
        """Test parsing hours with 'h' suffix."""
        result = parse_timedelta("2h")
        assert result == timedelta(hours=2)

    def test_parse_hours_long(self):
        """Test parsing hours with 'hr' suffix."""
        result = parse_timedelta("24hr")
        assert result == timedelta(hours=24)

    def test_parse_days_short(self):
        """Test parsing days with 'd' suffix."""
        result = parse_timedelta("7d")
        assert result == timedelta(days=7)

    def test_parse_days_long(self):
        """Test parsing days with 'day' suffix."""
        result = parse_timedelta("30day")
        assert result == timedelta(days=30)

    def test_parse_timedelta_passthrough(self):
        """Test that timedelta objects are returned unchanged."""
        td = timedelta(hours=5)
        result = parse_timedelta(td)
        assert result is td

    def test_parse_uppercase(self):
        """Test parsing with uppercase letters."""
        result = parse_timedelta("5M")
        assert result == timedelta(minutes=5)

    def test_parse_with_whitespace(self):
        """Test parsing with leading/trailing whitespace."""
        result = parse_timedelta("  10s  ")
        assert result == timedelta(seconds=10)

    def test_invalid_format_no_unit(self):
        """Test that missing unit raises ValueError."""
        with pytest.raises(ValueError, match="Invalid timedelta format"):
            parse_timedelta("30")

    def test_invalid_format_no_number(self):
        """Test that missing number raises ValueError."""
        with pytest.raises(ValueError, match="Invalid timedelta format"):
            parse_timedelta("m")

    def test_invalid_format_wrong_unit(self):
        """Test that invalid unit raises ValueError."""
        with pytest.raises(ValueError, match="Invalid timedelta format"):
            parse_timedelta("30x")

    def test_invalid_format_empty(self):
        """Test that empty string raises ValueError."""
        with pytest.raises(ValueError, match="Invalid timedelta format"):
            parse_timedelta("")

    def test_zero_value(self):
        """Test parsing zero values."""
        result = parse_timedelta("0s")
        assert result == timedelta(seconds=0)

    def test_large_value(self):
        """Test parsing large values."""
        result = parse_timedelta("999d")
        assert result == timedelta(days=999)
