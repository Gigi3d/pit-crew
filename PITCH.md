# 3-minute live pitch (solo, in the jersey)

Built for a charismatic solo presenter. The deck is bookends; the **live console is
the centre**. Do not click through 13 slides. Run the race for real and narrate it
like a pit-wall engineer. Total 3:00, aim to land at 2:50 for breathing room.

Story spine: you are the founder of an open-source Bitcoin wallet. This is a tool
you built for your own repo, and every maintainer has the same problem.

---

## 0:00 to 0:25  · who you are (slide 1)
Stand still. Own the room before the first word.

> "I run BitMask, an open-source Bitcoin wallet. Real people keep real money in it.
> And like every open-source project, I get pull requests from contributors I have
> never met. Every single one has to be two things: correct, and fast. A slow wallet
> loses users. A wrong one loses coins."

Beat.

> "I am one founder. I cannot hand-benchmark every pull request at two in the morning.
> So I built a pit crew."

## 0:25 to 0:40  · the idea (slide 3)
> "When a PR touches a hot function, I do not send one agent to fix it and hope.
> I send thirty. Each tries a different optimisation, in its own sandbox, all at
> once. The test suite decides who is even allowed to play. Fastest legal patch wins.
> Watch."

## 0:40 to 1:15  · the race, LIVE (the console)
Hit RUN. Step back. Let the grid do the talking. Narrate lightly.

> "Thirty bays. Each one writes a patch on Fireworks, applies it in a Daytona
> sandbox, and runs my real tests. Green passed. The grey ones..." (point) "...broke
> a test and are disqualified. I am not trusting the model. The tests are trusting it
> for me."

## 1:15 to 1:30  · talk to your code (LIVE, the wow)
Lean into the mic.

> "Box, box. Kill everything slower than five milliseconds."

Grid culls. Crew voice replies.

> "That is CopilotKit turning my voice into a real command, and my crew answering on
> the radio. I just talked to my codebase and it listened."

## 1:30 to 1:55  · the winner and the honest part (winner card)
Winner lights P1.

> "Bay seven takes it. Eight hundred milliseconds down to under one. Now here is the
> part I care about, because this is money software." (tap the clean-room line) "That
> number was re-measured in a fresh sandbox that never met the agent that wrote the
> patch. And Braintrust scored every strategy, so my crew gets smarter every race.
> No self-grading. No cheating."

## 1:55 to 2:20  · close the loop (LIVE → GitHub)
Click Approve. Cut to the real PR with CodeRabbit's review.

> "I approve, and it opens a real pull request against my repo. CodeRabbit reviews it
> before it can merge. The whole loop, a slow PR to a reviewed, faster, verified fix,
> ran while I was talking to you."

## 2:20 to 2:40  · safe, and bigger than me (slide 11, then 13)
> "Nothing ran on my laptop. Nothing merged without me. The agent could never touch
> its own tests. That is the only way I would let thirty strangers near a Bitcoin
> wallet." Beat. "I built this for bitmask-core. But every open-source maintainer on
> earth is drowning in the same PRs. Free for one repo, paid per team, and it markets
> itself: every fix it opens is signed by the crew."

## 2:40 to 3:00  · the line
Back to the winner card. Slow down. Land it.

> "Thirty mechanics. One car. Four seconds. Thirty agents enter, one patch leaves.
> Pit Crew."

Stop talking. Let it sit.

---

## Delivery notes
- **The jersey is the costume. Commit to it.** You are the race engineer, not a founder reading slides.
- **The live race is the whole demo.** If it is running, you are winning. Slides are punctuation.
- **Name each sponsor once, where it earns its place** (Fireworks writes, Daytona isolates, CopilotKit hears, Braintrust scores, CodeRabbit reviews). Never read a sponsor list out loud; show them working.
- **Say "money software" once.** It is why the safety and the clean-room verification matter more here than for any toy demo, and it is true.
- **If the mic fails**, type the command without breaking stride: "let me just type it, same thing." Never apologise, never freeze.
- **If the live race stutters**, cut to the recorded run and keep narrating. Nobody can tell if you do not flinch.

## The one honest sentence to have ready
If a judge asks whether it races the real Rust repo: "The engine is language-agnostic,
a bay just runs cargo instead of pytest. For a reliable fifteen-second stage demo I am
racing it on a representative function. Same engine, same race." True, and it disarms
the question instead of dodging it.
