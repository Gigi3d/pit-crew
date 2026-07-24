# Tool setup before the hack

Everything below is done **before Friday**. Commands marked verified were taken from each vendor's current quickstart on 2026-07-22. Two items I could not verify are flagged in section 8.

The goal: at 10:00 you write race logic, not auth code.

---

## 1. What you can do now vs what waits for the day

Your participation credits (Daytona $100, Braintrust $250, Fireworks $50, ElevenLabs Creator month, CopilotKit Enterprise token, CodeRabbit trial) are handed out **at the event**. So:

| Now | Friday morning |
|---|---|
| Create every account on the free tier | Redeem credits onto the same accounts |
| Generate API keys, put them in `.env` | Re-check nothing rate-limits at zero balance |
| Install SDKs, run one smoke call each | Nothing else |

Do not wait for credits to set up. Free tiers are enough to prove your wiring works.

**Priority order (by judges + cash, from the event page).** Spend your time in this
order: **Daytona** (host, 2 judges, the core) > **CodeRabbit** (2 judges, $1,000
track, undertargeted) > **CopilotKit** (2 judges, $500 + Ray-Ban) > **Braintrust**
(co-host, an Eval Engineer judges it, $500) > **Fireworks** (1 judge, $500) >
**ElevenLabs** (no judge, no cash: garnish, do it last). Note that half the cash is
in the Best-Use side prizes, so meaningful integration is worth as much as placement.

---

## 2. Daytona (the one that can kill the project)

```bash
pip install daytona          # python
npm install @daytona/sdk     # typescript
export DAYTONA_API_KEY=...   # the SDK reads this automatically
```

Key from `app.daytona.io`. Smoke test:

```python
from daytona import Daytona
daytona = Daytona()
sandbox = daytona.create()
print(sandbox.process.code_run('print("hello")').result)
```

Defaults are 1 vCPU, 1GB RAM, 3GiB disk per sandbox, Linux containers, Python runtime.

### The concurrency test, do this first
Everything depends on 30 sandboxes existing at once. Spawn 30 no-op sandboxes tonight and **count how many you actually get**. If your plan caps at 10, you want to discover that now, and the deck says ten instead of thirty. This is the single highest-value hour of prep.

### Build the snapshot
Create a Daytona snapshot with `widget-api` and its dependencies already installed. Otherwise every bay spends 30 to 60 seconds on `pip install` and your race takes four minutes instead of twenty seconds. On stage, that difference is everything.

---

## 3. Fireworks AI (the patch generator)

```bash
pip install --pre fireworks-ai
export FIREWORKS_API_KEY=...
```

Key from `app.fireworks.ai/settings/users/api-keys`.

```python
from fireworks import Fireworks
client = Fireworks()
r = client.chat.completions.create(
    model="accounts/fireworks/models/deepseek-v3p1",
    messages=[{"role":"user","content":"Say hello"}],
)
print(r.choices[0].message.content)
```

`deepseek-v3p1` is their recommended general high-throughput model, which is the right default for 30 concurrent patch generations. Test **30 concurrent calls** before Friday, not one, since throughput is the thing you are betting on.

---

## 4. Braintrust (telemetry)

```bash
pip install braintrust        # or: npm install braintrust
export BRAINTRUST_API_KEY=sk-...
```

```python
from braintrust import Braintrust
bt = Braintrust(project_name="pitcrew")
with bt.trace(name="bay-12") as span:
    span.log(score=1.0)
```

Create the `pitcrew` project in their dashboard now so traces land somewhere named, not in a default bucket you have to find on stage.

**Do the eval, not just logging.** The co-host is Braintrust and the judge, Izzy
Hurley, is an Eval Engineer. `python -m pitcrew.evals` already scores which repair
strategy wins, at what reliability, DQs scored zero. It runs today with no key and
prints the leaderboard; with `BRAINTRUST_API_KEY` it also pushes the scores. That
scored eval is what wins this track, and it strengthens your Technical score too.

---

