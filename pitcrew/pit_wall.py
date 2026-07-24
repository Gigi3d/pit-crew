"""Pit Crew's Discord voice: post the winning PR to the team channel.

The race picks a winner and opens a pull request. This drops that PR into the
hackathon Discord channel with a race GIF attached, so teammates (and the
CodeRabbit bot watching the channel) see the result in a form a human can read,
not just a raw link.

    from pitcrew.pit_wall import announce
    announce(pr_url="https://github.com/the-builders-burrow/…/pull/1",
             baseline_ms=619, candidate_ms=9, strategy="set + join + sort once")

Uses a Discord webhook (Server Settings -> Integrations -> Webhooks -> New).
No bot token, no OAuth. Set DISCORD_WEBHOOK_URL in .env. With no webhook set it
prints the payload instead of sending, so it is safe to dry-run.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

import httpx

from .gif import render_race_gif


def _load_env() -> None:
    """Read repo-root .env into the environment, no dependency required.

    Only fills vars that are not already set, so a real shell export always wins.
    """
    env = Path(__file__).resolve().parent.parent / ".env"
    if not env.is_file():
        return
    for line in env.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        # Drop inline comments and surrounding quotes from example-style lines.
        val = val.split("#", 1)[0].strip().strip('"').strip("'")
        # Skip blanks: an empty line in .env must not shadow a code default.
        if val:
            os.environ.setdefault(key.strip(), val)


_load_env()

BRAND = 0xF2D25A  # pit-crew gold


def _embed(pr_url, baseline_ms, candidate_ms, strategy, tests_ok):
    speedup = (baseline_ms / candidate_ms) if candidate_ms else 0
    return {
        "title": "Winner is in. PR is open.",
        "url": pr_url,
        "description": (
            f"Ten agents raced. The fastest legal patch won and its pull "
            f"request is up for review.\n\n**[Open the PR]({pr_url})**"
        ),
        "color": BRAND,
        "fields": [
            {"name": "Strategy", "value": strategy or "n/a", "inline": False},
            {"name": "Before", "value": f"{baseline_ms:.0f} ms", "inline": True},
            {"name": "After", "value": f"{candidate_ms:.0f} ms", "inline": True},
            {"name": "Speedup", "value": f"{speedup:.0f}x", "inline": True},
            {
                "name": "Tests",
                "value": "green, re-verified clean-room" if tests_ok else "FAILED",
                "inline": False,
            },
        ],
        "footer": {"text": "Pit Crew - every PR gets a pit stop"},
        "image": {"url": "attachment://race.gif"},
    }


def announce(
    pr_url: str,
    baseline_ms: float,
    candidate_ms: float,
    strategy: str = "",
    tests_ok: bool = True,
    result=None,
    gif_path: Optional[str] = None,
    webhook_url: Optional[str] = None,
) -> bool:
    """Post the winning PR to Discord. Returns True if delivered."""
    webhook_url = webhook_url or os.getenv("DISCORD_WEBHOOK_URL")

    # Make the GIF from the real result when we have one, else a synthetic race.
    gif_path = gif_path or render_race_gif(result, out_path="assets/race.gif")
    embed = _embed(pr_url, baseline_ms, candidate_ms, strategy, tests_ok)
    payload = {"embeds": [embed], "username": "Pit Crew"}

    if not webhook_url:
        print("DISCORD_WEBHOOK_URL not set - dry run. Would post:")
        print(json.dumps(embed, indent=2))
        print(f"with attachment: {gif_path}")
        return False

    # Discord takes the embed as payload_json and the GIF as a multipart file;
    # the embed references it via attachment://race.gif.
    with open(gif_path, "rb") as f:
        files = {
            "payload_json": (None, json.dumps(payload), "application/json"),
            "files[0]": ("race.gif", f, "image/gif"),
        }
        resp = httpx.post(webhook_url, files=files, timeout=30)

    if resp.status_code >= 300:
        print(f"Discord rejected the post: {resp.status_code} {resp.text[:200]}")
        return False
    print("Posted the winning PR to Discord.")
    return True


if __name__ == "__main__":
    # Dry-run with the numbers from the real widget-api fix. The PR opens on
    # Gigi3d/widget-api - the repo the incoming PR came from.
    announce(
        pr_url=os.getenv("PITCREW_PR_URL",
                         "https://github.com/Gigi3d/widget-api/pull/1"),
        baseline_ms=619,
        candidate_ms=9,
        strategy="set + join + sort once",
        tests_ok=True,
    )
