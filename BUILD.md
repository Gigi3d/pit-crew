# Pit Crew build plan (performance only)

Companion to [MVP.md](MVP.md). That file is the hour-by-hour schedule. This one is the repo layout, the contracts, and the code you should write **before Friday** so the morning is assembly rather than invention.

Scope for this hackathon is **performance only**. No security lane, no migration, no sweep. One PR, one function, thirty bays.

---

## 1. You need two repos

People lose an hour on Friday realising this.

| Repo | What it is | State by the night before |
|---|---|---|
| `pitcrew` | The product. Orchestrator, bay runner, UI. | Scaffolded, deps installed, keys working |
| `widget-api` | The **target**. The slow code we race against. | Finished, pushed, CodeRabbit installed |

`widget-api` is a prop, but it decides whether the demo lands. Build it first.

---

## 2. The target repo, `widget-api`

Small, real, and slow in a way that has more than one good fix. That last part matters: if there is exactly one obvious fix, all thirty bays produce the same patch and the tournament looks pointless.

### `app/events.py`
```python
def parse_events(rows, index):
    """Return every row whose id appears in index, newest first."""
    out = []
    for r in rows:
        # O(n*m): rebuilds the id list for every single row
        if r["id"] in [i["id"] for i in index]:
            label = ""
            for part in r["tags"]:          # quadratic string building
                label = label + "," + part
            out.append({**r, "label": label.strip(",")})
    # re-sorts on every call instead of sorting once
    for _ in range(3):
        out = sorted(out, key=lambda x: x["ts"], reverse=True)
    return out
```

Three independent inefficiencies means genuinely different winning strategies: set membership, `str.join`, and dropping the redundant sorts. Agents will find different subsets, which is exactly the spread you want on the leaderboard.

### `tests/test_events.py`
Your correctness gate. Make it strict enough that a fast-but-wrong patch actually fails.

```python
def test_filters_to_index(): ...
def test_preserves_all_original_fields(): ...
def test_label_is_comma_joined_in_tag_order(): ...
def test_sorted_newest_first(): ...
def test_empty_index_returns_empty(): ...
def test_duplicate_ids_are_not_deduped(): ...   # catches over-eager set() rewrites
```

That last test is the important one. It catches the patch that is fast because it quietly changed behaviour.

### `bench/run.py`
Prints one number, nothing else.

```python
import json, time, sys
from app.events import parse_events

rows, index = json.load(open(sys.argv[1]))
t0 = time.perf_counter()
for _ in range(5):
    parse_events(rows, index)
print(round((time.perf_counter() - t0) * 1000 / 5, 2))
```

### Fixtures
- `bench/fixture.json`: the workload agents are told about. Size it so the baseline lands at **500ms to 2s**. Around 20k rows against a 2k index is usually right.
- `bench/holdout.json`: a differently shaped workload used **only** for final scoring. Never mentioned in any prompt. This is what catches a patch memoised to the fixture.

Commit a `baseline.txt` with the measured number so you can sanity check drift on the day.

---

## 3. The bay contract

Freeze this first. It lets the UI and the orchestrator be built simultaneously by two people, and it is what the mock UI already speaks.

```json
{
  "bay": 12,
  "strategy": "set membership",
  "state": "done",
  "legal": true,
  "baseline_ms": 851.4,
  "candidate_ms": 91.2,
  "ratio": 0.107,
  "tests_passed": 240,
  "tests_total": 240,
  "error": null
}
```

- `state` is one of `queued` `run` `done` `dq`
- `legal` false plus `state: "dq"` means the patch broke tests or touched a forbidden file
- **`ratio` is the only cross-bay comparable number.** Never rank on `candidate_ms`, because bays sit on different physical hosts

---

## 4. What runs inside a bay

```
1. clone target at the PR commit          (or restore from the Daytona snapshot)
2. write the candidate patch
3. GUARD: reject if the diff touches tests/, bench/, or CI config  -> dq
4. run the test suite                                              -> fail = dq
5. interleave baseline and candidate, 5 iterations, take medians
6. return the contract object above
```

