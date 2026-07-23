"""Bake a Daytona snapshot so bays start instantly.

SETUP.md section 2: without this, every one of the 30 bays spends 30-60s on
`pip install` before it can do any work, and a 20-second race becomes a
four-minute one. On stage that difference is the whole demo.

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
