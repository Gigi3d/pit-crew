"""Prints one number: the mean milliseconds per parse_events call.

Usage: python bench/run.py bench/fixture.json
The bay runner calls this against the original and the patched file, interleaved.
"""
import json
import os
import sys
import time

# make `app` importable no matter what directory this is launched from
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.events import parse_events

with open(sys.argv[1]) as f:
    rows, index = json.load(f)

ITERS = int(sys.argv[2]) if len(sys.argv) > 2 else 5
t0 = time.perf_counter()
for _ in range(ITERS):
    parse_events(rows, index)
elapsed_ms = (time.perf_counter() - t0) * 1000 / ITERS
print(round(elapsed_ms, 2))
