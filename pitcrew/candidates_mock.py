"""Pre-written patches for MOCK mode, so the whole race runs with no LLM and no
keys. The ONLY thing mocked here is model output. The timing, the tests, the
guard, the ranking, and the clean-room verify are all real.

Each SOURCE is a full replacement for app/events.py. The spread is deliberate:
several real optimisations of different strength, two patches that are fast but
WRONG (caught by the test gate), and one that tries to weaken the tests (caught
by the guard). That produces a believable leaderboard and real disqualifications.

When you have a FIREWORKS_API_KEY, swap MockPatchProvider for FireworksPatchProvider
and delete none of this. It stays as your offline fallback.
"""

# --- real optimisations, all correct, varying strength -----------------------

SLOW = '''\
def parse_events(rows, index):
    out = []
    for r in rows:
        if r["id"] in [i["id"] for i in index]:
            label = ""
            for part in r["tags"]:
                label = label + "," + part
            out.append({**r, "label": label.strip(",")})
    for _ in range(3):
        out = sorted(out, key=lambda x: x["ts"], reverse=True)
    return out
'''

JOIN = '''\
def parse_events(rows, index):
    out = []
    for r in rows:
        if r["id"] in [i["id"] for i in index]:
            out.append({**r, "label": ",".join(r["tags"])})
    for _ in range(3):
        out = sorted(out, key=lambda x: x["ts"], reverse=True)
    return out
'''

SORTONCE = '''\
def parse_events(rows, index):
    out = []
    for r in rows:
        if r["id"] in [i["id"] for i in index]:
            label = ""
            for part in r["tags"]:
                label = label + "," + part
            out.append({**r, "label": label.strip(",")})
    out.sort(key=lambda x: x["ts"], reverse=True)
    return out
'''

SET = '''\
def parse_events(rows, index):
    ids = {i["id"] for i in index}
    out = []
    for r in rows:
        if r["id"] in ids:
            label = ""
            for part in r["tags"]:
                label = label + "," + part
            out.append({**r, "label": label.strip(",")})
    for _ in range(3):
        out = sorted(out, key=lambda x: x["ts"], reverse=True)
    return out
'''

SET_SORT = '''\
def parse_events(rows, index):
    ids = {i["id"] for i in index}
    out = []
    for r in rows:
        if r["id"] in ids:
            label = ""
            for part in r["tags"]:
                label = label + "," + part
            out.append({**r, "label": label.strip(",")})
    out.sort(key=lambda x: x["ts"], reverse=True)
    return out
'''

SET_JOIN = '''\
def parse_events(rows, index):
    ids = {i["id"] for i in index}
    out = []
    for r in rows:
        if r["id"] in ids:
            out.append({**r, "label": ",".join(r["tags"])})
    for _ in range(3):
        out = sorted(out, key=lambda x: x["ts"], reverse=True)
    return out
'''

FULL = '''\
def parse_events(rows, index):
    ids = {i["id"] for i in index}
    out = []
    for r in rows:
        if r["id"] in ids:
            out.append({**r, "label": ",".join(r["tags"])})
    out.sort(key=lambda x: x["ts"], reverse=True)
    return out
'''

# --- fast but WRONG: the test gate must catch these ---------------------------

# dedupes by id -> fails test_duplicate_ids_are_not_deduped
BROKEN_DEDUPE = '''\
def parse_events(rows, index):
    ids = {i["id"] for i in index}
    by_id = {}
    for r in rows:
        if r["id"] in ids:
            by_id[r["id"]] = {**r, "label": ",".join(r["tags"])}
    out = list(by_id.values())
    out.sort(key=lambda x: x["ts"], reverse=True)
    return out
'''

# ignores the index entirely -> fails test_filters_to_index + empty index
BROKEN_FILTER = '''\
def parse_events(rows, index):
    out = [{**r, "label": ",".join(r["tags"])} for r in rows]
    out.sort(key=lambda x: x["ts"], reverse=True)
    return out
'''

SOURCES = {
    "SLOW": SLOW, "JOIN": JOIN, "SORTONCE": SORTONCE, "SET": SET,
    "SET_SORT": SET_SORT, "SET_JOIN": SET_JOIN, "FULL": FULL,
    "BROKEN_DEDUPE": BROKEN_DEDUPE, "BROKEN_FILTER": BROKEN_FILTER,
}

LABELS = {
    "SLOW": "no change", "JOIN": "str.join", "SORTONCE": "sort once",
    "SET": "set membership", "SET_SORT": "set + sort once",
    "SET_JOIN": "set + join", "FULL": "set + join + sort once",
    "BROKEN_DEDUPE": "hash by id", "BROKEN_FILTER": "drop the filter",
    "MALICIOUS": "edit the tests",
}

# Hand-mixed candidate pool (a race takes the first n_bays) for a realistic race: strong winners, a long tail, two
# test-failing patches, and one that tries to tamper with the gate.
BAY_PLAN = [
    "FULL", "SET_JOIN", "SET", "JOIN", "SORTONCE", "SET_SORT", "FULL", "SET_JOIN",
    "SET", "BROKEN_DEDUPE", "JOIN", "SET_SORT", "SET", "SLOW", "SET_JOIN",
    "BROKEN_FILTER", "FULL", "JOIN", "SET", "MALICIOUS", "SET_SORT", "SET_JOIN",
    "SLOW", "SET", "BROKEN_DEDUPE", "JOIN", "SET_JOIN", "FULL", "SET_SORT", "SET",
]


def candidate_for(bay: int) -> dict:
    """Return {strategy, files} for a 1-indexed bay in mock mode."""
    key = BAY_PLAN[(bay - 1) % len(BAY_PLAN)]
    if key == "MALICIOUS":
        files = {"app/events.py": FULL, "tests/test_events.py": "# assertions removed\n"}
    else:
        files = {"app/events.py": SOURCES[key]}
    return {"strategy": LABELS[key], "files": files}
