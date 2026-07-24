# Pit Crew product feature doc

**Ten mechanics. One car. Four seconds.**

Pit Crew makes code faster by racing ten AI agents against each other in parallel sandboxes. A benchmark scores every attempt, the test suite decides which attempts are legal, and the fastest legal patch wins.

Status: spec. Nothing below is built yet. Written for Daytona HackSprint #5 and the product that could follow it.

---

## 1. The problem

Performance work is guess-and-check, and you only get one guess.

An engineer suspects a function is hot. They spend an afternoon on one optimisation idea, measure it, and either ship it or throw it away. They never learn whether a different approach would have been 5x better, because trying five approaches costs five afternoons.

Meanwhile the code quietly gets slower every release, and nobody notices until the cloud bill or a customer does.

The bottleneck is not intelligence. It is that a human can only run one experiment at a time.

## 2. The core idea

**Parallel speculative execution with an objective oracle.**

CPUs have executed dozens of branches simultaneously and discarded the losers for decades, because compute is cheaper than waiting. Sandboxes that boot in under 90ms make that same trade economical for whole machines. Cheap high-throughput inference makes it economical for whole *agents*.

So: spawn ten isolated attempts, let each try a different optimisation strategy, and let a machine rank them.

The entire product depends on one question being answerable without a human: **which of these ten attempts is best?** For performance work the answer is a benchmark, which is why this domain works and why marketing copy does not.

## 3. Two oracles, and why both are mandatory

This is the most important design decision in the product.

| Oracle | Type | Role |
|---|---|---|
| Test suite | Binary | **Gate.** Decides which patches are legal. |
| Benchmark | Continuous | **Score.** Ranks the legal patches. |

A binary oracle alone wastes the swarm: the race ends at first pass and the other twenty-nine results are discarded. A continuous oracle alone is dangerous: fast and wrong is worse than slow and right.

Running both in that order (gate, then score) is what turns a lottery into a tournament. Every bay returns usable information, so you can rank all ten, keep the fastest legal handful, mutate them, and race again.

## 4. Reward hacking is the main technical risk

An agent optimising for a benchmark number will cheat if cheating is easier than optimising. Expected attacks, all of which a naive implementation would score as spectacular wins:

- Deleting or weakening the assertions that make tests fail
- Memoising the exact benchmark input so the second call is free
- Detecting the benchmark harness and short-circuiting under it
- Moving work to module import time so it lands outside the timed region
- Returning a cached or precomputed constant

Mitigations, all of which belong in v0 because a demo that gets caught cheating on stage is worse than no demo:

1. **The test suite is read-only.** Patches touch source files only. Any diff to test files, benchmark harness, or CI config is an instant disqualification, checked before scoring.
2. **Hidden validation inputs.** Score on inputs the agent never sees, drawn from a different distribution than the ones in the prompt.
3. **Whole-process timing.** Measure wall time end to end, including import, so work cannot be smuggled into module load.
4. **Re-verify the winner from a clean checkout** in a fresh sandbox before showing anyone the number.

Point 4 is the one that matters. The winning number a human sees must come from a sandbox that never met the agent that produced it.

## 5. Benchmarking inside sandboxes is noisy, and that has to be handled

Cloud sandboxes share physical hardware. Absolute timings drift with whatever the neighbours are doing, so a naive implementation will crown the bay that got the quietest host rather than the best patch.

Design rules:

- **Never compare across sandboxes.** Every bay measures its own baseline *and* its own candidate, and reports the **ratio**. Ratios are comparable across hosts; milliseconds are not.
- **Interleave** baseline and candidate runs rather than running all of one then all of the other, so drift affects both equally.
- **Multiple iterations, report the median**, and discard the first run to exclude warm-up and JIT effects.
- **Re-race the top 3** on a single sandbox at the end, sequentially, for the final ranking.

The headline number shown to the user is always from that final sequential re-race.

## 6. Two product modes

Both use the same engine. They differ in trigger, scope, and who they are sold to.

### Mode A: Per PR (the guardrail)
Runs automatically on every pull request. Detects performance regressions before merge and offers a faster patch when it finds one.

- Trigger: PR opened or updated
- Scope: functions touched by the diff
- Output: a review comment with the delta, and a suggested patch on request
- Value: nothing merges slower than it arrived
- Why it matters commercially: it is a habit, it runs forever, and it is what makes the product retained rather than a one-off

### Mode B: Full sweep (the season opener)
Point it at an entire repository. It profiles, ranks the slowest paths, and races the top N overnight.

- Trigger: manual, or scheduled
- Scope: whole codebase
- Output: a ranked report plus one PR per accepted improvement
- Value: the number that wins the meeting
- Why it matters commercially: it is the land motion, it produces a headline result in the first 24 hours, and it justifies the contract

The intended sequence is sweep to land, per-PR to retain.

## 7. User flow

**Setup (once)**
1. Install the GitHub App on a repository
2. Point Pit Crew at the benchmark command and the test command
3. Confirm the detected runtime

