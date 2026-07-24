# tools

Preflight and measurement scripts. None are needed for the race itself - they
exist to prove a service works, and to produce the numbers the demo is designed
around. All read `.env` from the repo root.

| Script | What it answers |
|---|---|
| `setkey.py` | writes one API key to `.env` with hidden input, never touching shell history |
| `concurrency_test.py` | how many Daytona bays do you actually get? |
| `daytona_smoke.py` | does one bay work end to end, and where does its time go? |
| `fireworks_load_test.py` | does Fireworks hold up under N concurrent calls? |
| `voice.py` | ElevenLabs TTS/STT, and picking the crew voice |

## Measured on 2026-07-24

- **10 bays, not 30.** The account caps total CPU at 1. Confirmed at both 30 and
  12 requested. Everything in the decks assumes 30 - re-run this before
  presenting and change the number if it has not lifted.
- **2.3s per bay** cold (0.4s spawn + 1.6s pip + 0.2s verify). Custom snapshots
  are denied on this plan, but it does not matter: the target needs only pytest,
  so a snapshot would save under 2s.
- **Fireworks p95 4.6s** at 10 concurrent, 10/10 succeeded. `deepseek-v3p1` from
  SETUP.md does not exist; the account exposes 6 models and `deepseek-v4-pro`
  was fastest on the real patch prompt.
- **Race time is the slowest bay, not the mean.** p50 3.2s vs p95 4.6s - quote 5s.

## Usage

```bash
python3 tools/setkey.py DAYTONA_API_KEY
python3 tools/concurrency_test.py 30
python3 tools/daytona_smoke.py
python3 tools/fireworks_load_test.py 10
python3 tools/voice.py voices
```
