"""The correctness gate. A fast-but-wrong patch must fail here.

These run inside every bay before the benchmark is even measured. If any fail,
the patch is disqualified regardless of how fast it is.
"""
from app.events import parse_events


def _row(id, ts, tags):
    return {"id": id, "ts": ts, "tags": tags}


def test_filters_to_index():
    rows = [_row(1, 10, ["a"]), _row(2, 20, ["b"]), _row(3, 30, ["c"])]
    index = [{"id": 1}, {"id": 3}]
    got = [r["id"] for r in parse_events(rows, index)]
    assert set(got) == {1, 3}


def test_preserves_all_original_fields():
    rows = [_row(1, 10, ["a"])]
    index = [{"id": 1}]
    out = parse_events(rows, index)[0]
    assert out["id"] == 1 and out["ts"] == 10 and out["tags"] == ["a"]
    assert "label" in out


def test_label_is_comma_joined_in_tag_order():
    rows = [_row(1, 10, ["z", "a", "m"])]
    index = [{"id": 1}]
    assert parse_events(rows, index)[0]["label"] == "z,a,m"


def test_empty_tags_gives_empty_label():
    rows = [_row(1, 10, [])]
    index = [{"id": 1}]
    assert parse_events(rows, index)[0]["label"] == ""


def test_sorted_newest_first():
    rows = [_row(1, 10, ["a"]), _row(2, 99, ["b"]), _row(3, 50, ["c"])]
    index = [{"id": 1}, {"id": 2}, {"id": 3}]
    ts = [r["ts"] for r in parse_events(rows, index)]
    assert ts == sorted(ts, reverse=True)


def test_empty_index_returns_empty():
    rows = [_row(1, 10, ["a"])]
    assert parse_events(rows, []) == []


def test_duplicate_ids_are_not_deduped():
    # Two distinct rows share an id. Both must survive. Catches the patch that
    # is fast because it quietly turned the result into a set.
    rows = [_row(7, 10, ["a"]), _row(7, 20, ["b"]), _row(8, 30, ["c"])]
    index = [{"id": 7}]
    out = parse_events(rows, index)
    assert len(out) == 2
    assert {r["ts"] for r in out} == {10, 20}
