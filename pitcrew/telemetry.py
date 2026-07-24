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

    def flush(self) -> None:
        pass


class BraintrustTelemetry:
    """Friday swap. One scored span per bay. Needs BRAINTRUST_API_KEY.

    Score convention: legal winners score by speedup (higher = better), a DQ
    scores 0. That makes the Braintrust dashboard rank strategies for you.
    """
    mode = "braintrust"

    def __init__(self, project: str = "pitcrew"):
        key = os.environ.get("BRAINTRUST_API_KEY")
        if not key:
            raise RuntimeError("BRAINTRUST_API_KEY is not set")
        # SETUP.md section 4 shows `from braintrust import Braintrust` with a
        # .trace() context manager. That class DOES NOT EXIST in braintrust
        # 0.30.1 - the import raises ImportError. The real API is login() +
        # init_logger(). Verified against the installed package on 2026-07-24.
        import logging

        import braintrust

        # The background flush thread dumps a full traceback per retry on a bad
        # key, which would bury the race output. login() below fails loudly instead.
        logging.getLogger("braintrust").setLevel(logging.CRITICAL)
        braintrust.login(api_key=key)  # synchronous: raises on a bad key
        self._logger = braintrust.init_logger(project=project, api_key=key)

    def log(self, result: BayResult) -> None:
        # Braintrust REJECTS scores outside 0..1 ("score values must be between 0
        # and 1"), so raw speedup (151x) cannot be a score - that was the original
        # convention and it raised ValueError on the first bay. Scores carry the
        # pass/fail judgement; speedup goes in metrics, which is unbounded and
        # still sorts the dashboard.
        speedup = result.speedup if (result.legal and result.speedup) else 0.0
        metrics = {"speedup": speedup}
        if result.baseline_ms is not None:
            metrics["baseline_ms"] = result.baseline_ms
        if result.candidate_ms is not None:
            metrics["candidate_ms"] = result.candidate_ms

        self._logger.log(
            input={"bay": result.bay, "strategy": result.strategy},
            output={"state": result.state, "legal": result.legal},
            scores={"legal": 1.0 if result.legal else 0.0},
            metrics=metrics,
            metadata={
                "strategy": result.strategy,
                "state": result.state,
                "ratio": result.ratio,
                "tests": f"{result.tests_passed}/{result.tests_total}",
                "error": result.error,
            },
        )

    def flush(self) -> None:
        """Braintrust logs on a background thread; call this before exit."""
        self._logger.flush()