Step 3 is about ten lines and it is the difference between a working demo and an agent that deletes an assertion and reports a 400x win.

Step 5 in practice: run `bench/run.py` against the **original** file and the **patched** file alternately in the same sandbox, discard the first pair as warm-up, take the median of the rest. Report the ratio.

---

## 5. The product repo, `pitcrew`

```
pitcrew/
  orchestrator/
    race.py          spawn N bays, collect results, rank by ratio
    strategies.py    the 30 seed prompts (see below)
    verify.py        clean-room re-run of the winner in a fresh sandbox
  bay/
    runner.py        everything in section 4, runs inside the sandbox
    guard.py         the forbidden-path diff check
  agents/
    patch.py         Fireworks call: (source, strategy) -> unified diff
  api/
    server.py        serves race state, exposes the CopilotKit actions
  ui/
    index.html       the console (already built, see ui/ in this folder)
  evals/
    log.py           Braintrust span per bay
  .env
```

### Strategy seeding is the part people underestimate
Thirty agents given one prompt write thirty near-identical patches. Seed each bay with a *named, different* angle:

```python
STRATEGIES = [
  "replace linear membership scans with a hash-based lookup",
  "hoist loop-invariant work out of the hot loop",
  "use str.join instead of repeated concatenation",
  "remove redundant repeated sorting",
  "precompute an index once before iterating",
  "avoid copying dicts when a shallow update will do",
  "use a generator to avoid materialising intermediate lists",
  ...
]
```

Have a couple of deliberately mediocre seeds in there. A leaderboard where everything is 9x looks fake. A spread from 1.1x to 9.3x looks like a real race, and it makes the tournament argument for you.

---

## 6. The UI

Open [`ui/index.html`](ui/index.html) now. It runs a full fake race on load, and the **SPEAK COMMAND** button demonstrates the voice cull.

It is not a mockup to copy, it is the shell to wire. Every render function already takes the section 3 contract, so on the day you replace one function:

```js
function fakeRace(){ ... }   // <- delete this
// feed real events into paint(bay), refresh(), say('crew', text)
```

Layout, so you know what you are building toward:

- **Header**: repo, PR number, target function, live status, run and speak buttons
- **Stat strip**: baseline, fastest lap, speedup, legal vs DQ counts
- **Bay grid**: 30 tiles, each showing bay number, lap time, and state. Amber while running with a progress shimmer, green when legal, dimmed when disqualified, white and scaled up for P1
- **Leaderboard**: top six by ratio, live
- **Team radio**: the transcript, your commands in red, crew replies in green, with a mic indicator
- **Winner card**: before and after, the actual diff, the clean-room verification line, and Approve or Discard

The winner card is the slide-5 number and the CopilotKit approve action in one component. Keep it.

---

## 7. The night-before checklist

- [ ] `widget-api` built, pushed, baseline measured and committed
- [ ] CodeRabbit installed on `widget-api`, one test PR already reviewed
- [ ] Daytona snapshot with the repo and deps preinstalled, so bays skip `pip install`
- [ ] One successful call made to each of: Daytona, Fireworks, Braintrust, ElevenLabs
- [ ] `.env` filled, and a `hello.py` that exercises all four keys in one run
- [ ] The bay contract pasted into your team chat so nobody invents a second shape
- [ ] `ui/index.html` opened once on the actual presentation laptop and projector if possible
- [ ] Voice command rehearsed with background noise playing

## 8. The two things that will actually go wrong

**Thirty concurrent sandboxes hit a plan limit.** Find out the night before, not at 10:40 on Friday. Spawn 30 no-op sandboxes as your very first test and count how many you really get. If the ceiling is 10, the demo still works, and the deck says ten instead of thirty.

**Benchmarks are noisy and the race looks random.** This is why ratios and interleaving exist. If lap times still look absurd, raise the iteration count before you touch anything else.
