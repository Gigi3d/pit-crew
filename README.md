# Pit Crew

**Every PR gets a pit stop.** Thirty AI agents race in parallel isolated sandboxes to
make a pull request's code faster; the tests decide who is legal, the fastest patch
wins, a human approves, and it opens a reviewed PR. Built for **bitmask-core**, an
open-source Bitcoin wallet, for the **Daytona HackSprint (Friday, July 24 2026)**.

This folder is the whole project: working engine, decks, and every planning doc.

## Run it now (no keys)

```bash
pip install -r pitcrew-requirements.txt   # or just: pip install pytest
python3 -m pytest pitcrew/tests widget-api/tests -q   # 13 tests
python3 -m pitcrew.cli          # full 30-bay race in the terminal
python3 -m pitcrew.serve        # then open http://localhost:8420  (live UI)
python3 -m pitcrew.evals        # Braintrust-style strategy leaderboard
python3 hello.py                # stack check (skips services with no key)
```

Everything runs in **mock mode** with no API keys: the LLM and cloud sandbox are
stubbed, but the tests, timing, guard, ranking, and clean-room verify are all real.

## Where everything is

| Path | What it is |
|---|---|
| `pitcrew/` | the race engine (mock + Friday-swap adapters). See `pitcrew/README.md` |
| `widget-api/` | the target repo Pit Crew races against. See `widget-api/DEMO.md` |
| `ui/index.html` | the console design reference (animated fake race) |
| `ui/live.html` | the console wired to the live engine over SSE |
| `copilotkit/` | the Next.js voice + action files. See `copilotkit/README.md` |
| `deck-mvp/` | **the deck to present** (13 slides) |
| `deck-pitcrew/`, `deck/` | full-vision deck and the Thunderdome alternative |

## The docs, in reading order

| Doc | Purpose |
|---|---|
| `PITCH.md` | the 3-minute live pitch script (solo, in the jersey) |
| `SUBMISSION.md` | the Devpost submission text, ready to paste |
| `VIDEO.md` | the under-2-minute demo video script |
| `MVP.md` | the hour-by-hour Friday build schedule and cut list |
| `BUILD.md` | repo layout, the bay contract, the demo-repo code |
| `SETUP.md` | per-tool setup, keys, and sponsor priority order |
| `INSTALL.md` | everything to install on a bare Mac |
| `PRODUCT.md` | the full product/feature spec |
| `.env.example` | the keys needed for the Friday swap (none needed for mock) |

## Status

- Built and verified with no keys: the engine, the live console, the eval, the target
  repo (13 passing tests), all three decks, all docs.
- Needs Friday (keys / on-machine): the Daytona concurrency test, `npx create-next-app`
  for the CopilotKit UI, confirming two SDK signatures (flagged in `SETUP.md` section 8),
  swapping the three adapters to the real services, recording the video.
- Needs you: the four accounts + keys, `gh auth login` on the new device, creating and
  pushing the `pitcrew` and `widget-api` repos, the Devpost submission.

## The one honest note

`bitmask-core` is 92% Rust. The live demo races a representative Python function for
reliability; the engine is language-agnostic (a bay runs `cargo` instead of `pytest`).
The console labels it `SAMPLE FN`, and `PITCH.md` has the one-sentence answer if a
judge asks.
