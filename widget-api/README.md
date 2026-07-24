# widget-api

A tiny service repo. It exists for one reason: to be the target Pit Crew races against on stage.

```
app/events.py        the slow function under test: parse_events()
app/events_fast.py   the reference winning patch (NOT the product's answer, a fallback)
tests/test_events.py the correctness gate, 7 tests
bench/run.py         prints one number: mean ms per call
bench/gen_fixtures.py generates the workloads
bench/fixture.json   the workload agents optimise against
bench/holdout.json   a differently shaped workload, used only for final scoring
```

## Run it

```bash
pip install -r requirements.txt
python bench/gen_fixtures.py          # writes fixture.json + holdout.json
python -m pytest tests/ -q            # 7 passed
python bench/run.py bench/fixture.json # baseline ms
```

`app/events_fast.py` passes all 7 tests and is dramatically faster. That is the win the race is trying to discover. Keep it out of the target's import path so nothing accidentally uses it.
