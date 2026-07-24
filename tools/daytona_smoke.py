"""Prove one Daytona bay end to end, with a timing breakdown.

This is one bay doing exactly what all 30 do during the race: come up, take a
patch, run the test gate, report, and get torn down. Run it before
concurrency_test.py - if one bay does not work, thirty will not either.

    ./.venv/bin/python daytona_smoke.py

The timing breakdown is the point. Whichever phase dominates is the one worth
optimising, and it is almost always cold start - which is what build_snapshot.py
exists to fix.
"""

import os
import sys
import time

from dotenv import load_dotenv

load_dotenv()

key = os.getenv("DAYTONA_API_KEY")
if not key or key.startswith("#"):
    sys.exit("DAYTONA_API_KEY is not set in .env - get one at app.daytona.io")

SNAPSHOT = os.getenv("DAYTONA_SNAPSHOT")

from daytona import CreateSandboxFromSnapshotParams, Daytona, DaytonaConfig  # noqa: E402

client = Daytona(DaytonaConfig(api_key=key))

# A bay's real job: a buggy function, a candidate patch, and a test that judges it.
CANDIDATE_PATCH = '''
def last_n(items, n):
    return items[-n:] if n else []

# the correctness gate, same shape as widget-api's pytest run
assert last_n([1, 2, 3, 4], 2) == [3, 4], "wrong slice"
assert last_n([1, 2, 3], 0) == [], "n=0 should be empty"
print("PATCH OK")
'''

timings = {}
sandbox = None

try:
    print("\nOne bay, end to end\n" + "-" * 46)

    t = time.monotonic()
    if SNAPSHOT:
        sandbox = client.create(CreateSandboxFromSnapshotParams(snapshot=SNAPSHOT))
        how = f"from snapshot {SNAPSHOT!r}"
    else:
        sandbox = client.create()
        how = "from default image (no snapshot yet)"
    timings["cold start"] = time.monotonic() - t
    print(f"  up        {timings['cold start']:5.1f}s  {how}")

    t = time.monotonic()
    result = sandbox.process.code_run(CANDIDATE_PATCH)
    timings["run patch"] = time.monotonic() - t
    output = (result.result or "").strip()
    passed = "PATCH OK" in output
    print(f"  ran       {timings['run patch']:5.1f}s  gate {'PASSED' if passed else 'FAILED'}")
    if not passed:
        print(f"            output: {output[:200]}")

    t = time.monotonic()
    sandbox.delete()
    timings["teardown"] = time.monotonic() - t
    sandbox = None
    print(f"  torn down {timings['teardown']:5.1f}s")

    total = sum(timings.values())
    print("-" * 46)
    print(f"  total     {total:5.1f}s per bay")
    slowest = max(timings, key=timings.get)
    pct = 100 * timings[slowest] / total
    print(f"\n>>> {slowest} is {pct:.0f}% of a bay's life. <<<")
    if slowest == "cold start" and not SNAPSHOT:
        print(">>> Run build_snapshot.py - that is exactly what it fixes. <<<")
    print()

except Exception as e:
    print(f"\nFAILED: {type(e).__name__}: {e}\n")
    raise
finally:
    if sandbox is not None:
        print("cleaning up sandbox after failure...")
        try:
            sandbox.delete()
            print("deleted")
        except Exception as e:
            print(f"!! could not delete: {e}")
            print("!! check app.daytona.io for leftovers - they burn credits")
