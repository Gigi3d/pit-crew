"""Generates the two workloads. Seeded, so the numbers are reproducible.

  python bench/gen_fixtures.py

Writes:
  bench/fixture.json   the workload agents are told about
  bench/holdout.json   a differently shaped workload used ONLY for final scoring

Tune ROWS / INDEX until `python bench/run.py bench/fixture.json` lands the
baseline between 500ms and 2000ms on your machine. Bigger = slower.
"""
import json
import random

TAGS = ["auth", "api", "db", "cache", "ui", "infra", "perf", "sec", "docs", "test"]


def make(rows_n, index_n, id_space, seed):
    rnd = random.Random(seed)
    index = [{"id": i} for i in rnd.sample(range(id_space), index_n)]
    rows = []
    for _ in range(rows_n):
        rows.append({
            "id": rnd.randrange(id_space),
            "ts": rnd.randrange(1_000_000_000),
            "tags": rnd.sample(TAGS, rnd.randint(1, 4)),
        })
    return [rows, index]


if __name__ == "__main__":
    # Sized so the SLOW baseline lands ~800ms on a laptop, which gives the 30-bay
    # race a satisfying ~15s runtime. The optimised win is large and REAL: removing
    # the O(n*m) scan is genuinely a 50x-plus speedup. Capture the actual number on
    # the day and put it on the results slide. Do not hand-pick a smaller one.
    json.dump(make(rows_n=16000, index_n=1600, id_space=24000, seed=1),
              open("bench/fixture.json", "w"))
    # holdout: different shape, different seed, never shown to an agent
    json.dump(make(rows_n=9000, index_n=2600, id_space=15000, seed=99),
              open("bench/holdout.json", "w"))
    print("wrote bench/fixture.json and bench/holdout.json")
