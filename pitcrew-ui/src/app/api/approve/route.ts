// "Approve the winner" -> the engine opens PR #2 against widget-api.
//
// The openWinnerPR copilot action POSTs here. This proxies to the Python engine,
// which owns the git/gh side. Kept as a thin pass-through so the browser never
// needs a GitHub token and the UI has one place to call regardless of where the
// engine runs.
//
// The engine endpoint (POST /approve on pitcrew/serve.py) is not built yet, so
// this fails soft with a clear message rather than a raw 404 mid-demo.
import { NextRequest } from "next/server";

export const dynamic = "force-dynamic";

const ENGINE = process.env.ENGINE_URL ?? "http://localhost:8420";

export const POST = async (_req: NextRequest) => {
  try {
    const res = await fetch(`${ENGINE}/approve`, { method: "POST" });
    if (!res.ok) {
      return Response.json(
        { ok: false, error: `engine returned ${res.status}` },
        { status: 502 },
      );
    }
    return Response.json(await res.json().catch(() => ({ ok: true })));
  } catch {
    return Response.json(
      { ok: false, error: "engine unreachable" },
      { status: 503 },
    );
  }
};
