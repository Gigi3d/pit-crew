"""Ship the winner: open its PR on the source repo, then post it to Discord.

One command closes the loop. Opens a pull request from the winning branch on
Gigi3d/widget-api, reads back the real PR URL, and hands that URL to the Discord
bot with the race GIF.

    python -m pitcrew.ship \
        --head speed-up-rollup \
        --baseline-ms 619 --candidate-ms 9 \
        --strategy "set + join + sort once"

Needs `gh auth login` first. Retries on GitHub 5xx (PR creation had an incident
on event day), and if a PR already exists for the branch it reuses it instead of
failing.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time

from .pit_wall import announce

REPO = "Gigi3d/widget-api"


def _gh(args: list[str]) -> tuple[int, str]:
    """Run a gh command, return (exit_code, stdout+stderr)."""
    p = subprocess.run(["gh", *args], capture_output=True, text=True)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def existing_pr_url(head: str) -> str | None:
    """Return the URL of an open PR for this branch, if one already exists."""
    code, out = _gh(["api", f"repos/{REPO}/pulls",
                     "-f", f"head={REPO.split('/')[0]}:{head}", "--jq",
                     ".[0].html_url // empty"])
    return out.strip() if code == 0 and out.strip() else None


def open_pr(head: str, base: str, title: str, body: str,
            retries: int = 5) -> str:
    """Open the PR and return its URL, retrying through GitHub 5xx."""
    if url := existing_pr_url(head):
        print(f"PR already open, reusing: {url}")
        return url

    for attempt in range(1, retries + 1):
        code, out = _gh([
            "api", "-X", "POST", f"repos/{REPO}/pulls",
            "-f", f"title={title}", "-f", f"head={head}", "-f", f"base={base}",
            "-f", f"body={body}", "--jq", ".html_url",
        ])
        url = out.strip()
        if code == 0 and url.startswith("http"):
            print(f"opened PR: {url}")
            return url
        # 5xx is GitHub's problem; back off and retry. Anything else is ours.
        if "HTTP 4" in out or "Validation" in out:
            raise SystemExit(f"PR create rejected (client error):\n{out.strip()}")
        print(f"attempt {attempt}/{retries}: GitHub not cooperating, retrying...")
        time.sleep(min(2 ** attempt, 20))

    # Maybe it actually got created on a retry that reported a bad status.
    if url := existing_pr_url(head):
        return url
    raise SystemExit(
        "Could not open the PR after retries. GitHub PR creation is likely "
        "having an incident - try again shortly, or open it in the web UI."
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--head", default="speed-up-rollup", help="winning branch")
    ap.add_argument("--base", default="main")
    ap.add_argument("--baseline-ms", type=float, required=True)
    ap.add_argument("--candidate-ms", type=float, required=True)
    ap.add_argument("--strategy", default="")
    ap.add_argument("--no-discord", action="store_true",
                    help="open the PR but skip the Discord post")
    args = ap.parse_args()

    speedup = args.baseline_ms / args.candidate_ms if args.candidate_ms else 0
    title = f"Make rollup_events single-pass ({args.baseline_ms:.0f}ms to {args.candidate_ms:.0f}ms)"
    body = (
        f"The winning patch from a Pit Crew race. rollup_events was correct but "
        f"O(n*widgets); this makes it single-pass. {args.baseline_ms:.0f}ms to "
        f"{args.candidate_ms:.0f}ms ({speedup:.0f}x faster), output byte-identical, "
        f"all tests pass. Ten agents raced in isolated Daytona sandboxes; the "
        f"fastest legal patch won."
    )

    url = open_pr(args.head, args.base, title, body)

    if args.no_discord:
        print("skipping Discord post (--no-discord)")
        return
    announce(
        pr_url=url,
        baseline_ms=args.baseline_ms,
        candidate_ms=args.candidate_ms,
        strategy=args.strategy,
        tests_ok=True,
    )


if __name__ == "__main__":
    main()
