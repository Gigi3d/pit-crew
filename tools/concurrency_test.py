"""Find out how many Daytona sandboxes you actually get in parallel.

Everything in the race assumes this number. Run it the moment your key works,
and again on venue wifi. If you get 12 instead of 30, you have a 12-bay garage
and you need to know that before you design the demo, not during it.

    ./.venv/bin/python concurrency_test.py [target]

Spawns `target` no-op sandboxes as fast as it can, reports how many came up,
how long they took, and then deletes every one it created.
"""

import concurrent.futures
import os
import sys
import time

from dotenv import load_dotenv

load_dotenv()

TARGET = int(sys.argv[1]) if len(sys.argv) > 1 else 30

key = os.getenv("DAYTONA_API_KEY")
if not key or key.startswith("#"):
    sys.exit("DAYTONA_API_KEY is not set in .env")

from daytona import Daytona, DaytonaConfig  # noqa: E402

client = Daytona(DaytonaConfig(api_key=key))

created = []
failures = []


def spawn(i):
    started = time.monotonic()
    sandbox = client.create()
    return i, sandbox, time.monotonic() - started


print(f"\nSpawning {TARGET} sandboxes...\n" + "-" * 54)
wall_start = time.monotonic()

with concurrent.futures.ThreadPoolExecutor(max_workers=TARGET) as pool:
    futures = [pool.submit(spawn, i) for i in range(TARGET)]
    for future in concurrent.futures.as_completed(futures):
        try:
            i, sandbox, elapsed = future.result()
            created.append(sandbox)
            print(f"  up   #{i:<3} in {elapsed:5.1f}s")
        except Exception as e:
            failures.append(e)
            print(f"  FAIL      {type(e).__name__}: {str(e)[:70]}")

wall = time.monotonic() - wall_start

print("-" * 54)
print(f"{len(created)}/{TARGET} sandboxes up in {wall:.1f}s wall clock")
if failures:
    kinds = {}
    for f in failures:
        kinds[type(f).__name__] = kinds.get(type(f).__name__, 0) + 1
    print("failures by type:", ", ".join(f"{k}x{v}" for k, v in kinds.items()))
print(f"\n>>> Design the race around {len(created)} bays, not {TARGET}. <<<\n")

print("Cleaning up...")
removed = 0
for sandbox in created:
    try:
        client.delete(sandbox)
        removed += 1
    except Exception as e:
        print(f"  could not delete {getattr(sandbox, 'id', '?')}: {e}")
print(f"deleted {removed}/{len(created)}")
if removed < len(created):
    print("!! Check app.daytona.io for leftovers - they burn credits.")
