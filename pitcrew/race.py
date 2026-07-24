"""Orchestrate the race: fan out N bays in parallel, rank the legal ones by
ratio, verify the winner clean-room. Emits an event per bay as it finishes so a
UI can render live.
"""
from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Callable, List, Optional

from . import strategies
from .contracts import BayResult
from .runner import run_bay
from .sandbox import LocalSandbox
from .verify import clean_room_verify


@dataclass
class RaceResult:
    results: List[BayResult]
    winner: Optional[BayResult]
    verified_baseline_ms: Optional[float] = None
    verified_candidate_ms: Optional[float] = None
    verified_ratio: Optional[float] = None
    verified_tests_ok: bool = False


def run_race(
    target_repo: str,
    fixture: str,
    provider,
    n_bays: int = 10,  # measured Daytona ceiling on this account (CPU-quota capped)
    telemetry=None,
    sandbox_factory=LocalSandbox,
    winner_files_for: Optional[Callable[[int], dict]] = None,
    emit: Optional[Callable[[dict], None]] = None,
    max_workers: int = 8,
    rounds: int = 4,
    iters: int = 3,
) -> RaceResult:
    emit = emit or (lambda e: None)
    source = _read(os.path.join(target_repo, "app/events.py"))
    candidates = {
        b: provider.get(b, strategies.for_bay(b), source)
        for b in range(1, n_bays + 1)
    }

    emit({"type": "lights_out", "bays": n_bays})
    results: List[BayResult] = []

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futs = {
            pool.submit(run_bay, b, candidates[b], target_repo, fixture,
                        sandbox_factory, rounds, iters): b
            for b in range(1, n_bays + 1)
        }
        for fut in as_completed(futs):
            res = fut.result()
            results.append(res)
            if telemetry:
                telemetry.log(res)
            emit({"type": "bay", **res.to_dict()})

    results.sort(key=lambda r: r.bay)
    legal = [r for r in results if r.legal and r.ratio is not None]
    winner = min(legal, key=lambda r: r.ratio) if legal else None

    out = RaceResult(results=results, winner=winner)
    if winner:
        # clean-room re-verify in a sandbox that never met the race
        files = candidates[winner.bay]["files"]
        b, c, ok = clean_room_verify(target_repo, files, fixture,
                                     sandbox_factory, rounds, iters)
        out.verified_baseline_ms = round(b, 2)
        out.verified_candidate_ms = round(c, 2)
        out.verified_ratio = round(c / b, 4) if b else None
        out.verified_tests_ok = ok
        emit({"type": "winner", "bay": winner.bay, "strategy": winner.strategy,
              "baseline_ms": out.verified_baseline_ms,
              "candidate_ms": out.verified_candidate_ms,
              "ratio": out.verified_ratio, "tests_ok": ok})
    else:
        emit({"type": "no_winner"})
    return out


def _read(path: str) -> str:
    with open(path) as f:
        return f.read()
