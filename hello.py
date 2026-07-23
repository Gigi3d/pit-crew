"""Four green lines means the morning is yours.

Run it the night before, and again on the venue wifi at 09:45:

    ./.venv/bin/python hello.py

Each SDK is probed independently, so one dead key never hides the other three.
Every check is synchronous and network-real: nothing here can report green on a
key that would fail during the race.
"""

import logging
import os
import sys

from dotenv import load_dotenv

load_dotenv()

# Braintrust's background logger retries on a worker thread and dumps a full
# traceback per attempt. We validate it synchronously below instead.
logging.getLogger("braintrust").setLevel(logging.CRITICAL)

PASS = "\033[32mPASS\033[0m"
FAIL = "\033[31mFAIL\033[0m"

# SETUP.md section 3: deepseek-v3p1 is Fireworks' recommended high-throughput
# model, which is what 30 concurrent patch generations needs. Override in .env
# if it is retired.
FIREWORKS_MODEL = os.getenv(
    "FIREWORKS_MODEL", "accounts/fireworks/models/deepseek-v3p1"
)

# SETUP.md section 4 calls this project 'pitcrew'. It must match the project you
# create in the dashboard, or traces land somewhere you have to hunt for on stage.
BRAINTRUST_PROJECT = os.getenv("BRAINTRUST_PROJECT", "pitcrew")

results = []


def probe(name, key_env, fn):
    """Run one SDK's smoke check and record the outcome."""
    key = os.getenv(key_env)
    if not key or key.startswith("#"):
        results.append((name, False))
        print(f"{FAIL}  {name:<11} {key_env} is not set in .env")
        return
    try:
        detail = fn(key)
        results.append((name, True))
        print(f"{PASS}  {name:<11} {detail}")
    except Exception as e:
        results.append((name, False))
        print(f"{FAIL}  {name:<11} {type(e).__name__}: {str(e)[:88]}")


def check_daytona(key):
    from daytona import Daytona, DaytonaConfig

    client = Daytona(DaytonaConfig(api_key=key))
    sandboxes = list(client.list())  # .list() is a generator
    return f"reachable, {len(sandboxes)} sandbox(es) currently up"


def check_fireworks(key):
    import httpx
    from fireworks import Fireworks

    # The SDK reports account-level problems as a generic 404 "Model not found",
    # which sends you hunting for a model-name bug that isn't there. Probe the
    # REST endpoint first so billing/suspension errors say what they mean.
    r = httpx.get(
        "https://api.fireworks.ai/inference/v1/models",
        headers={"Authorization": f"Bearer {key}"},
        timeout=30,
    )
    if r.status_code == 401:
        raise RuntimeError("key rejected (401) - wrong or truncated key")
    if r.status_code == 412:
        msg = r.json().get("error", {}).get("message", "")
        raise RuntimeError(f"ACCOUNT BLOCKED (412): {msg[:110]}")
    r.raise_for_status()

    client = Fireworks(api_key=key)
    resp = client.chat.completions.create(
        model=FIREWORKS_MODEL,
        messages=[{"role": "user", "content": "Reply with the single word: green"}],
        max_tokens=8,
    )
    word = resp.choices[0].message.content.strip()
    return f"auth ok, {FIREWORKS_MODEL.split('/')[-1]} returned {word!r}"


def check_braintrust(key):
    import braintrust

    braintrust.login(api_key=key)  # synchronous, raises on a bad key
    logger = braintrust.init_logger(project=BRAINTRUST_PROJECT, api_key=key)
    logger.log(input="hello", output="world", scores={"smoke": 1.0})
    logger.flush()
    return f"authenticated, one event logged to project {BRAINTRUST_PROJECT!r}"


def check_elevenlabs(key):
    from elevenlabs.client import ElevenLabs

    client = ElevenLabs(api_key=key)
    voices = client.voices.get_all()
    return f"reachable, {len(voices.voices)} voice(s) available"


print("\nPit Crew preflight\n" + "-" * 54)

probe("Daytona", "DAYTONA_API_KEY", check_daytona)
probe("Fireworks", "FIREWORKS_API_KEY", check_fireworks)
probe("Braintrust", "BRAINTRUST_API_KEY", check_braintrust)
probe("ElevenLabs", "ELEVENLABS_API_KEY", check_elevenlabs)

print("-" * 54)
good = sum(1 for _, ok in results if ok)
print(f"{good}/4 green\n")
sys.exit(0 if good == 4 else 1)
