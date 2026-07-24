"""Where the 30 candidate patches come from.

MockPatchProvider: pre-written patches, no key, runs today.
FireworksPatchProvider: the real thing, one call per bay. Written but not run here
because it needs FIREWORKS_API_KEY. The race code does not care which one it holds.
"""
from __future__ import annotations

import os
from typing import Protocol

from . import candidates_mock


class PatchProvider(Protocol):
    def get(self, bay: int, strategy_hint: str, source: str) -> dict:
        """Return {"strategy": str, "files": {relpath: new_source}}."""
        ...


class MockPatchProvider:
    mode = "mock"

    def get(self, bay: int, strategy_hint: str = "", source: str = "") -> dict:
        return candidates_mock.candidate_for(bay)


PATCH_SYSTEM = (
    "You optimise one Python function for speed without changing its behaviour. "
    "Return ONLY the full new source of app/events.py, no prose, no fences. "
    "You may not edit tests or the benchmark."
)


class FireworksPatchProvider:
    """Friday swap. One chat completion per bay, seeded with a distinct strategy.

    Needs FIREWORKS_API_KEY and `pip install --pre fireworks-ai`. Kept import-lazy
    so this module loads with no key and no SDK.
    """
    mode = "fireworks"
    model = "accounts/fireworks/models/deepseek-v3p1"

    def __init__(self):
        if not os.environ.get("FIREWORKS_API_KEY"):
            raise RuntimeError("FIREWORKS_API_KEY is not set")
        from fireworks import Fireworks  # lazy: only needed in real mode
        self._client = Fireworks()

    def get(self, bay: int, strategy_hint: str, source: str) -> dict:
        prompt = (
            f"Strategy for this attempt: {strategy_hint}.\n\n"
            f"Here is app/events.py:\n\n{source}\n\n"
            "Return the full optimised file."
        )
        r = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": PATCH_SYSTEM},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )
        new_source = _strip_fences(r.choices[0].message.content)
        return {"strategy": strategy_hint, "files": {"app/events.py": new_source}}


def _strip_fences(text: str) -> str:
    t = text.strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[1] if "\n" in t else t
        if t.rstrip().endswith("```"):
            t = t.rstrip()[:-3]
    return t.strip() + "\n"
