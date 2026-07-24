from pitcrew import guard


def test_app_paths_are_legal():
    ok, reason = guard.check_paths(["app/events.py"])
    assert ok and reason is None


def test_touching_tests_is_illegal():
    ok, reason = guard.check_paths(["app/events.py", "tests/test_events.py"])
    assert not ok and "forbidden" in reason


def test_touching_bench_is_illegal():
    ok, _ = guard.check_paths(["bench/run.py"])
    assert not ok


def test_path_escape_is_illegal():
    ok, reason = guard.check_paths(["app/../tests/test_events.py"])
    assert not ok and "escape" in reason