**A race**
1. Trigger fires (PR, schedule, or manual)
2. Target selection picks the function or path to optimise
3. Ten bays spawn in parallel, each seeded with a different optimisation strategy
4. Each bay: apply patch, run tests (gate), run interleaved benchmark (score), report ratio
5. Illegal patches are discarded, legal ones ranked
6. Top 10 mutated and re-raced, then top 3 refined and re-raced
7. Winner re-verified from a clean checkout in a fresh sandbox
8. Result surfaced as a PR with the before, after, ratio, and the full tournament log

**Human control**
At any point the user can veto a patch, force a different strategy, or stop the race. Nothing reaches a branch without approval.

## 8. Feature list

### v0, hackathon scope (must exist by 3:30pm Friday)
- Parallel spawn of N sandboxes with a per-bay agent loop
- Strategy seeding so the ten bays attempt genuinely different approaches
- Test gate and benchmark score, with ratio-based measurement
- Three-round tournament with mutation of survivors
- Anti-cheat: read-only tests, clean-room re-verification of the winner
- Live grid UI showing bays and falling lap times
- Voice narration of the race
- One real measured result to put on the results slide

### v1, first real users
- GitHub App with per-PR guardrail mode
- Automatic detection of test and benchmark commands
- Profiling to pick targets in sweep mode
- Strategy library learned from prior races
- Cost ceiling per race, and a hard timeout
- Report with the full tournament log, not just the winner

### Later
- Language coverage beyond the launch runtime
- Migration lane: same engine, tests as the sole oracle, aimed at the broken dependency upgrades Dependabot opens and abandons
- Cost-aware optimisation, targeting cloud spend rather than latency
- Regression tracking over time, so a repo has a performance history

## 9. Architecture and the stack

```
trigger (PR / schedule / manual)
   |
   v
target selection ......... which function are we racing?
   |
   v
strategy seeding ......... 30 distinct optimisation approaches
   |
   +--> Daytona bay 1 ....... patch -> tests (gate) -> benchmark (score)
   +--> Daytona bay 2 ....... "
   +--> ... x30 ............. all in parallel, isolated
   |
   v
rank legal patches -> mutate top 10 -> race -> refine top 3 -> race
   |
   v
clean-room re-verification in a fresh sandbox
   |
   v
PR + report
```

| Component | Provider | Role |
|---|---|---|
| Sandboxes | **Daytona** | Ten isolated machines, sub-90ms spawn. Provides both the safety boundary for untrusted patches and the isolation that makes benchmarks trustworthy. |
| Review | **CodeRabbit** | Nominates the slow path on PR review, and re-reviews the winning patch before merge. A benchmark cannot tell you the code is unreadable. |
| Inference | **Fireworks AI** | Ten bays across three rounds is ~30 calls per race. High-throughput open models are what make a tournament affordable rather than a one-time stunt. |
| Evaluation | **Braintrust** | Logs and scores every lap. Learns which strategy class wins on which code shape, at what token cost, so the strategy library improves each race. |
| Control UI | **CopilotKit** | The pit wall. `useCopilotAction` turns a spoken sentence into a real call on the swarm: kill bays, spawn bays, re-seed a strategy. |
| Voice | **ElevenLabs** | Team radio, two way. Speech to text carries the command in, TTS speaks the result back. |

## 10. Safety model

The event asks for agents that operate safely. The honest version:

- **Nothing executes on user infrastructure.** Every patch runs inside a Daytona sandbox with its own kernel, filesystem, and network.
- **Nothing reaches a branch without a human.** The output is a proposed PR, never a direct push.
- **The agent cannot edit its own grading criteria.** Tests and benchmark harness are read-only, enforced by diff inspection before scoring.
- **The winning number is independently reproduced** in a clean sandbox that never ran the agent.
- **Bounded blast radius by construction.** A compromised or malicious patch reaches one disposable bay and nothing else.

## 11. Open questions

1. **Target selection in sweep mode.** Profiling gives hot paths, but hot does not mean optimisable. Needs a heuristic for "hot and plausibly improvable".
2. **Strategy diversity.** Ten agents given the same prompt will produce ten similar patches. Seeding needs to enforce genuinely different approaches, and the right mechanism is unproven.
3. **What counts as a win.** Is a 4% improvement worth a PR? There is a threshold below which the review cost exceeds the value, and it is probably repo-specific.
4. **Benchmark availability.** Most repositories have tests. Far fewer have benchmarks. If Pit Crew has to write the benchmark too, then it is grading its own homework, which reopens every reward-hacking concern in section 4.

Question 4 is the biggest commercial risk and should be tested with real repositories before building v1.

## 12. What would make this a business

The wedge is not "AI makes code faster". It is that **compute is now cheaper than an engineer's afternoon**, so exploring ten options costs less than carefully choosing one.

That logic generalises to any engineering task with a machine-checkable definition of better: performance, dependency migration, security patching, flaky test elimination. Performance is the entry point because the oracle is a number, the result is a headline, and the buyer already has a budget line for cloud spend.
