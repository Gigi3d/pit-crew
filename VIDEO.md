# Demo video script (under 2 minutes, required on Devpost)

This is the SUBMISSION video, a screen recording, separate from your 3-minute
live pitch. Judges may watch it without you in the room, so it has to stand alone.
It also doubles as your wifi-failure insurance for the live demo.

Target: 1:45. Record the real live console (`python -m pitcrew.serve`). Narrate in
your own voice, calm and confident. No music needed; the content carries it.

---

## Shot list

**0:00 to 0:12  · the hook**
On camera or voiceover, over the console at rest.
> "I run an open-source Bitcoin wallet. Strangers send me pull requests that have to
> be correct and fast, because slow loses users and wrong loses coins. I cannot
> benchmark every one by hand, so I built a pit crew. Watch thirty agents fix one in
> fifteen seconds."

**0:12 to 0:20  · the setup, one breath**
Point at the header: repo, PR #482, `parse_events()`.
> "One slow function. One pull request. Thirty sandboxes, each trying a different
> fix, all at once."

**0:20 to 0:45  · the race (let it breathe)**
Hit RUN. Say almost nothing. Let the grid fill: amber running, green passing,
grey disqualified.
> "Every bay writes a patch, runs the real test suite, then times itself. The grey
> ones broke a test and are out. Nobody is trusting the model; the tests decide."

**0:45 to 1:00  · the voice command (the wow)**
Speak into the mic:
> "Box, box. Kill everything slower than five milliseconds."
Grid visibly culls. Crew replies.
> "I just talked to my code and it obeyed."

**1:00 to 1:20  · the winner and the proof**
Winner lights up P1. Show the before/after and the clean-room line.
> "Bay seven wins. Eight hundred milliseconds down to under one. And here is the
> honest part: that number was re-measured in a fresh sandbox that never met the
> agent that wrote the patch. No cheating."

**1:20 to 1:35  · the loop closes**
Click Approve. Cut to the real GitHub PR with the CodeRabbit review on it.
> "Approve, and it opens a real pull request. CodeRabbit reviews it. The whole loop,
> problem to reviewed fix, ran while I was talking."

**1:35 to 1:45  · the line that lands**
Back to the winner card.
> "Thirty agents enter. One patch leaves. Pit Crew."

---

## Rules for the recording

- **Record the mock/live console**, not slides. Motion sells this.
- **One take of the race, uncut.** A visible real race beats a polished edit.
- **Say the sponsor names once, naturally**, where they do the work: Daytona
  (the thirty sandboxes), CodeRabbit (the review), Fireworks (the patches),
  Braintrust (the strategy scores), CopilotKit (the voice command). The Devpost
  text lists them formally; the video just shows them earning their place.
- **Keep it under 2:00 hard.** Overruns get cut off. Aim 1:45 for margin.
- **End on the tagline**, not a fade. Last frame should be the winner card.

## If the live race is flaky when you record

Record the `python -m pitcrew.serve` console; it runs the mock end to end with no
keys and looks identical. An honest mock recording that plays is worth more than a
real race that stutters on camera.
