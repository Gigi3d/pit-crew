"""Run one bay: guard, apply, test, benchmark. This is section 4 of BUILD.md,
identical whether the sandbox is local (today) or Daytona (Friday).
"""
from __future__ import annotations

from . import guard
from .contracts import BayResult, dq


def run_bay(bay: int, candidate: dict, target_repo: str, fixture: str,
            sandbox_factory, rounds: int = 4, iters: int = 3) -> BayResult:
    strategy = candidate.get("strategy", "?")
    files = candidate["files"]

    # 1. GUARD before anything runs
    ok, reason = guard.check_paths(files.keys())
    if not ok:
        return dq(bay, strategy, error=reason)

    try:
        with sandbox_factory(target_repo) as sb:
            baseline_src = sb.read("app/events.py")   # pristine, before we patch

            # 2. apply + 3. tests (the gate)
            sb.write(files)
            passed, total, tests_ok = sb.run_tests()
            if not tests_ok:
                return dq(bay, strategy, error="tests failed",
                          tests_passed=passed, tests_total=total)

            # 4. benchmark, interleaved, ratio only
            candidate_src = files["app/events.py"]
            base_ms, cand_ms = sb.bench_interleaved(
                baseline_src, candidate_src, fixture, rounds=rounds, iters=iters)
            ratio = cand_ms / base_ms if base_ms else None

            return BayResult(
                bay=bay, strategy=strategy, state="done", legal=True,
                baseline_ms=round(base_ms, 2), candidate_ms=round(cand_ms, 2),
                ratio=round(ratio, 4) if ratio else None,
                tests_passed=passed, tests_total=total,
            )
    except Exception as e:  # a crashed bay is a DQ, never a crashed race
        return dq(bay, strategy, error=f"{type(e).__name__}: {e}")
