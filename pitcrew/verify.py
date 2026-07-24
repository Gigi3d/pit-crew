"""Clean-room verification. Re-run the winning patch from a fresh copy in a
sandbox that never met the agent that produced it. The number a judge sees comes
from HERE, not from the racing bay.
"""
from __future__ import annotations

from typing import Tuple


def clean_room_verify(target_repo: str, winner_files: dict, fixture: str,
                      sandbox_factory, rounds: int = 4, iters: int = 3
                      ) -> Tuple[float, float, bool]:
    """Return (baseline_ms, candidate_ms, tests_ok)."""
    with sandbox_factory(target_repo) as sb:
        baseline_src = sb.read("app/events.py")
        sb.write(winner_files)
        _, _, tests_ok = sb.run_tests()
        base, cand = sb.bench_interleaved(
            baseline_src, winner_files["app/events.py"], fixture,
            rounds=rounds, iters=iters)
    return base, cand, tests_ok