## 5. ElevenLabs (voice in and out)

```bash
pip install elevenlabs                  # python
npm install @elevenlabs/elevenlabs-js   # node
```

```python
from elevenlabs.client import ElevenLabs
client = ElevenLabs(api_key="...")
audio = client.text_to_speech.with_raw_response.convert(
    text="Copy. Twenty two bays retired.", voice_id="<pick one>")
```

**Lowest priority: no judge, no cash.** ElevenLabs is garnish that makes the demo
feel alive, not a pillar. Your keyless Web Speech voice-IN (in the Next.js UI)
already carries the "talk to your code" wow. Do ElevenLabs voice-OUT last, and cut
it first if you are behind.

**Pick your crew voice tonight and hard-code the `voice_id`.** Browsing the voice library live is a terrible use of stage time. Choose something clipped and radio-like.

Speech to text is the half that matters for idea 1, and I could not confirm its exact call signature from the docs I could reach (section 8). Budget 20 minutes to confirm it, and have the fallback ready: bind the same command to a text input, so a mic failure becomes typing rather than a dead demo.

---

## 6. CopilotKit (the actuator)

```bash
npx create-next-app@latest pitcrew-ui
cd pitcrew-ui
npm install @copilotkit/react-core @copilotkit/react-ui @copilotkit/runtime
```

Wrap the app in `<CopilotKit runtimeUrl="/api/copilotkit">`, add an API route using `CopilotRuntime`, and drop in `CopilotSidebar`.

**Point the runtime at Fireworks, not OpenAI.** The default quickstart wires `BuiltInAgent` to an OpenAI model. Using Fireworks there instead makes your Fireworks usage deeper and avoids introducing a seventh vendor nobody is judging.

The hook you actually need is `useCopilotAction`, which lets the LLM call a frontend function. That is what turns "kill everything slower than 300ms" into bays disappearing. Confirm its exact signature against their reference (section 8) and get **one trivial action working tonight**, for example an action that changes the page background. If that works, the race command is the same shape with a real handler.

---

## 7. CodeRabbit (best value on the board)

Not an SDK. It is a GitHub App.

1. Install CodeRabbit on the `widget-api` repo
2. Open one throwaway PR and confirm a review actually appears
3. Note how long it takes, so you know whether to trigger it before or during the pitch

Fifteen minutes of work for a $1,000 track that few teams will target. Do not skip it because it is not code.

---

## 8. What I could not verify, budget time for these

1. **ElevenLabs speech to text.** Their reachable API docs covered text to speech only. Confirm the transcription call yourself.
2. **`useCopilotAction` exact signature.** Their reference page 404'd for me. The concept is stable (name, description, parameters, handler, optional render), but confirm the current shape.

Both are on the critical path for idea 1, which is why the fallback matters: **CopilotKit action first, voice on top.** The action is the load-bearing half.

---

## 9. One file that proves the whole stack

Write `hello.py` (or `.ts`) that hits all four key-based services in one run and prints a line each. Run it the night before, then again at 09:45 on the venue wifi.

```
daytona    ok   sandbox 7f2a created and destroyed
fireworks  ok   142 tokens
braintrust ok   trace logged to project pitcrew
elevenlabs ok   1.2s audio generated
```

Four green lines means the morning is yours. If one fails, you know exactly which vendor to debug while everyone else is still reading docs.

---

## 10. Prep that is not an API

- **Test on the presentation laptop**, on the projector if you can. A 30-tile grid that looks great on a laptop can be unreadable at the back of a room.
- **Rehearse the voice command with crowd noise playing.** A venue at 4pm is loud and laptop mics degrade badly.
- **Have a headset mic** if you own one.
- **Screen-record a full successful race the night before.** If the wifi dies mid-pitch, you play the recording and narrate. Nobody is impressed by a spinner.
- **Download the five hotlinked sponsor logos locally** so the deck renders with the wifi off.
- **Charge everything, bring the dongle.**

The screen recording is the cheapest insurance on this list. Do it.
