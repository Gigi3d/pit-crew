"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { CopilotSidebar } from "@copilotkit/react-ui";
import { useRaceActions, type Bay } from "@/components/useRaceActions";

// The Python engine serves SSE on 8420 (pitcrew/serve.py). Override for a
// deployed backend.
const ENGINE = process.env.NEXT_PUBLIC_ENGINE_URL ?? "http://localhost:8420";

export default function Console() {
  const [bays, setBays] = useState<Record<number, Bay>>({});
  const [connected, setConnected] = useState(false);
  const [winner, setWinner] = useState<string | null>(null);

  useEffect(() => {
    const source = new EventSource(`${ENGINE}/events`);
    source.onopen = () => setConnected(true);
    source.onerror = () => setConnected(false);
    source.onmessage = (e) => {
      try {
        const ev = JSON.parse(e.data);
        if (ev.type === "bay") {
          setBays((prev) => ({ ...prev, [ev.bay]: { ...prev[ev.bay], ...ev } }));
        } else if (ev.type === "winner") {
          setWinner(`bay ${ev.bay} — ${ev.strategy}`);
        }
      } catch {
        /* a malformed frame must never kill the console mid-demo */
      }
    };
    return () => source.close();
  }, []);

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

  useRaceActions(bays, killBays);

  const rows = useMemo(
    () => Object.values(bays).sort((a, b) => a.bay - b.bay),
    [bays],
  );

  return (
    <main className="flex-1 p-6 font-mono">
      <header className="flex items-baseline gap-4 mb-6">
        <h1 className="text-2xl font-bold">PIT CREW</h1>
        <span className="text-xs opacity-60">SAMPLE FN</span>
        <span className="ml-auto text-xs">
          {connected ? "engine connected" : "engine offline"}
        </span>
      </header>

      {winner && <div className="mb-4 border px-3 py-2 text-sm">P1 {winner}</div>}

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
        {rows.length === 0 && (
          <p className="col-span-full text-sm opacity-60">
            No bays yet. Start the engine: <code>python3 -m pitcrew.serve</code>
          </p>
        )}
        {rows.map((b) => (
          <div
            key={b.bay}
            className={`border p-2 text-xs ${
              b.state === "killed" || b.state === "dq" ? "opacity-30" : ""
            }`}
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
            'Try: "kill everything slower than 300ms" or "approve the winner".',
        }}
      />
    </main>
  );
}
