"""Render an animated GIF of a race, for the Discord post.

The bot attaches this so anyone reading the channel sees the race, not just a
link. It mirrors the deck's grid: tiles flip from queued to running to green,
the winner lands gold, everything else dims.

    from pitcrew.gif import render_race_gif
    render_race_gif(result, "assets/race.gif")

Falls back to a synthetic race if given no result, so it always produces
something to attach.
"""
from __future__ import annotations

import os
from typing import Optional

from PIL import Image, ImageDraw

# Deck palette.
BG = (11, 12, 16)
DIM = (40, 42, 50)
RUN = (210, 150, 40)
LEGAL = (40, 170, 90)
GOLD = (240, 210, 90)
DQ = (70, 40, 44)
TEXT = (230, 232, 238)


def _grid(n: int) -> tuple[int, int]:
    """Columns and rows for n tiles, favouring a wide layout."""
    cols = 5 if n <= 10 else 6
    rows = (n + cols - 1) // cols
    return cols, rows


def render_race_gif(
    result=None,
    out_path: str = "assets/race.gif",
    n_bays: int = 10,
    winner_bay: Optional[int] = None,
    cell: int = 96,
    pad: int = 10,
) -> str:
    """Write an animated GIF and return its path.

    `result` is an optional RaceResult; if absent, a plausible race is faked so
    the asset always exists (useful before a live race has been run).
    """
    # Pull lap times and the winner from a real result when we have one.
    laps: dict[int, int] = {}
    if result is not None:
        for r in getattr(result, "results", []):
            laps[r.bay] = int(r.candidate_ms) if r.candidate_ms else 0
        n_bays = len(laps) or n_bays
        if getattr(result, "winner", None):
            winner_bay = result.winner.bay
    if not laps:  # synthetic fallback
        laps = {b: 400 - b * 12 for b in range(1, n_bays + 1)}
        winner_bay = winner_bay or 1

    cols, rows = _grid(n_bays)
    W = cols * cell + pad * 2
    H = rows * cell + pad * 2 + 40  # header strip

    order = sorted(laps, key=lambda b: laps[b])  # fastest finish first
    frames: list[Image.Image] = []
    FRAMES = 28

    for f in range(FRAMES):
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        d.text((pad, pad), "PIT CREW   |   every PR gets a pit stop", fill=TEXT)

        # How far through the race this frame is, as a count of finished bays.
        finished = int((f / (FRAMES - 1)) * n_bays)
        done = set(order[:finished])
        reveal_winner = f > FRAMES * 0.75

        for i, b in enumerate(sorted(laps)):
            c, rrow = i % cols, i // cols
            x = pad + c * cell
            y = pad + 30 + rrow * cell
            box = [x + 4, y + 4, x + cell - 4, y + cell - 4]

            if b == winner_bay and reveal_winner:
                color = GOLD
            elif b in done:
                color = LEGAL
            elif finished > 0 and i == finished:
                color = RUN  # the one crossing the line this frame
            else:
                color = DIM
            d.rounded_rectangle(box, radius=8, fill=color)

            label = f"bay {b:02d}"
            d.text((x + 12, y + 12), label, fill=BG if color in (GOLD, LEGAL) else TEXT)
            if b in done or (b == winner_bay and reveal_winner):
                d.text((x + 12, y + cell - 24), f"{laps[b]}ms",
                       fill=BG if color in (GOLD, LEGAL) else TEXT)

        frames.append(img)

    # Hold the final frame so the winner reads.
    frames += [frames[-1]] * 8

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    frames[0].save(
        out_path,
        save_all=True,
        append_images=frames[1:],
        duration=90,
        loop=0,
        optimize=True,
    )
    return out_path


if __name__ == "__main__":
    path = render_race_gif(out_path="assets/race.gif")
    print(f"wrote {path} ({os.path.getsize(path):,} bytes)")
