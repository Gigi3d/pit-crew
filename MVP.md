# Pit Crew MVP build spec (Daytona HackSprint #5)

Hacking window is **10:00 to 15:30. Five and a half hours.** This document is the scoped-down version of [PRODUCT.md](PRODUCT.md), written so it can actually be finished, while still touching all six sponsor tracks.

**The one sentence:** a pull request comes in, ten agents race in parallel Daytona sandboxes to make the changed function faster, and the fastest patch that still passes the tests wins.

---

## 1. In scope, and firmly out

| In | Out (say "later" on stage, do not build) |
|---|---|
| One repository, prepared in advance | Any repo, auto-detection of commands |
| One target function, hardcoded | Profiling, target selection, whole-codebase sweep |
| One round of ten bays | Three-round tournament with mutation |
| Manual trigger from a button | Real GitHub App, webhooks, install flow |
| Python (or your fastest language) | Multi-language support |
| Tests as gate, benchmark as score | Cost ceilings, regression history, strategy library |

Everything in the right column belongs on the roadmap slide, not in the build.

**The tournament is the one judgement call.** One round is the honest MVP. The build leaves a `ROUNDS` constant so that if the core works by 13:00 you flip it to 3 and get the mutation story too. Do not start there.

## 2. Prep before Friday (this is the highest-leverage hour you will spend)

Nothing here is against the rules, and skipping it is how teams lose the morning to auth errors.

- [ ] Accounts created and API keys in a `.env`: Daytona, Fireworks, Braintrust, ElevenLabs
- [ ] One successful hello-world call made to each of those four
- [ ] CodeRabbit installed on the demo GitHub repo, with one test PR already reviewed so you know it works
- [ ] CopilotKit example app cloned and running locally
- [ ] Demo repo built and pushed (spec below)
- [ ] Daytona snapshot prepared with the repo and dependencies preinstalled, so bays do not spend 40 seconds on `pip install`
- [ ] Decide the team split, one person per sponsor integration

## 3. The demo repo (build this the night before)

The demo repo is the single biggest determinant of whether the demo lands. It needs:

1. **A genuinely slow function** with an obvious but non-trivial fix. Good candidates: an O(n²) loop that should be a dict lookup, repeated recomputation that should be cached, a naive string concat in a loop, a pandas `apply` that should be vectorised.
2. **A real test suite** covering that function's behaviour, including edge cases. This is your correctness gate, so it must be strict enough that a wrong-but-fast patch actually fails.
3. **A benchmark script** that runs the function on a fixed workload and prints a duration.
4. **A hidden validation set**, used only for final scoring, that the agent never sees in its prompt.

Target a baseline slow enough to be dramatic but fast enough to iterate: roughly 500ms to 2s per benchmark run. Anything slower and ten parallel bays will not finish inside your demo.

## 4. Build order, by risk

Always build the thing that could kill the project first.

**10:00 to 11:00. Daytona parallel spawn.** Nothing else. Ten sandboxes up concurrently, each running a trivial command, results collected. If this does not work you must know at 11:00, not at 14:00, because everything else is worthless without it.

**11:00 to 12:15. The bay loop.** Inside one sandbox: receive a patch, apply it, run tests, run the benchmark, return `{legal, ratio}`. Then wire it to the ten-way spawn with ten different strategy prompts.

**12:15 to 13:00. Fireworks generates the patches.** Swap in their API for patch generation. Ten distinct strategy seeds so bays do not all produce the same diff.

**13:00 to 14:00. The grid UI.** This is what wins, so give it real time. Ten tiles, live status, lap times falling, winner highlighted. Do not let this slip.

**14:00 to 14:30. Braintrust.** Log every lap as a scored span: strategy, ratio, legal, tokens.

**14:30 to 15:00. Voice race control and the CodeRabbit PR.** Wire `useCopilotAction` first so a *typed* command culls the grid, then put speech to text in front of it. Open the winning patch as a real PR so CodeRabbit reviews it live.

**15:00 to 15:20. Rehearse the three minutes twice.** Out loud. Timed.

