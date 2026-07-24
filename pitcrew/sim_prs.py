"""A feed of realistic performance PRs, for demoing the race repeatedly.

Modelled on the kind of hot paths a Bitcoin wallet core (bitmask-core) actually
optimises: coin selection, PSBT handling, descriptor derivation, UTXO scans.
These are demo scenarios, not real pull requests. The "Open the PR" link points
at a repo YOU own (PITCREW_SIM_REPO), so nothing here impersonates the real
bitmask-stack project or fabricates a review against it.

    from pitcrew.sim_prs import next_pr
    pr = next_pr()   # a different scenario each call

Each scenario carries a plausible before/after and the winning strategy, so
every Discord post looks like a distinct race instead of a repeat.
"""
from __future__ import annotations

import json
import os
import random
from pathlib import Path

# Where the simulated PR links resolve. Point this at your own fork, e.g.
# Gigi3d/bitmask-core, so the links are real and yours. Defaults to widget-api.
SIM_REPO = os.getenv("PITCREW_SIM_REPO", "Gigi3d/widget-api")

# area, title, winning strategy, baseline_ms, candidate_ms
SCENARIOS = [
    ("coin-selection",
     "Speed up branch-and-bound coin selection on large UTXO sets",
     "prune the search tree once effective value is met", 1840, 22),
    ("utxo",
     "Group and cache UTXOs by descriptor instead of rescanning",
     "index by descriptor, single pass", 960, 14),
    ("psbt",
     "Avoid re-parsing the PSBT on every input finalization",
     "parse once, mutate in place", 1220, 31),
    ("fees",
     "Vectorise fee estimation over the mempool histogram",
     "bucket once, cumulative sum", 540, 9),
    ("descriptors",
     "Cache derived addresses in the descriptor wallet gap scan",
     "memoise derivation by index", 2100, 40),
    ("balance",
     "Compute confirmed balance in one UTXO pass",
     "accumulate in a single fold", 780, 11),
    ("merkle",
     "Short-circuit SPV Merkle proof verification on match",
     "early-exit on root match", 610, 7),
    ("serialization",
     "Reserve capacity when serializing large transactions",
     "presize the buffer", 430, 12),
    ("keys",
     "Batch BIP32 child key derivation for account discovery",
     "derive siblings together", 1550, 28),
    ("rgb",
     "Deduplicate RGB state transitions before consignment",
     "hash-set the transitions", 1980, 35),
]

# A tiny state file so consecutive posts do not repeat the same scenario.
_STATE = Path(__file__).resolve().parent.parent / ".pitcrew_sim_state.json"


def _next_number() -> int:
    """A monotonically climbing demo PR number, so each post looks fresh."""
    try:
        state = json.loads(_STATE.read_text())
    except (OSError, ValueError):
        state = {}
    n = int(state.get("pr", 128)) + random.randint(1, 3)
    last = state.get("last_scenario")
    state["pr"] = n
    _STATE.write_text(json.dumps(state))
    return n


def next_pr() -> dict:
    """Return a fresh simulated PR: a scenario plus a plausible PR number/URL."""
    try:
        state = json.loads(_STATE.read_text())
        last = state.get("last_scenario")
    except (OSError, ValueError):
        last = None

    choices = [s for s in SCENARIOS if s[0] != last] or SCENARIOS
    area, title, strategy, baseline, candidate = random.choice(choices)

    number = _next_number()
    # Persist which scenario we used so the next call avoids it.
    try:
        state = json.loads(_STATE.read_text())
    except (OSError, ValueError):
        state = {}
    state["last_scenario"] = area
    _STATE.write_text(json.dumps(state))

    return {
        "area": area,
        "title": title,
        "strategy": strategy,
        "baseline_ms": baseline,
        "candidate_ms": candidate,
        "number": number,
        "pr_url": f"https://github.com/{SIM_REPO}/pull/{number}",
    }


if __name__ == "__main__":
    for _ in range(3):
        pr = next_pr()
        print(f"#{pr['number']:>4}  {pr['title']}")
        print(f"       {pr['baseline_ms']}ms -> {pr['candidate_ms']}ms  "
              f"({pr['baseline_ms'] // pr['candidate_ms']}x)  |  {pr['pr_url']}")
