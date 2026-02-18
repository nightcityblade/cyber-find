"""
Utility functions for CyberFind
"""

import hashlib
import re
from typing import Any, Dict, List, Optional
from urllib.parse import quote, urlparse


def is_valid_email(email: str) -> bool:
    """Validate email format"""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def is_valid_phone(phone: str) -> bool:
    """Validate phone number format (E.164)"""
    pattern = r"^\+?[1-9]\d{1,14}$"
    return bool(re.match(pattern, phone))


def is_valid_username(username: str) -> bool:
    """Validate username format"""
    if not username or len(username) < 2 or len(username) > 50:
        return False
    pattern = r"^[a-zA-Z0-9._-]+$"
    return bool(re.match(pattern, username))


def is_valid_url(url: str) -> bool:
    """Validate URL format"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def normalize_username(username: str) -> str:
    """Normalize username for searching"""
    return username.strip().lower()


def normalize_email(email: str) -> str:
    """Normalize email for searching"""
    return email.strip().lower()


def normalize_phone(phone: str) -> str:
    """Normalize phone number for searching"""
    return re.sub(r"[^\d+]", "", phone)


def email_to_hash(email: str) -> str:
    """Convert email to MD5 hash for gravatar-style lookups"""
    return hashlib.md5(email.lower().encode("utf-8"), usedforsecurity=False).hexdigest()


def format_url(base_url: str, username: str) -> str:
    """Format URL with username placeholder or regex pattern.

    Supports two modes:
    - Standard: replaces ``{username}`` in the URL template.
    - Regex: if *base_url* starts with ``regex:``, the remainder is
      treated as a regex pattern.  The escaped username is inserted in
      place of the first capture group (if present) or appended, and
      the resulting string is returned as-is (useful for complex URL
      schemes).

    Args:
        base_url: URL template, optionally prefixed with ``regex:``.
        username: The username to insert.

    Returns:
        Formatted URL string.
    """
    if base_url.startswith("regex:"):
        pattern = base_url[len("regex:") :]
        escaped_username = re.escape(username)
        # Replace the first capture group placeholder with the escaped username
        if "(" in pattern and ")" in pattern:
            # Replace the first capture group with the literal escaped username
            result = re.sub(r"\([^)]*\)", escaped_username, pattern, count=1)
        else:
            result = pattern + escaped_username
        return result
    return base_url.replace("{username}", quote(username, safe=""))


def extract_domain(url: str) -> Optional[str]:
    """Extract domain from URL"""
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except Exception:
        return None


def get_username_from_url(url: str) -> Optional[str]:
    """Try to extract username from URL"""
    try:
        # Common patterns
        patterns = [
            r"(?:\/|%2F)([a-zA-Z0-9._-]+)(?:\/|$)",
            r"(?:user=|username=)([a-zA-Z0-9._-]+)",
            r"(?:@)([a-zA-Z0-9._-]+)(?:\.|\/|$)",
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    except Exception:
        return None


def sanitize_output(text: str, max_length: int = 1000) -> str:
    """Sanitize text for output"""
    if not text:
        return ""
    # Remove control characters
    text = "".join(char for char in text if ord(char) >= 32 or char in "\n\t\r")
    # Limit length
    return text[:max_length]


def format_size(size_bytes: int) -> str:
    """Format bytes to human-readable size"""
    size = float(size_bytes)
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.2f}{unit}"
        size /= 1024
    return f"{size:.2f}TB"


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable format"""
    if seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        return f"{seconds / 60:.2f}m"
    else:
        return f"{seconds / 3600:.2f}h"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def split_urls(urls: str) -> List[str]:
    """Split multiple URLs by common delimiters"""
    # Split by comma, newline, or semicolon
    parts = re.split(r"[,\n;]", urls)
    return [url.strip() for url in parts if url.strip()]


def combine_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Combine multiple search results"""
    combined: Dict[str, Any] = {
        "total_found": 0,
        "total_errors": 0,
        "accounts": [],
        "errors": [],
    }

    for result in results:
        if result.get("status") == "found":
            combined["total_found"] = combined["total_found"] + 1
            combined["accounts"].append(result)
        elif result.get("error"):
            combined["total_errors"] = combined["total_errors"] + 1
            combined["errors"].append(result)

    return combined
