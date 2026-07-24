# Everything to install, from a bare macOS laptop

Assumes a brand-new Mac with nothing but a browser and a terminal. Runs top to bottom. Nothing here needs the venue wifi except the account signups, so do it the night before.

Pit Crew does **not** need Docker. Daytona runs the sandboxes in its cloud over an API, so there is no local container runtime to install.

---

## 1. System layer

```bash
# Apple command line tools (gives you git and a compiler)
xcode-select --install

# Homebrew, the package manager everything else comes from
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
# then follow its final "Next steps" to add brew to your PATH

# the toolchain
brew install git gh node python
```

That gives you: `git`, `gh` (GitHub CLI, needed for the PR flow), `node` + `npm` + `npx` (for the CopilotKit UI), and `python3` + `pip3` (for the orchestrator).

Verify:

```bash
git --version && gh --version && node --version && npm --version && python3 --version
```

---

## 2. Authenticate GitHub

```bash
gh auth login          # pick GitHub.com, HTTPS, login via browser
```

Needed to create `widget-api`, push branches, and open PR #1 and PR #2 from the command line.

---

## 3. Python side (the orchestrator and the target repo)

```bash
pip3 install --pre fireworks-ai          # ships as a pre-release, needs --pre
pip3 install daytona braintrust elevenlabs fastapi "uvicorn[standard]" python-dotenv pytest
```

What each is for:

| Package | Role |
|---|---|
| `daytona` | spawn the 10 parallel sandboxes |
| `fireworks-ai` | generate the 10 candidate patches |
| `braintrust` | log and score each bay |
| `elevenlabs` | voice in (speech to text) and out (TTS) |
| `fastapi` + `uvicorn` | serve live race state to the UI over websocket |
| `python-dotenv` | load `.env` |
| `pytest` | the target repo's correctness gate |

---

## 4. Node side (the CopilotKit UI)

The UI is a Next.js app. Create it once, night before:

```bash
npx create-next-app@latest pitcrew-ui     # accept defaults
cd pitcrew-ui
npm install @copilotkit/react-core @copilotkit/react-ui @copilotkit/runtime
```

Everything else on the Node side is pulled in by `create-next-app` (React, Next, the dev server). No global npm installs needed.

You can drop the existing `ui/index.html` design in as the page, or keep it standalone and only use the Next app for the CopilotKit action wiring. Decide based on time.

---

## 5. Accounts and API keys (free tier now, credits at the event)

Sign up and generate a key for each. Put them all in one `.env`:

```
DAYTONA_API_KEY=...        # app.daytona.io
FIREWORKS_API_KEY=...      # app.fireworks.ai/settings/users/api-keys
BRAINTRUST_API_KEY=sk-...  # braintrust.dev
ELEVENLABS_API_KEY=...     # elevenlabs.io
```

Plus two that are not keys:
- **GitHub** account, authed in step 2
- **CopilotKit** Enterprise token, handed out at the event; the free path works without it for the demo
- **CodeRabbit**, installed as a GitHub App on `widget-api` (not a key, not an SDK)

---

## 6. Prove it (the one file that de-risks the morning)

Write `hello.py` that hits all four SDKs in one run and prints a line each. Run it the night before, and again on the venue wifi at 09:45. Four green lines means the morning is yours. See SETUP.md section 9 for the expected output.

---

## 7. Not an install, but on the critical path

- **Screen recorder**: built into macOS, `Cmd+Shift+5`. Record a full successful race the night before as your wifi-failure insurance.
- **A headset mic** for the voice command, if you own one. The venue is loud.
- **The Daytona concurrency test**: spawn 30 no-op sandboxes and count how many you actually get. Do this the moment your key works. Everything assumes that number.

---

## The whole thing as one block

```bash
xcode-select --install
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install git gh node python
gh auth login
pip3 install --pre fireworks-ai
pip3 install daytona braintrust elevenlabs fastapi "uvicorn[standard]" python-dotenv pytest
npx create-next-app@latest pitcrew-ui && cd pitcrew-ui
npm install @copilotkit/react-core @copilotkit/react-ui @copilotkit/runtime
```

Then: create the four accounts, fill `.env`, run `hello.py`, run the Daytona concurrency test.
