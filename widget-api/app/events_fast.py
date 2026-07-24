"""The reference winning patch. NOT committed to widget-api.

Keep this in your pitcrew toolbox, not in the target repo. Two uses:
  1. a fallback: if the live race produces nothing good, PR #2 is this, by hand
  2. a sanity check: run the tests and bench against this to confirm your
     demo repo really does speed up and stay correct

It fixes all three slow paths and passes every test, including
test_duplicate_ids_are_not_deduped (note: it does NOT use a set for output).
"""


def parse_events(rows, index):
    ids = {i["id"] for i in index}          # FIX 1: build the lookup set once
    out = []
    for r in rows:
        if r["id"] in ids:
            label = ",".join(r["tags"])     # FIX 2: single join, no quadratic concat
            out.append({**r, "label": label})
    out.sort(key=lambda x: x["ts"], reverse=True)   # FIX 3: sort once
    return out
