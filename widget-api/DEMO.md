# The PR flow (which PR we race, and how PR #2 appears)

Two PRs. You prepare the first the night before. Pit Crew opens the second, live.

| | PR | Made by | Role |
|---|---|---|---|
| PR #1 | "Add event parsing" | you, the night before | The incoming PR that shipped slow code. **This is the race target.** |
| PR #2 | "perf: optimize parse_events" | Pit Crew, live | The winning patch. **CodeRabbit reviews this one on screen.** |

`main` stays clean. The slow function only ever exists on a branch, so PR #1's diff *is* the slow code, and the baseline the race measures is exactly what the PR introduced.

---

## The night before: create PR #1

Run from a fresh clone of your empty GitHub repo. Uses the GitHub CLI (`gh`); the web-UI fallback is below.

```bash
# main: everything EXCEPT the slow function
git checkout -b main
mkdir -p app tests bench
:> app/__init__.py
:> tests/__init__.py
cp .../requirements.txt .   ;  cp .../.gitignore .   ;  cp .../README.md .
cp .../tests/test_events.py tests/
cp .../bench/run.py bench/  ;  cp .../bench/gen_fixtures.py bench/
python bench/gen_fixtures.py
git add . && git commit -m "scaffold: tests, benchmark, fixtures"
git push -u origin main

# feature branch: adds ONLY the slow function
git checkout -b add-event-parsing
cp .../app/events.py app/
python bench/run.py bench/fixture.json > baseline.txt   # capture the real number
git add app/events.py baseline.txt
git commit -m "Add event parsing"
git push -u origin add-event-parsing

# open PR #1
gh pr create --base main --head add-event-parsing \
  --title "Add event parsing" \
  --body "Adds parse_events(): filters rows to the index and labels them."
```

Note the PR number `gh` prints. That is the number your orchestrator points at, and the number shown in the UI header.

**Web-UI fallback if `gh` is not installed:** push both branches, then open the repo on github.com and click "Compare & pull request" on the `add-event-parsing` branch.

Confirm CodeRabbit reviews PR #1 automatically. If it does, it will review PR #2 the same way, which is the whole point.

---

## On stage: Pit Crew opens PR #2

The orchestrator does this after the race, from the winning bay's diff. The commands it runs:

```bash
git fetch origin add-event-parsing
git checkout -b pitcrew/winner origin/add-event-parsing
# write the winning patch over app/events.py
git commit -am "perf: optimize parse_events (Nx faster, tests green)"
git push -u origin pitcrew/winner

gh pr create --base add-event-parsing --head pitcrew/winner \
  --title "perf: optimize parse_events" \
  --body "$WINNER_SUMMARY"   # ratio, before/after ms, clean-room note
```

PR #2 targets **`add-event-parsing`**, not `main`, so it reads as "here is the fix for your PR." A new PR appears on GitHub, CodeRabbit reviews it live, and your winner card's Approve button is what triggered it.

**If the live push fails** (auth, wifi), you still have `app/events_fast.py`. Open PR #2 by hand from a pre-made `pitcrew/winner` branch you pushed the night before but left as a draft. Rehearse this fallback once.

---

## The number

`baseline.txt` holds the real slow time. The winning patch (see `app/events_fast.py`) is genuinely dozens of times faster because it removes an O(n*m) scan. That large number is real and reproducible. Capture the actual before and after on the day and put them on the results slide, replacing the deck placeholders. Do not invent a smaller, "more believable" number: the clean-room re-verification is what makes the real one credible.
