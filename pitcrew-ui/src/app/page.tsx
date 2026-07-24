"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { CopilotSidebar } from "@copilotkit/react-ui";
import { useRaceActions, type Bay } from "@/components/useRaceActions";
import { runSimRace, pickPR, type SimPR } from "@/lib/race";

// If a live Python engine is deployed, point at it. Otherwise the console runs
// the race client-side so the hosted demo needs no backend.
const ENGINE = process.env.NEXT_PUBLIC_ENGINE_URL;

export default function Console() {
  const [bays, setBays] = useState<Record<number, Bay>>({});
  const [connected, setConnected] = useState(false);
  const [winner, setWinner] = useState<string | null>(null);
  const [pr, setPr] = useState<SimPR | null>(null);
  const [posted, setPosted] = useState<string | null>(null);

  const apply = useCallback((ev: any) => {
    if (ev.type === "bay") {
      setBays((prev) => ({ ...prev, [ev.bay]: { ...prev[ev.bay], ...ev } }));
    } else if (ev.type === "winner") {
      setWinner(`bay ${ev.bay} · ${ev.strategy}`);
    }
  }, []);

  // Live engine when configured, else a client-side race.
  useEffect(() => {
    setPr(pickPR());
    if (ENGINE) {
      const source = new EventSource(`${ENGINE}/events`);
      source.onopen = () => setConnected(true);
      source.onerror = () => setConnected(false);
      source.onmessage = (e) => {
        try {
          apply(JSON.parse(e.data));
        } catch {
          /* a malformed frame must never kill the console mid-demo */
        }
      };
      return () => source.close();
    }
    setConnected(true);
    const stop = runSimRace(apply);
    return stop;
  }, [apply]);

  // Deterministic handler: the model only extracts the number, this does the
  // work. That split is why the typed fallback behaves identically to voice.
  const killBays = useCallback((predicate: (b: Bay) => boolean) => {
    let killed = 0;
    setBays((prev) => {
      const next = { ...prev };
      for (const b of Object.values(prev)) {
        if (predicate(b)) {
          next[b.bay] = { ...b, state: "killed" };
          killed++;
        }
      }
      return next;
    });
    return killed;
  }, []);

  // "Approve the winner" posts the PR to Discord via the API route.
  const approve = useCallback(async () => {
    const res = await fetch("/api/approve", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(pr),
    });
    const data = await res.json().catch(() => ({}));
    setPosted(data.pr ?? pr?.pr_url ?? "posted");
    return data;
  }, [pr]);

  useRaceActions(bays, killBays, approve, (msg) => {
    // Speak the crew's reply if TTS is wired; harmless if not.
    fetch("/api/tts", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: msg }),
    })
      .then((r) => (r.ok ? r.blob() : null))
      .then((b) => b && new Audio(URL.createObjectURL(b)).play().catch(() => {}))
      .catch(() => {});
  });

  const rows = useMemo(
    () => Object.values(bays).sort((a, b) => a.bay - b.bay),
    [bays],
  );

  return (
    <main className="flex-1 p-6 font-mono">
      <header className="flex items-baseline gap-4 mb-6">
        <h1 className="text-2xl font-bold">PIT CREW</h1>
        {pr && <span className="text-xs opacity-60 truncate">{pr.title}</span>}
        <span className="ml-auto text-xs">
          {connected ? "racing" : "engine offline"}
        </span>
      </header>

      {winner && (
        <div className="mb-4 border px-3 py-2 text-sm flex items-center gap-3">
          <span className="font-bold">P1 {winner}</span>
          {pr && (
            <span className="opacity-70">
              {pr.baseline_ms}ms → {pr.candidate_ms}ms
            </span>
          )}
          {posted && (
            <a
              href={posted}
              target="_blank"
              rel="noreferrer"
              className="ml-auto underline"
            >
              posted to Discord ↗
            </a>
          )}
        </div>
      )}

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2">
        {rows.length === 0 && (
          <p className="col-span-full text-sm opacity-60">Lights out…</p>
        )}
        {rows.map((b) => (
          <div
            key={b.bay}
            className={`border p-2 text-xs transition-opacity ${
              b.state === "killed" || b.state === "dq" ? "opacity-30" : ""
            } ${b.bay === Number(winner?.match(/\d+/)?.[0]) ? "border-yellow-400" : ""}`}
          >
            <div className="font-bold">bay {String(b.bay).padStart(2, "0")}</div>
            <div className="truncate opacity-70">{b.strategy}</div>
            <div>{b.candidate_ms != null ? `${b.candidate_ms}ms` : b.state}</div>
          </div>
        ))}
      </div>

      <CopilotSidebar
        labels={{
          title: "Pit Wall",
          initial:
            'Try: "kill everything slower than 100ms" or "approve the winner".',
        }}
      />
    </main>
  );
}
