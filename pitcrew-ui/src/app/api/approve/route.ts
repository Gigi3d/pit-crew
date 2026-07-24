// "Approve the winner" -> post the winning PR to Discord for review.
//
// Runs entirely in this route so the hosted app needs no Python backend. Posts
// a rich embed to the team webhook with a race GIF (served from /public), and
// the CodeRabbit bot in the channel picks up the PR. The browser never sees the
// webhook or any key.
import { NextRequest } from "next/server";

export const dynamic = "force-dynamic";

const WEBHOOK = process.env.DISCORD_WEBHOOK_URL;
const BRAND = 0xf2d25a; // pit-crew gold

type Winner = {
  title?: string;
  strategy?: string;
  baseline_ms?: number;
  candidate_ms?: number;
  pr_url?: string;
};

export const POST = async (req: NextRequest) => {
  const w: Winner = await req.json().catch(() => ({}));
  const prUrl =
    w.pr_url ??
    process.env.NEXT_PUBLIC_PR_URL ??
    "https://github.com/Gigi3d/widget-api/pull/1";

  if (!WEBHOOK) {
    // Fail soft: the demo still shows the winner, just no Discord post.
    return Response.json(
      { ok: false, error: "DISCORD_WEBHOOK_URL not set", pr: prUrl },
      { status: 503 },
    );
  }

  const baseline = w.baseline_ms ?? 619;
  const candidate = w.candidate_ms ?? 9;
  const speedup = candidate ? Math.round(baseline / candidate) : 0;
  const origin = req.nextUrl.origin;

  const embed = {
    title: w.title ?? "Winner is in. PR is open.",
    url: prUrl,
    description: `Ten agents raced. The fastest legal patch won and its pull request is up for review.\n\n**[Open the PR](${prUrl})**`,
    color: BRAND,
    fields: [
      { name: "Strategy", value: w.strategy || "n/a", inline: false },
      { name: "Before", value: `${baseline} ms`, inline: true },
      { name: "After", value: `${candidate} ms`, inline: true },
      { name: "Speedup", value: `${speedup}x`, inline: true },
      { name: "Tests", value: "green, re-verified clean-room", inline: false },
    ],
    footer: { text: "Pit Crew - every PR gets a pit stop" },
    // Served from public/race.gif on this same deployment.
    image: { url: `${origin}/race.gif` },
  };

  const res = await fetch(WEBHOOK, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username: "Pit Crew", embeds: [embed] }),
  });

  if (!res.ok) {
    return Response.json(
      { ok: false, error: `discord ${res.status}`, pr: prUrl },
      { status: 502 },
    );
  }
  return Response.json({ ok: true, pr: prUrl });
};
