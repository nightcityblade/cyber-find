"""
Unit tests for utils module
"""

import pytest

from cyber_find.utils import (
    combine_results,
    format_duration,
    format_size,
    format_url,
    is_valid_email,
    is_valid_phone,
    is_valid_username,
    split_urls,
    truncate_text,
)


@pytest.mark.unit
class TestValidationFunctions:
    """Test validation utility functions"""

    def test_is_valid_email_valid(self):
        """Test valid email addresses"""
        assert is_valid_email("test@example.com") is True
        assert is_valid_email("user.name@domain.co.uk") is True
        assert is_valid_email("user+tag@example.com") is True

    def test_is_valid_email_invalid(self):
        """Test invalid email addresses"""
        assert is_valid_email("not-an-email") is False
        assert is_valid_email("@example.com") is False
        assert is_valid_email("test@") is False
        assert is_valid_email("") is False

    def test_is_valid_phone_valid(self):
        """Test valid phone numbers"""
        assert is_valid_phone("+1234567890") is True
        assert is_valid_phone("1234567890") is True

    def test_is_valid_phone_invalid(self):
        """Test invalid phone numbers"""
        assert is_valid_phone("abc") is False
        assert is_valid_phone("+") is False
        assert is_valid_phone("") is False

    def test_is_valid_username_valid(self):
        """Test valid usernames"""
        assert is_valid_username("testuser") is True
        assert is_valid_username("user.name") is True
        assert is_valid_username("user_name") is True
        assert is_valid_username("user-name") is True

    def test_is_valid_username_invalid(self):
        """Test invalid usernames"""
        assert is_valid_username("") is False
        assert is_valid_username("a") is False  # Too short
        assert is_valid_username("a" * 51) is False  # Too long
        assert is_valid_username("user@name") is False  # Invalid character


@pytest.mark.unit
class TestFormatFunctions:
    """Test formatting utility functions"""

    def test_format_size_bytes(self):
        """Test format_size with bytes"""
        assert "B" in format_size(100)

    def test_format_size_kilobytes(self):
        """Test format_size with kilobytes"""
        result = format_size(1024)
        assert "KB" in result or "MB" in result

    def test_format_size_megabytes(self):
        """Test format_size with megabytes"""
        result = format_size(1024 * 1024)
        assert "MB" in result or "GB" in result

    def test_format_duration_seconds(self):
        """Test format_duration with seconds"""
        assert "s" in format_duration(30)

    def test_format_duration_minutes(self):
        """Test format_duration with minutes"""
        assert "m" in format_duration(90)

    def test_format_duration_hours(self):
        """Test format_duration with hours"""
        assert "h" in format_duration(3600)

    def test_truncate_text_short(self):
        """Test truncate_text with short text"""
        text = "Short text"
        assert truncate_text(text, max_length=100) == text

    def test_truncate_text_long(self):
        """Test truncate_text with long text"""
        text = "A" * 200
        result = truncate_text(text, max_length=50)
        assert len(result) <= 53  # 50 + "..."
        assert result.endswith("...")

    def test_truncate_text_custom_suffix(self):
        """Test truncate_text with custom suffix"""
        text = "A" * 200
        result = truncate_text(text, max_length=50, suffix=" [more]")
        assert result.endswith(" [more]")


@pytest.mark.unit
class TestUrlFunctions:
    """Test URL utility functions"""

    def test_split_urls_comma(self):
        """Test split_urls with comma separator"""
        urls = "https://example.com, https://test.com"
        result = split_urls(urls)
        assert len(result) == 2
        assert "https://example.com" in result

    def test_split_urls_newline(self):
        """Test split_urls with newline separator"""
        urls = "https://example.com\nhttps://test.com"
        result = split_urls(urls)
        assert len(result) == 2

    def test_split_urls_semicolon(self):
        """Test split_urls with semicolon separator"""
        urls = "https://example.com; https://test.com"
        result = split_urls(urls)
        assert len(result) == 2

    def test_split_urls_empty(self):
        """Test split_urls with empty string"""
        result = split_urls("")
        assert result == []

    def test_split_urls_whitespace(self):
        """Test split_urls trims whitespace"""
        urls = "  https://example.com  ,  https://test.com  "
        result = split_urls(urls)
        assert "https://example.com" in result
        assert "  " not in result[0]


@pytest.mark.unit
class TestCombineResults:
    """Test combine_results function"""

    def test_combine_results_empty(self):
        """Test combine_results with empty list"""
        result = combine_results([])
        assert result["total_found"] == 0
        assert result["total_errors"] == 0
        assert result["accounts"] == []
        assert result["errors"] == []

    def test_combine_results_found(self):
        """Test combine_results with found results"""
        results = [
            {"status": "found", "url": "https://example.com"},
            {"status": "found", "url": "https://test.com"},
        ]
        result = combine_results(results)
        assert result["total_found"] == 2
        assert len(result["accounts"]) == 2

    def test_combine_results_errors(self):
        """Test combine_results with error results"""
        results = [
            {"error": "Connection failed"},
            {"error": "Timeout"},
        ]
        result = combine_results(results)
        assert result["total_errors"] == 2
        assert len(result["errors"]) == 2

    def test_combine_results_mixed(self):
        """Test combine_results with mixed results"""
        results = [
            {"status": "found", "url": "https://example.com"},
            {"error": "Connection failed"},
            {"status": "not_found"},
        ]
        result = combine_results(results)
        assert result["total_found"] == 1
        assert result["total_errors"] == 1


@pytest.mark.unit
class TestFormatUrl:
    """Test format_url with standard and regex patterns"""

    def test_standard_substitution(self):
        """Standard {username} replacement still works"""
        url = format_url("https://github.com/{username}", "john_doe")
        assert url == "https://github.com/john_doe"

    def test_standard_special_chars_encoded(self):
        """Special characters are percent-encoded in standard mode"""
        url = format_url("https://example.com/{username}", "user name")
        assert "user%20name" in url

    def test_regex_with_capture_group(self):
        """Regex mode replaces capture group with escaped username"""
        url = format_url(r"regex:https://site\.com/u/([a-z0-9_]+)/profile", "john_doe")
        assert url == r"https://site\.com/u/john_doe/profile"

    def test_regex_escapes_username(self):
        """Username with regex metacharacters is escaped in regex mode"""
        url = format_url(r"regex:https://site\.com/u/([a-z0-9_.]+)/profile", "user.name")
        assert r"user\.name" in url

    def test_regex_no_capture_group(self):
        """Regex mode without capture group appends username"""
        url = format_url(r"regex:https://site\.com/search?q=", "testuser")
        assert url == r"https://site\.com/search?q=testuser"

    def test_regex_preserves_standard_urls(self):
        """Non-regex URLs are unaffected even if they contain 'regex' elsewhere"""
        url = format_url("https://regex.example.com/{username}", "alice")
        assert url == "https://regex.example.com/alice"
