"""Small workload generator for local runs, so a mock race finishes in seconds.
Mirrors widget-api/bench/gen_fixtures.py but sized down.
"""
from __future__ import annotations

import json
import random

TAGS = ["auth", "api", "db", "cache", "ui", "infra", "perf", "sec", "docs", "test"]


def make(rows_n: int, index_n: int, id_space: int, seed: int):
    rnd = random.Random(seed)
    index = [{"id": i} for i in rnd.sample(range(id_space), index_n)]
    rows = [{"id": rnd.randrange(id_space),
             "ts": rnd.randrange(1_000_000_000),
             "tags": rnd.sample(TAGS, rnd.randint(1, 4))}
            for _ in range(rows_n)]
    return [rows, index]


def write_mini(path: str, rows_n: int = 3000, index_n: int = 300,
               id_space: int = 6000, seed: int = 1) -> str:
    with open(path, "w") as f:
        json.dump(make(rows_n, index_n, id_space, seed), f)
    return path
