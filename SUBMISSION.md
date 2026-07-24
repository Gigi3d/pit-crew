# PitCrew: Devpost submission

Paste-ready. The seven judged sections first, meta and presenter notes at the bottom.

---

## Inspiration

I am the founder of an open-source Bitcoin wallet backed by Tim Draper, with over 300,000 wallets created. Every pull request that lands in that codebase has to be fast and safe, because real people are moving real money through it.

Take UTXO coin selection. When you send Bitcoin, the wallet has to pick which unspent outputs to spend. That is a combinatorial search, and it sits on the hot path of every single transaction. The set of outputs only grows, and the number of ways to combine them explodes, so a slow implementation is a wallet that feels broken, and a subtly wrong one loses money. Reviewing that kind of PR by hand, and actually proving one version is faster than another without breaking it, takes real time a small team does not always have.

PitCrew is the pit stop every PR deserves. It does this for our wallet, and it can do it for any team. It can even take a legacy codebase and start making it agentic, one function at a time.

## What it does

A pull request comes in with a slow function. PitCrew races ten AI agents to fix it, and only lets a winner out if it is both correct and fast.

- Ten agents spin up, each in its own sealed cloud machine, each seeded with a different optimization strategy, each writing its own candidate patch.
- The test suite is the referee. A patch that is faster but wrong gets disqualified. A patch that is correct but slow gets retired. Only a patch that is both survives.
- The fastest legal patch wins, and PitCrew re-runs it in a clean machine that never saw the race, so the number is honest.
- You approve the winner by voice or by typing. The winning PR posts to your team Discord with a replay of the race, and CodeRabbit reviews it automatically.

Concrete example: a contributor speeds up coin selection over a large UTXO set. PitCrew proves the new version is dramatically faster with byte-identical output, then opens the reviewed PR. Nobody benchmarked anything by hand.

## How we built it

Six sponsor tools, one loop.

- **Daytona** runs the ten agents, each in an isolated sandbox. Untrusted AI code runs at full speed with zero blast radius, and that same isolation is what makes the benchmark trustworthy.
- **Fireworks** writes the ten patches, one per agent, each with a different strategy seed. It also powers the assistant you talk to, so the whole product leans on one inference provider instead of bolting on another.
- **Braintrust** scores and ranks every agent, so the race is a measured tournament with data behind it, not a lottery.
- **CopilotKit** turns "approve the winner" or "kill everything slower than 100ms" into a real action on the grid. The model only pulls the number out of your sentence. The actual work is plain code, which is exactly why typing is a perfect fallback if the mic dies.
- **ElevenLabs** gives the crew a voice, hearing the command and answering back over pit radio.
- **CodeRabbit** reviews the winning PR the moment it lands in Discord.

The console itself is a Next.js app on Vercel that runs the race client-side, so the public demo needs no backend on anyone's laptop.

## Challenges we ran into

Almost every problem was a "looks fine, is quietly broken" problem. We are proud of catching them early.

- **We planned for thirty agents.** We measured, and the account tops out at ten concurrent sandboxes because of a CPU quota. We found that the night before instead of on stage, so the whole demo now says ten and means it.
- **A dependency deadlock.** One SDK required an older pydantic, another required a newer one, and no single version satisfied both. We pinned the combination that actually works and wrote down why, so nobody "fixes" it back into a break under pressure.
- **The recommended model did not exist.** The docs pointed at a model our account could not see. Auth passed, the model 404'd. We probed the live model list, tested candidates on the real patch task, and picked the fastest one.
- **GitHub threw 500s while opening the winning PR.** Right as we shipped, GitHub's pull-request API had an incident. We built retry-through-5xx, and it rode straight through.
- **Small landmines everywhere.** An SDK class the docs referenced but did not exist. An API key minted with zero permissions. Clients constructed at build time with no keys. A font that fetched at build and would have died on venue wifi. Each one would have been a live-demo failure. Each one got caught first.

## Accomplishments that we're proud of

- **It works end to end, for real.** A real PR, a real race, a real winning patch that is many times faster with identical output, a real Discord post, and a real CodeRabbit review. Nothing staged.
- **We never fake a result.** Every number the demo shows is measured, and every link points at a real record. When a review is real, we show it. When it is not, we do not pretend it is.
- **Honest tradeoff by design.** The target function is correct but slow on purpose, so the race has a real finish line the tests enforce, not a scripted outcome.
- **One URL is the whole product.** A single Vercel deploy runs the race, the voice, the Discord post, and the review handoff. No laptop in the loop.

## What we learned

- **The demo that survives a stage is the one you already broke in private.** The morning was calm only because we ran the entire loop the night before and hit every failure with time to fix it.
- **Isolation is a measurement feature, not just a safety one.** You cannot trust a benchmark that shares a machine, so the sandbox that keeps untrusted patches safe is the same thing that makes the timing honest.
- **Give the LLM the smallest possible job.** Ours only extracts a number. Everything downstream is deterministic, and that is what makes it reliable enough to run live in front of judges.

## What's next for PitCrew

- **A security lane.** Same race, but the referee is a fuzzer and a static analyzer instead of a benchmark. Every PR to a wallet should be proven safe, not just fast.
- **A real tournament.** Turn the single race into rounds: keep the fastest legal patches, mutate them, and race again.
- **Language-agnostic bays.** The engine already treats a bay as "run a command, read a result." Rust, Go, and TypeScript targets are a small step, which matters because our own wallet is mostly Rust.
- **Legacy to agentic.** Point PitCrew at an old codebase and let it optimize and harden it function by function, opening reviewed PRs the whole way.

---

## Built with

Daytona, Fireworks AI, Braintrust, CopilotKit, ElevenLabs, CodeRabbit, Next.js, Vercel, Python, TypeScript.

## Links

- Live app: `https://<your-vercel-app>.vercel.app`
- Code: https://github.com/the-builders-burrow/pit-crew
- Example winning PR: https://github.com/Gigi3d/widget-api/pull/1

## Team

- <name>, <email>, <x / github / linkedin>

## Demo video

Under two minutes. Script in [VIDEO.md](VIDEO.md).

---

## Presenter notes (not for the judges' eyes)

The judges are mostly in DevRel. They will look at the repo, click the links, and reward a clean developer experience and honest engineering over hype.

- **Impact.** Say the pain plainly: performance PRs go unreviewed, code gets slower every release, a solo maintainer gets one guess per experiment. Name the expansion to security and legacy-to-agentic.
- **Technical execution.** The two referees (tests gate, benchmark ranks), the anti-cheat guard (a patch cannot touch its own grader), the clean-room re-verify. This is where you prove it is real, not a wrapper.
- **Creativity.** Parallel speculative execution for engineering work: run ten attempts, keep the winner, because compute is cheaper than a maintainer's afternoon. Lean on the pit-crew framing.
- **Presentation.** The live race, the voice command, "ten agents enter, one patch leaves." Own the room.

Sponsor usage is judged, and half the cash is in best-use prizes. Every integration here is load-bearing, not a bolt-on, so a placement can stack with side prizes. Say the safety story out loud: nothing runs on the user's machine, nothing merges without a human, the agent cannot edit its own grader, the winning number is independently reproduced.
