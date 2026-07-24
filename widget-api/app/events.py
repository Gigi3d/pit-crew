def parse_events(rows, index):
    """Return every row whose id appears in index, with a label built from its
    tags, sorted newest first.

    Correct, but deliberately slow in three independent ways. This is the
    function Pit Crew races to optimise. Do not "fix" it here.
    """
    out = []
    for r in rows:
        # SLOW 1: rebuilds the id list from scratch for every single row -> O(n*m)
        if r["id"] in [i["id"] for i in index]:
            # SLOW 2: quadratic string building instead of ",".join(...)
            label = ""
            for part in r["tags"]:
                label = label + "," + part
            out.append({**r, "label": label.strip(",")})
    # SLOW 3: sorts the same list three times instead of once
    for _ in range(3):
        out = sorted(out, key=lambda x: x["ts"], reverse=True)
    return out
