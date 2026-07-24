"""The anti-cheat gate. A patch may only touch source under app/. Any attempt
to edit the tests, the benchmark harness, or CI config is rejected before the
patch is ever scored. This is the ten lines that stop an agent from deleting an
assertion and reporting a 400x win.
"""
from __future__ import annotations

from typing import Iterable, Optional, Tuple

ALLOWED_PREFIX = "app/"


def check_paths(paths: Iterable[str]) -> Tuple[bool, Optional[str]]:
    """Return (legal, reason). Legal iff every path is under app/."""
    for p in paths:
        norm = p.replace("\\", "/").lstrip("./")
        if ".." in norm.split("/"):
            return False, f"path escapes the repo: {p}"
        if not norm.startswith(ALLOWED_PREFIX):
            return False, f"patch touches a forbidden path: {p}"
    return True, None
