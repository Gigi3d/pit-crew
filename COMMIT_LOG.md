# Build log

Each stage is one commit, pushed as it lands. Written for a judge reading the
history cold: what changed, why, and what was measured.

## Commit convention

```
<stage>: <what changed in one line>

<why it changed, and any number that was measured>
```

Stages: `preflight`, `race`, `ui`, `voice`, `telemetry`, `docs`.

Rules for today:
- Commit when a feature set **works**, not when it is typed. A green test or a
  measured number is the trigger.
- Put the measurement in the message. "10 bays, capped by CPU quota" beats
  "fixed concurrency".
- Push immediately. An unpushed commit is invisible to judges.
- Never commit `.env`, `.braintrust.json`, or anything under `.venv/`.

## Verified before the event

| Sponsor | Status | Measured |
|---|---|---|
| Daytona | green | 10 concurrent bays (CPU quota), 2.3s per bay |
| Fireworks | green | `deepseek-v4-pro`, 10/10 concurrent, p95 4.6s |
| Braintrust | green | logging to project `pitcrew` |
| ElevenLabs | blocked | key has no scopes |
| CopilotKit | pending | runtime not yet pointed at Fireworks |
| CodeRabbit | pending | needs PR on widget-api |

### Numbers that shape the demo

- **10 bays, not 30.** Account caps total CPU at 1. Confirmed at both 30 and 12
  requested. Re-test if credits lift the quota.
- **No snapshot needed.** Custom snapshots are denied on this plan, and it does
  not matter: widget-api needs only pytest, so a bay costs 2.3s cold. A
  snapshot would save under 2s.
- **Race time is the slowest bay, not the average.** Fireworks p50 is 3.2s but
  p95 is 4.6s. Quote 5s.
- **`deepseek-v3p1` does not exist.** SETUP.md's recommendation is stale; the
  account exposes 6 models. Chose `deepseek-v4-pro` on a real patch-generation
  prompt.

## Stages

- `preflight` - harness proving all four SDKs, target repo, measured limits
