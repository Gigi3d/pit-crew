"""Put an API key into .env without it touching your shell history or screen.

    ./.venv/bin/python setkey.py DAYTONA_API_KEY

Prompts with no echo, then rewrites that one line in .env. Handles keys
containing / & $ or other characters that would break a sed one-liner, and
never prints the value back.
"""

import sys
from getpass import getpass
from pathlib import Path

VALID = {
    "DAYTONA_API_KEY",
    "FIREWORKS_API_KEY",
    "BRAINTRUST_API_KEY",
    "ELEVENLABS_API_KEY",
    "ELEVENLABS_VOICE_ID",
    "DISCORD_WEBHOOK_URL",
    "PITCREW_PR_URL",
}

if len(sys.argv) != 2:
    sys.exit(f"usage: setkey.py <VAR>\n  one of: {', '.join(sorted(VALID))}")

var = sys.argv[1].upper()
if var not in VALID:
    sys.exit(f"{var} is not one of: {', '.join(sorted(VALID))}")

# .env lives at the repo root, one level up from this tools/ dir.
env = Path(__file__).resolve().parent.parent / ".env"
if not env.is_file():
    sys.exit(".env not found - copy it from .env.example first")

value = getpass(f"{var} (input hidden): ").strip()
if not value:
    sys.exit("empty, nothing changed")

lines = env.read_text().splitlines()
for i, line in enumerate(lines):
    if line.startswith(f"{var}="):
        lines[i] = f"{var}={value}"
        break
else:
    lines.append(f"{var}={value}")

env.write_text("\n".join(lines) + "\n")
env.chmod(0o600)  # readable only by you
print(f"{var} written to .env ({len(value)} chars). File is now chmod 600.")
