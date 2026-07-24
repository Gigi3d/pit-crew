"""Bake a Daytona snapshot so bays start instantly.

*** MEASURED 2026-07-23: YOU DO NOT NEED THIS. ***

Two findings from running it against the live API:

1. Custom snapshot creation is DENIED on this account's plan
   (DaytonaAuthorizationError: Access denied). Every snapshot the account can
   see is one of Daytona's own general=True prebuilts.

2. It does not matter. SETUP.md's 30-60s warning assumes a heavy dependency
   tree; widget-api needs only pytest. Measured on a live sandbox:

       spawn 0.4s + pip install pytest 1.6s + verify 0.2s = 2.3s per bay

   A snapshot would save under two seconds per bay. Not worth an hour.

Keep this file in case the plan changes at the event, but do not spend prep
time here. Install deps at bay startup instead.

    ./.venv/bin/python build_snapshot.py

Run this ONCE, the night before. It bakes widget-api's dependencies into an
image; the race then spawns from the snapshot with everything preinstalled.

PREREQUISITE: widget-api must exist locally with a requirements.txt. Point at
it with WIDGET_API_PATH in .env if it is not a sibling of this directory.
"""

import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

SNAPSHOT_NAME = os.getenv("DAYTONA_SNAPSHOT", "pitcrew-widget-api")
WIDGET_API = Path(
    os.getenv("WIDGET_API_PATH", Path(__file__).parent.parent / "widget-api")
).expanduser()

key = os.getenv("DAYTONA_API_KEY")
if not key or key.startswith("#"):
    sys.exit("DAYTONA_API_KEY is not set in .env")

reqs = WIDGET_API / "requirements.txt"
if not reqs.is_file():
    sys.exit(
        f"No requirements.txt at {reqs}\n"
        "Create widget-api first, or set WIDGET_API_PATH in .env.\n"
        "The snapshot is only worth baking once its deps are pinned."
    )

from daytona import CreateSnapshotParams, Daytona, DaytonaConfig, Image, Resources  # noqa: E402

client = Daytona(DaytonaConfig(api_key=key))

print(f"\nBaking snapshot {SNAPSHOT_NAME!r}")
print(f"  deps from: {reqs}")
for line in reqs.read_text().splitlines():
    if line.strip() and not line.startswith("#"):
        print(f"    {line.strip()}")

# pytest is the correctness gate every bay runs, so it belongs in the image too.
image = (
    Image.debian_slim("3.13")
    .pip_install_from_requirements(str(reqs))
    .pip_install(["pytest"])
)

started = time.monotonic()
snapshot = client.snapshot.create(
    CreateSnapshotParams(
        name=SNAPSHOT_NAME,
        image=image,
        # SETUP.md section 2: defaults are 1 vCPU / 1GB / 3GiB per sandbox.
        resources=Resources(cpu=1, memory=1, disk=3),
    ),
    on_logs=print,
)
elapsed = time.monotonic() - started

print(f"\nSnapshot ready in {elapsed:.0f}s: {SNAPSHOT_NAME}")
print("\nSpawn bays from it with:")
print("    from daytona import CreateSandboxFromSnapshotParams")
print(f"    client.create(CreateSandboxFromSnapshotParams(snapshot={SNAPSHOT_NAME!r}))")
print("\nRe-run concurrency_test.py against the snapshot to get your real")
print("cold-start number - that is the one to design the race around.\n")
