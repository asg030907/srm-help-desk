"""
technicians.py
Loads the campus technician roster used by the Dispatch Agent. Backed
by a plain JSON file (data/technicians.json) rather than a database
table, since the roster changes rarely and is meant to be hand-edited.
"""

from src.utils.config import get_settings
from src.utils.helpers import load_json_file


def list_technicians() -> list[dict]:
    settings = get_settings()
    return load_json_file(settings.technicians_path, default=[])
