# CodeRabbit Discord Challenge: the Pit Crew bot

The challenge wants something creative built around the CodeRabbit Discord bot,
for a $1,000 prize (plus more if it is genuinely interesting). Ours: **Pit Crew
drops the winning pull request into your team's Discord channel with a race GIF
attached**, so teammates and the CodeRabbit bot see the result in a form a human
can read, not just a bare link.

## The flow

```
PR opens on Gigi3d/widget-api        (a slow function lands)
        |
        v
Pit Crew reads it, 10 agents race    (each tries a different optimisation)
        |
        v
winning patch opens a PR             (back on Gigi3d/widget-api)
        |
        v
Pit Crew posts that PR to Discord    (embed + race GIF)
        |
        v
CodeRabbit reviews it, team reads it
```

The source repo is **Gigi3d/widget-api**: that is where the incoming PR comes
from and where the winning patch's PR opens. Pit Crew is the middle: it runs the
race and delivers the winner to the channel.

## What is built (in this repo)

| Piece | File | Does |
|---|---|---|
| Race GIF | `pitcrew/gif.py` | renders the race as an animated GIF from the real result |
| The bot | `pitcrew/pit_wall.py` | posts the winning PR + GIF to Discord via a webhook |
| Trigger | `pitcrew/serve.py` `POST /approve` | "approve the winner" opens the PR and fires the post |

Dry-run it now, no accounts needed (prints the payload instead of sending):

```bash
python3 -m pitcrew.pit_wall
```

Once `DISCORD_WEBHOOK_URL` is set in `.env`, the same command posts for real.

## Setup: the parts only you can do

The org is **the-builders-burrow** (https://github.com/the-builders-burrow).
The event instructions also say "working-ant" in one place; the-builders-burrow
is the live org, so use that. Confirm with their team if a repo create is refused.

1. **CodeRabbit account** - www.coderabbit.ai
2. **Join the Discord** - the invite link in the event instructions
3. **Accept the GitHub org invite** - check the inbox of the email you registered
   with; it invites you to `the-builders-burrow`
4. **Create a PUBLIC repo inside `the-builders-burrow`** (not your personal
   account, or CodeRabbit will not see it). Give every teammate access.
5. **Make a team channel** in the hackathon Discord
6. **Connect the repo** - run the CodeRabbit bot's GitHub OAuth in that channel,
   and confirm `the-builders-burrow` shows as connected
7. **Add the webhook** - that channel's Settings > Integrations > Webhooks > New
   Webhook > Copy URL, and paste it into `.env` as `DISCORD_WEBHOOK_URL`

Steps 1-3 and 6 are OAuth and account flows: they need your login, so they are
yours to do, not something the code can automate.

## Then it runs itself

```bash
# in .env: DISCORD_WEBHOOK_URL=...  and  PITCREW_PR_URL=...
python3 -m pitcrew.serve            # open http://localhost:8420, run a race
curl -X POST http://localhost:8420/approve   # or say "approve the winner" in the UI
```

The winning PR appears in your channel with the race GIF. CodeRabbit reviews the
PR on GitHub; your teammates read the result in Discord. That is the loop.

## Why it fits the brief

- It **uses** the CodeRabbit bot rather than reinventing review: Pit Crew hands
  it a real PR to chew on.
- The GIF makes an automated result **legible to humans** in the channel.
- It is the natural last mile of the whole product: ten agents race, one patch
  wins, and this is how it reaches the people who approve it.
