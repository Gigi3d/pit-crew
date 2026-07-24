"""The frozen bay contract. Everything speaks this shape: the runner produces
it, the UI renders it, telemetry logs it. See BUILD.md section 3.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Optional


@dataclass
class BayResult:
    bay: int
    strategy: str
    state: str                     # queued | run | done | dq
    legal: bool
    baseline_ms: Optional[float] = None
    candidate_ms: Optional[float] = None
    ratio: Optional[float] = None  # candidate_ms / baseline_ms; lower is faster
    tests_passed: int = 0
    tests_total: int = 0
    error: Optional[str] = None

    @property
    def speedup(self) -> Optional[float]:
        if self.ratio and self.ratio > 0:
            return 1.0 / self.ratio
        return None

    def to_dict(self) -> dict:
        d = asdict(self)
        d["speedup"] = self.speedup
        return d


def dq(bay: int, strategy: str, error: str,
       tests_passed: int = 0, tests_total: int = 0) -> BayResult:
    """A disqualified bay: broke tests, or touched a forbidden path."""
    return BayResult(
        bay=bay, strategy=strategy, state="dq", legal=False,
        tests_passed=tests_passed, tests_total=tests_total, error=error,
    )
