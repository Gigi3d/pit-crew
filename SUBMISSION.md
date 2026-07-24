# Devpost submission

Fill this into Devpost when submissions open. Everything the page requires is here.

---

## Team name
**Pit Crew**

## Team members
List everyone with **email and socials** (the page asks for these so they can tag
you). Fill in before submitting.

- <name>, <email>, <x/github/linkedin>

## Demo video
The under-2-minute recording. Script in [VIDEO.md](VIDEO.md).

---

## Project description

**Summary (2 to 3 sentences).**
Pit Crew gives every pull request a pit stop. I run bitmask-core, an open-source
Bitcoin wallet, and I get contributor PRs that have to be both correct and fast, so
I built a tool that sends thirty AI agents to race in parallel isolated sandboxes to
make the changed function faster, where the test suite decides who is legal and the
fastest patch wins. You watch it live, steer it by voice, and the winner opens a
real, reviewed pull request. I built it for my repo; any open-source maintainer can
use it.

**The problem and its impact.**
I maintain an open-source Bitcoin wallet. Contributors I have never met send pull
requests, and every one has to be correct and fast, because a slow wallet loses
users and a wrong one loses coins. As a solo founder I cannot deeply benchmark every
PR by hand. More generally, performance work is guess-and-check and an engineer only
ever gets one guess; code quietly gets slower every release until a customer or the
cloud bill notices. The bottleneck is not intelligence, it is that a human runs one
experiment at a time. Pit Crew runs thirty at once, because compute is now cheaper
than a maintainer's afternoon. It turns a vague "this feels slow" into a measured,
verified, reviewed speedup in under a minute, and the same engine extends to security
fixes and dependency migrations. Every open-source maintainer has this exact problem.

**Key technical architecture and components.**
- A **GitHub pull request** is the trigger; the changed function is the target.
- An **orchestrator** fans out N bays in parallel. Each bay is an isolated sandbox
  that applies one candidate patch, runs the real test suite as a hard gate, then
  benchmarks itself against its own baseline and reports a ratio (ratios, never raw
  milliseconds, because bays sit on different hosts).
- Two oracles: the **test suite** decides which patches are legal, the **benchmark**
  ranks the legal ones. Fast-but-wrong patches are disqualified.
- A **guard** rejects any patch that touches the tests or the harness, so an agent
  cannot cheat by weakening its own grader.
- The winner is **re-verified in a clean-room sandbox** that never ran the race,
  so the headline number is trustworthy, then opened as a new pull request.
- A **live console** streams the race; a **voice command** can cull or steer bays
  mid-race; a **human approves** before anything reaches a branch.

**Sponsor tools and how we integrated them.**
- **Daytona**: the thirty parallel bays are Daytona sandboxes. Untrusted
  AI-generated patches run at full speed with zero blast radius. This is the
  primitive the whole project stands on: without cheap, fast, isolated sandboxes
  the tournament is impossible.
- **Fireworks AI**: generates all thirty candidate patches concurrently on
  deepseek-v3p1. High-throughput open-model inference is what makes a thirty-way
  race affordable per pull request; frontier models would cost more than the bug.
- **Braintrust**: scores every bay and aggregates a strategy leaderboard: which
  optimisation wins, at what reliability, with disqualifications scored zero. It
  turns the race into a real eval, so the swarm gets smarter each run.
- **CopilotKit**: the actuator. A `useCopilotAction` turns a spoken sentence
  ("kill everything slower than 300ms") into a real call that culls the grid, and
  another opens the winning pull request on approval.
- **CodeRabbit**: reviews the winning pull request before it can merge. A
  benchmark proves the code is fast; CodeRabbit is the check that it is also
  readable and correct in review. It is the last gate before the branch.
- **ElevenLabs**: the crew's voice: it speaks the race back to you ("bay twelve,
  ninety-one milliseconds") so the loop is a two-way radio, not a dashboard.

---

## Presenter notes (not for the judges' eyes)

**How the demo maps to the four judging axes (25% each).** Make sure each lands:
- **Impact**: say the pain out loud: dead performance PRs, rising cloud bills, one
  guess per engineer. Name the expansion to security and migration.
- **Technical Execution**: the two-oracle design, the anti-cheat guard, the
  clean-room re-verification. This is where you prove it is real, not a wrapper.
- **Creativity**: parallel speculative execution for engineering work: thirty
  attempts, throw away the losers, because compute beats waiting. The F1 framing.
- **Presentation**: the jersey, the live race, the voice command, "thirty agents
  enter, one patch leaves." Your strongest axis. Own the room.

**Sponsor usage is a bonus for placement but half the cash is in Best-Use prizes.**
Make each integration genuinely "the best use," not a bolt-on, and you can stack a
placement with multiple side prizes.

**Safety is in the brief.** Say it plainly: nothing runs on the user's machine,
nothing merges without a human, the agent cannot edit its own grader, the winning
number is independently reproduced. Sandboxing is the reason all of that is true.
