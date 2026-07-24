"""Per-bay telemetry. NullTelemetry does nothing and needs no key, so the race
runs today. BraintrustTelemetry is the Friday swap.
"""
from __future__ import annotations

import os

from .contracts import BayResult


class NullTelemetry:
    mode = "null"

    def log(self, result: BayResult) -> None:
        pass


class BraintrustTelemetry:
    """Friday swap. One scored span per bay. Needs BRAINTRUST_API_KEY.

    Score convention: legal winners score by speedup (higher = better), a DQ
    scores 0. That makes the Braintrust dashboard rank strategies for you.
    """
    mode = "braintrust"

    def __init__(self, project: str = "pitcrew"):
        if not os.environ.get("BRAINTRUST_API_KEY"):
            raise RuntimeError("BRAINTRUST_API_KEY is not set")
        from braintrust import Braintrust  # lazy
        self._bt = Braintrust(project_name=project)

    def log(self, result: BayResult) -> None:
        score = result.speedup if (result.legal and result.speedup) else 0.0
        with self._bt.trace(name=f"bay-{result.bay:02d}") as span:
            span.log(
                score=score,
                metadata={
                    "strategy": result.strategy,
                    "state": result.state,
                    "ratio": result.ratio,
                    "tests": f"{result.tests_passed}/{result.tests_total}",
                    "error": result.error,
                },
            )
