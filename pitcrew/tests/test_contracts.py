from pitcrew.contracts import BayResult, dq


def test_speedup_from_ratio():
    r = BayResult(bay=1, strategy="s", state="done", legal=True, ratio=0.1)
    assert round(r.speedup, 1) == 10.0


def test_dq_is_illegal_with_no_speedup():
    r = dq(3, "hash by id", "tests failed", tests_passed=6, tests_total=7)
    assert r.state == "dq" and not r.legal and r.speedup is None
    assert r.to_dict()["tests_passed"] == 6
