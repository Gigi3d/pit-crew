"""Run a full race from the terminal, no keys required.

  python -m pitcrew.cli                       # mock race against ../widget-api
  python -m pitcrew.cli --target /path/to/widget-api --bays 30

Writes race_events.jsonl and race_result.json next to where you run it, so the
same events can later feed the live UI.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile

from . import fixtures
from .providers import MockPatchProvider
from .race import run_race
from .telemetry import NullTelemetry

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_TARGET = os.path.normpath(os.path.join(HERE, "..", "widget-api"))

C = {"g": "\033[32m", "a": "\033[33m", "r": "\033[31m", "w": "\033[97m",
     "d": "\033[90m", "x": "\033[0m", "b": "\033[1m"}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default=DEFAULT_TARGET)
    ap.add_argument("--bays", type=int, default=30)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--full-fixture", action="store_true",
                    help="use the target's real fixture.json instead of a mini one")
    args = ap.parse_args(argv)

    target = os.path.abspath(args.target)
    if not os.path.isdir(target):
        sys.exit(f"target repo not found: {target}")

    if args.full_fixture:
        fixture = os.path.join(target, "bench", "fixture.json")
    else:
        fixture = fixtures.write_mini(os.path.join(tempfile.gettempdir(), "pitcrew_mini.json"))

    events = []
    events_path = os.path.abspath("race_events.jsonl")
    ev_file = open(events_path, "w")

    def emit(e):
        events.append(e)
        ev_file.write(json.dumps(e) + "\n"); ev_file.flush()
        if e["type"] == "lights_out":
            print(f"\n{C['r']}{C['b']}LIGHTS OUT{C['x']}  {e['bays']} bays away\n")
        elif e["type"] == "bay":
            _print_bay(e)
        elif e["type"] == "winner":
            _print_winner(e)
        elif e["type"] == "no_winner":
            print(f"\n{C['r']}no legal patch this race{C['x']}")

    print(f"{C['d']}target : {target}\nfixture: {fixture}\nmode   : MOCK (no keys){C['x']}")
    result = run_race(
        target_repo=target, fixture=fixture,
        provider=MockPatchProvider(), n_bays=args.bays,
        telemetry=NullTelemetry(), emit=emit, max_workers=args.workers,
    )
    ev_file.close()

    legal = [r for r in result.results if r.legal]
    dqs = [r for r in result.results if not r.legal]
    print(f"\n{C['d']}{'-'*52}{C['x']}")
    print(f"{len(legal)} legal, {len(dqs)} disqualified")
    if result.winner:
        s = 1 / result.verified_ratio if result.verified_ratio else 0
        print(f"{C['w']}{C['b']}winner: bay {result.winner.bay:02d} "
              f"({result.winner.strategy}){C['x']}")
        print(f"clean-room: {result.verified_baseline_ms}ms -> "
              f"{C['g']}{result.verified_candidate_ms}ms{C['x']}  "
              f"{C['w']}{s:.1f}x faster{C['x']}  "
              f"tests {'green' if result.verified_tests_ok else 'RED'}")

    with open("race_result.json", "w") as f:
        json.dump({
            "results": [r.to_dict() for r in result.results],
            "winner_bay": result.winner.bay if result.winner else None,
            "verified": {
                "baseline_ms": result.verified_baseline_ms,
                "candidate_ms": result.verified_candidate_ms,
                "ratio": result.verified_ratio,
                "tests_ok": result.verified_tests_ok,
            },
        }, f, indent=2)
    print(f"{C['d']}wrote race_events.jsonl and race_result.json{C['x']}")


def _print_bay(e):
    if e["state"] == "dq":
        print(f"  {C['r']}DQ  {C['x']} bay {e['bay']:02d}  {C['d']}{e['strategy']:<20}"
              f" {e['error']}{C['x']}")
    else:
        sp = e.get("speedup") or 0
        col = C["g"] if sp >= 3 else C["a"]
        print(f"  {col}done{C['x']} bay {e['bay']:02d}  {e['strategy']:<20}"
              f" {e['candidate_ms']:>7}ms  {col}{sp:>5.1f}x{C['x']}")


def _print_winner(e):
    sp = 1 / e["ratio"] if e["ratio"] else 0
    print(f"\n{C['w']}{C['b']}P1  bay {e['bay']:02d}  {e['strategy']}{C['x']}  "
          f"{e['baseline_ms']}ms -> {C['g']}{e['candidate_ms']}ms{C['x']} "
          f"({sp:.1f}x), tests {'green' if e['tests_ok'] else 'RED'}")


if __name__ == "__main__":
    main()
