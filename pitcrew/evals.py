"""The Braintrust eval. Not just logging: a scored evaluation of which repair
STRATEGY actually wins, aggregated across the race.

Each strategy is a case. Its score is the speedup it achieved (0 if it was
disqualified). Run it, get a ranked leaderboard of strategies. That is exactly
what an eval engineer wants to see, and it is the co-host's tool.

  python -m pitcrew.evals           # run a mock race, score strategies, print
                                     # (pushes to Braintrust too if a key is set)

Runs today with no key: the leaderboard prints locally. With BRAINTRUST_API_KEY,
the same scores also land in the Braintrust dashboard.
"""
from __future__ import annotations

import os
import statistics
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List

from .contracts import BayResult


@dataclass
class StrategyScore:
    strategy: str
    runs: int
    legal: int
    dq: int
    best_speedup: float          # the eval score for this strategy
    median_speedup: float
    legal_rate: float


def score_strategies(results: List[BayResult]) -> List[StrategyScore]:
    """Aggregate bay results into a per-strategy scored leaderboard."""
    by_strat: Dict[str, List[BayResult]] = defaultdict(list)
    for r in results:
        by_strat[r.strategy].append(r)

    out: List[StrategyScore] = []
    for strat, rs in by_strat.items():
        speedups = [r.speedup for r in rs if r.legal and r.speedup]
        legal = len(speedups)
        out.append(StrategyScore(
            strategy=strat,
            runs=len(rs),
            legal=legal,
            dq=len(rs) - legal,
            best_speedup=round(max(speedups), 1) if speedups else 0.0,
            median_speedup=round(statistics.median(speedups), 1) if speedups else 0.0,
            legal_rate=round(legal / len(rs), 2),
        ))
    # rank by the eval score: best achievable speedup, then reliability
    out.sort(key=lambda s: (s.best_speedup, s.legal_rate), reverse=True)
    return out


def print_leaderboard(scores: List[StrategyScore]) -> None:
    print(f"\n{'STRATEGY':<26}{'best':>7}{'median':>8}{'legal':>7}{'runs':>6}")
    print("-" * 54)
    for s in scores:
        flag = "" if s.legal_rate == 1 else f"  ({s.dq} dq)"
        print(f"{s.strategy:<26}{s.best_speedup:>6.1f}x{s.median_speedup:>7.1f}x"
              f"{int(s.legal_rate*100):>6}%{s.runs:>6}{flag}")


def push_braintrust(scores: List[StrategyScore], project: str = "pitcrew") -> bool:
    """Push each strategy as a scored eval case. Needs BRAINTRUST_API_KEY."""
    if not os.environ.get("BRAINTRUST_API_KEY"):
        return False
    from braintrust import Eval  # lazy

    cases = [{"input": s.strategy, "expected": "faster, still correct"} for s in scores]
    lut = {s.strategy: s for s in scores}

    def task(strategy: str) -> str:
        s = lut[strategy]
        return f"{s.best_speedup}x best, {int(s.legal_rate*100)}% legal"

    def speedup_score(input, output, expected):
        s = lut[input]
        # normalise: 10x+ is a full score, DQ-heavy strategies score low
        return min(s.best_speedup / 10.0, 1.0) * s.legal_rate

    Eval(project, data=cases, task=task,
         scores=[lambda input, output, expected, **k: speedup_score(input, output, expected)])
    return True


def main():
    from .providers import MockPatchProvider
    from .race import run_race
    from . import fixtures
    import tempfile, os as _os

    here = _os.path.dirname(_os.path.abspath(__file__))
    target = _os.path.normpath(_os.path.join(here, "..", "widget-api"))
    fixture = fixtures.write_mini(_os.path.join(tempfile.gettempdir(), "pitcrew_eval.json"))

    print("running a race to score strategies (mock, no keys needed)...")
    result = run_race(target_repo=target, fixture=fixture,
                      provider=MockPatchProvider(), n_bays=10, max_workers=8)
    scores = score_strategies(result.results)
    print_leaderboard(scores)

    if push_braintrust(scores):
        print("\npushed to Braintrust project 'pitcrew'")
    else:
        print("\n(set BRAINTRUST_API_KEY to also push these scores to Braintrust)")


if __name__ == "__main__":
    main()