**15:20 to 15:30. Submit.** Do not be finishing code here.

## 5. Minimum real integration per sponsor

Each of these is small, but each is genuinely load-bearing. Bolt-ons lose tracks.

| Sponsor | Smallest real usage | Effort |
|---|---|---|
| **Daytona** | Ten parallel sandboxes running untrusted patches | Core, unavoidable |
| **Fireworks** | The model generating all ten patches | ~20 min, it is an API swap |
| **Braintrust** | A scored **strategy eval**, not just logging: which optimisation wins, at what reliability, DQs scored zero. `python -m pitcrew.evals` already builds it. | ~20 min |
| **CopilotKit** | `useCopilotAction` executes a typed or spoken command against the live swarm | ~40 min |
| **CodeRabbit** | Winner opens a real PR, CodeRabbit reviews it on camera | ~15 min, mostly prep |
| **ElevenLabs** | Speaks the crew's reply back. Garnish only: no judge in the room, no cash prize. | ~20 min, do last |

**Two best-value integrations, both undertargeted.** CodeRabbit is a $1,000 track
few teams will bother with, fifteen minutes mostly prep. Braintrust is the co-host
("HackSprint w/ Braintrust") and its judge is an Eval Engineer, so a real scored
eval, which you already have, punches above its $500.

## 6. Keep these two safeguards even under time pressure

They are cheap, and they are your best answers in Q&A.

**Read-only tests.** Before scoring any patch, reject it if the diff touches test files, the benchmark harness, or config. Roughly ten lines. Without it, an agent will delete an assertion and report a 400x speedup, and if that happens on stage you are finished.

**Clean-room re-verification.** Re-run the winning patch from a fresh checkout in a new sandbox before showing the number. Roughly twenty lines. It means the number a judge sees came from a sandbox that never met the agent that produced it.

## 7. Measurement: never compare across sandboxes

Cloud sandboxes share hardware, so absolute timings drift with whatever the neighbours are doing. A naive build crowns the bay with the quietest host.

**The rule:** every bay measures its own baseline *and* its own candidate, and reports the **ratio**. Interleave the runs, take the median of five, discard the first. Ratios compare across hosts. Milliseconds do not.

The headline number comes from the clean-room re-verification in section 6, run once, sequentially.

## 8. Cut list, in order

When you are behind, cut in exactly this order. The order follows the prize map:
ElevenLabs has no judge in the room and no cash prize, so it goes first. Braintrust
is the co-host and CodeRabbit is a $1,000 track with two judges, so they are protected.

1. **ElevenLabs spoken confirmation.** The crew's reply shows as text either way.
2. **Voice input.** Keep the CopilotKit action, type the command instead of speaking it. The grid still culls, which is the part that matters and the part CopilotKit is judged on.
3. Drop to fewer bays (five still reads as a race). Ten is already the measured Daytona cap, not a target.

**Never cut:** Daytona parallel spawn, the test gate, the grid UI, the clean-room
re-verification, the **Braintrust strategy eval**, and the **CodeRabbit review on PR #2**.
Those are the project and the two richest side prizes.

**Rehearse the voice command in a noisy room.** A hackathon venue at 4pm is loud, and laptop speech to text degrades badly in crowd noise. Bind the same `useCopilotAction` to a text box and a keyboard shortcut, so if the mic fails mid-pitch you type the sentence and the demo continues without a visible stumble. Say the command into a headset mic if you have one.

## 9. What must be on screen at 15:30

- Ten tiles, visibly running at once
- Lap times falling
- One winner, highlighted
- A real before and after number from the clean-room run
- Green tests next to that number
- A command (spoken or typed) visibly culling the grid
- A real PR on GitHub with a CodeRabbit review on it

If all six are true, you have a finished project regardless of what got cut.

## 10. The honest line for the pitch

Say this out loud, because judges reward it and it disarms the obvious question:

> "Today it races one function on one pull request. The engine does not care about that scope. Point it at a whole codebase and it is a performance sweep. Give it tests instead of a benchmark and it fixes the broken dependency upgrades Dependabot opens and abandons. Same crew, same garage, same oracle."
