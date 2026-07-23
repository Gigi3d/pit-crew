"""Test 30 CONCURRENT Fireworks calls, not one.

SETUP.md section 3: throughput is the thing you are betting on. One call
succeeding tells you nothing about 30 at once - that is where rate limits,
queueing, and tail latency show up.

    ./.venv/bin/python fireworks_load_test.py [n]

Reports per-call latency, the p50/p95 spread, and any rate-limit errors. The
number that matters is the SLOWEST call: the race is only over when the last
bay reports, so p95 is your race time, not the mean.
"""

import concurrent.futures
import os
import statistics
import sys
import time

from dotenv import load_dotenv

load_dotenv()

N = int(sys.argv[1]) if len(sys.argv) > 1 else 30
MODEL = os.getenv("FIREWORKS_MODEL", "accounts/fireworks/models/deepseek-v3p1")

key = os.getenv("FIREWORKS_API_KEY")
if not key or key.startswith("#"):
    sys.exit("FIREWORKS_API_KEY is not set in .env")

from fireworks import Fireworks  # noqa: E402

client = Fireworks(api_key=key)

PROMPT = (
    "Here is a Python function with an off-by-one bug:\n\n"
    "def last_n(items, n):\n    return items[-n-1:]\n\n"
    "Return only the corrected function."
)


def one_call(i):
    started = time.monotonic()
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": PROMPT}],
        max_tokens=200,
    )
    elapsed = time.monotonic() - started
    tokens = getattr(resp.usage, "completion_tokens", 0) if resp.usage else 0
    return i, elapsed, tokens


latencies = []
failures = []

print(f"\n{N} concurrent calls to {MODEL}\n" + "-" * 58)
wall_start = time.monotonic()

with concurrent.futures.ThreadPoolExecutor(max_workers=N) as pool:
    futures = [pool.submit(one_call, i) for i in range(N)]
    for future in concurrent.futures.as_completed(futures):
        try:
            i, elapsed, tokens = future.result()
            latencies.append(elapsed)
            print(f"  ok   #{i:<3} {elapsed:5.1f}s  {tokens:>4} tokens")
        except Exception as e:
            failures.append(e)
            print(f"  FAIL      {type(e).__name__}: {str(e)[:60]}")

wall = time.monotonic() - wall_start

print("-" * 58)
print(f"{len(latencies)}/{N} succeeded in {wall:.1f}s wall clock")

if latencies:
    latencies.sort()
    p50 = statistics.median(latencies)
    p95 = latencies[min(int(len(latencies) * 0.95), len(latencies) - 1)]
    print(f"fastest {latencies[0]:.1f}s | p50 {p50:.1f}s | p95 {p95:.1f}s | slowest {latencies[-1]:.1f}s")
    print(f"\n>>> Your race takes ~{latencies[-1]:.0f}s, not ~{p50:.0f}s. Quote the slowest bay. <<<")

if failures:
    kinds = {}
    for f in failures:
        kinds[type(f).__name__] = kinds.get(type(f).__name__, 0) + 1
    print("\nfailures:", ", ".join(f"{k} x{v}" for k, v in kinds.items()))
    if any("RateLimit" in type(f).__name__ for f in failures):
        print("!! Rate limited at zero balance. Re-run after redeeming credits Friday.")
print()
