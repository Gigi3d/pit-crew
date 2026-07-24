# pitcrew

The race engine. It spawns N bays, each applying a candidate patch to the target
function, gating on the tests, timing the result, and ranking by speedup. The
winner is re-verified in a clean room.

**It runs today with no API keys.** Mock mode uses pre-written patches instead of
a model and local temp copies instead of Daytona sandboxes. Everything else, the
tests, the timing, the guard, the ranking, the clean-room verify, is real.

## Run the mock race

```bash
cd ~/thunderdome
python -m pytest pitcrew/tests/ -q          # engine unit tests
python -m pitcrew.cli                        # full 30-bay race vs ../widget-api
python -m pitcrew.cli --bays 12 --workers 6  # smaller, faster
python -m pitcrew.cli --full-fixture         # use the real 700ms workload
```

It prints a live leaderboard and writes `race_events.jsonl` (one event per bay,
the exact stream the UI will consume) and `race_result.json`.

## What is real vs mocked

| Piece | Mock mode (today) | Friday swap |
|---|---|---|
| Patch source | `MockPatchProvider`, pre-written | `FireworksPatchProvider` |
| Sandbox | `LocalSandbox`, temp copy | `DaytonaSandbox` |
| Telemetry | `NullTelemetry` | `BraintrustTelemetry` |
| Tests, timing, guard, ranking, verify | **real** | **real** |

## The Friday swap

Three one-line changes in `cli.py`, nothing else in the engine moves:

```python
from .providers import FireworksPatchProvider   # was MockPatchProvider
from .sandbox   import DaytonaSandbox            # was LocalSandbox (via run_race default)
from .telemetry import BraintrustTelemetry       # was NullTelemetry
```

`FireworksPatchProvider` and `BraintrustTelemetry` are written and import-lazy, so
they load with no key present and only reach for the SDK when constructed.
`DaytonaSandbox` is a documented skeleton: implement `__enter__` (create) and
`__exit__` (destroy, in a finally, always) against the same method surface
`LocalSandbox` exposes. Keep the mock classes: they are your offline fallback if a
vendor is down on the day.

## Files

```
contracts.py       BayResult, the frozen shape everything speaks
guard.py           patches may only touch app/, checked before scoring
strategies live in candidates_mock.py (mock) / are seeded per bay (fireworks)
sandbox.py         LocalSandbox (real, local) + DaytonaSandbox (skeleton)
providers.py       MockPatchProvider (real) + FireworksPatchProvider (skeleton)
telemetry.py       NullTelemetry (real) + BraintrustTelemetry (skeleton)
runner.py          one bay: guard, apply, test, benchmark
race.py            fan out, rank, verify winner, emit events
verify.py          clean-room re-run of the winner
fixtures.py        small workload for fast local runs
cli.py             python -m pitcrew.cli
```

## Not built here (needs keys or a browser)

- The voice layer (ElevenLabs) and the CopilotKit action wiring live in the
  Next.js UI, not this Python engine.
- Wiring `race_events.jsonl` into the live `ui/index.html` is a small Friday task:
  replace `fakeRace()` with a reader of that stream.
