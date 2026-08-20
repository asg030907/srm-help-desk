"""
helpers.py
Small, dependency-free utility functions used across the codebase.
"""

import json
import re
import uuid
from pathlib import Path
from typing import Any


def new_id(prefix: str = "id") -> str:
    """Generate a short, prefixed unique identifier (e.g. 'session-3f9a1c2b')."""
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def truncate(text: str, max_len: int = 500) -> str:
    """Truncate text to max_len characters, appending an ellipsis if cut."""
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "…"


def safe_json_loads(raw: str, default: Any = None) -> Any:
    """Parse JSON, returning `default` instead of raising on malformed input."""
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return default


def load_json_file(path: str | Path, default: Any = None) -> Any:
    """Load a JSON file, returning `default` if it doesn't exist or fails to parse."""
    p = Path(path)
    if not p.exists():
        return default
    return safe_json_loads(p.read_text(encoding="utf-8"), default=default)


def strip_extra_whitespace(text: str) -> str:
    """Collapse repeated whitespace/newlines into single spaces and trim."""
    return re.sub(r"\s+", " ", text).strip()
