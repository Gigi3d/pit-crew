"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { CopilotSidebar } from "@copilotkit/react-ui";
import { useRaceActions, type Bay } from "@/components/useRaceActions";
import { runSimRace, pickPR, type SimPR } from "@/lib/race";
import "./console.css";

// Live engine when configured, else the client-side race.
const ENGINE = process.env.NEXT_PUBLIC_ENGINE_URL;

type Radio = { who: "you" | "crew"; text: string };

export default function Console() {
  const [bays, setBays] = useState<Record<number, Bay>>({});
  const [phase, setPhase] = useState("LIGHTS OUT");
  const [live, setLive] = useState(true);
  const [pr, setPr] = useState<SimPR | null>(null);
  const [winnerBay, setWinnerBay] = useState<number | null>(null);
  const [radio, setRadio] = useState<Radio[]>([]);
  const [posted, setPosted] = useState<string | null>(null);
  const [cmd, setCmd] = useState("");
  const [runId, setRunId] = useState(0);
  const radioRef = useRef<HTMLDivElement>(null);

  const say = useCallback((who: "you" | "crew", text: string) => {
    setRadio((r) => [...r, { who, text }]);
  }, []);

  const apply = useCallback(
    (ev: any) => {
      if (ev.type === "lights_out") {
        setPhase("RACING");
        setLive(true);
        say("crew", "Lights out. Ten bays away.");
      } else if (ev.type === "bay") {
        setBays((prev) => ({ ...prev, [ev.bay]: { ...prev[ev.bay], ...ev } }));
      } else if (ev.type === "winner") {
        setWinnerBay(ev.bay);
        setPhase("RACE COMPLETE");
        setLive(false);
        say(
          "crew",
          `Chequered flag. Bay ${ev.bay}, ${ev.candidate_ms}ms, ${(
            ev.baseline_ms / ev.candidate_ms
          ).toFixed(0)}x. Tests green.`,
        );
      }
    },
    [say],
  );

  // Start a race whenever runId changes (mount + RUN RACE button).
  useEffect(() => {
    setBays({});
    setWinnerBay(null);
    setPosted(null);
    setRadio([]);
    const nextPr = pickPR();
    setPr(nextPr);

    if (ENGINE) {
      const source = new EventSource(`${ENGINE}/events`);
      source.onmessage = (e) => {
        try {
          apply(JSON.parse(e.data));
        } catch {
          /* a malformed frame must never kill the console mid-demo */
        }
      };
      source.onerror = () => {
        setLive(false);
        setPhase("DISCONNECTED");
      };
      return () => source.close();
    }
    const stop = runSimRace(apply, nextPr);
    return stop;
  }, [runId, apply]);

  useEffect(() => {
    radioRef.current?.scrollTo(0, radioRef.current.scrollHeight);
  }, [radio]);

  // Deterministic cull. The copilot's number lands here; so does the text box.
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

  // "Approve the winner" -> post the PR to Discord.
  const approve = useCallback(async () => {
    const res = await fetch("/api/approve", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(pr),
    });
    const data = await res.json().catch(() => ({}));
    const url = data.pr ?? pr?.pr_url ?? null;
    setPosted(url);
    say("crew", url ? "Winner approved. PR posted to Discord for review." : "Could not post the PR.");
    return data;
  }, [pr, say]);

  // Text command, same shape as the voice action, no model needed.
  const runCommand = useCallback(
    (text: string) => {
      say("you", `"${text}"`);
      const m = text.match(/(\d+(\.\d+)?)\s*ms?/);
      if (/kill|retire|slower|drop/i.test(text) && m) {
        const thr = parseFloat(m[1]);
        const killed = killBays(
          (b) => b.state === "done" && (b.candidate_ms ?? Infinity) > thr,
        );
        const alive = Object.values(bays).filter((b) => b.state === "done").length;
        say("crew", `Copy. ${killed} bays retired. ${Math.max(alive - killed, 0)} still running.`);
      } else if (/approve|open|winner|ship/i.test(text)) {
        approve();
      } else {
        say("crew", "Say: kill everything slower than N ms, or approve the winner.");
      }
    },
    [bays, killBays, say, approve],
  );

  useRaceActions(bays, killBays, approve, (msg) => {
    fetch("/api/tts", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: msg }),
    })
      .then((r) => (r.ok ? r.blob() : null))
      .then((b) => b && new Audio(URL.createObjectURL(b)).play().catch(() => {}))
      .catch(() => {});
  });

  const rows = useMemo(() => Object.values(bays).sort((a, b) => a.bay - b.bay), [bays]);
  const done = useMemo(
    () =>
      Object.values(bays)
        .filter((b) => b.state === "done" || (b.bay === winnerBay && b.state !== "dq"))
        .sort((a, b) => (a.candidate_ms ?? 9e9) - (b.candidate_ms ?? 9e9)),
    [bays, winnerBay],
  );
  const dq = useMemo(() => Object.values(bays).filter((b) => b.state === "dq").length, [bays]);
  const best = done[0]?.candidate_ms ?? null;
  const baseline = pr?.baseline_ms ?? 619;

  return (
    <div className="pc">
      <header>
        <div className="logo">
          Pit<em>&nbsp;</em>Crew
        </div>
        <div className="repo">
          <b>Gigi3d/widget-api</b> &nbsp;·&nbsp; PR #{pr?.number ?? 1} &nbsp;·&nbsp;{" "}
          <span className="fn">{pr?.title ?? "coin selection"}</span>
        </div>
        <div className="status">
          <span className={`dot ${live ? "live" : ""}`} />
          <span>{phase}</span>
        </div>
        <button onClick={() => setRunId((n) => n + 1)}>RUN RACE</button>
      </header>

      <div className="stats">
        <div className="stat">
          <div className="k">BASELINE</div>
          <div className="v">{baseline}ms</div>
        </div>
        <div className="stat">
          <div className="k">FASTEST LAP</div>
          <div className="v g">{best != null ? `${best}ms` : "·"}</div>
        </div>
        <div className="stat">
          <div className="k">SPEEDUP</div>
          <div className="v a">{best ? `${(baseline / best).toFixed(0)}x` : "·"}</div>
        </div>
        <div className="stat">
          <div className="k">BAYS LEGAL / DQ</div>
          <div className="v r">
            {done.length} / {dq}
          </div>
        </div>
      </div>

      <div className="wrap">
        <div className="panel">
          <h2>Ten bays</h2>
          <div className="grid">
            {rows.length === 0 &&
              Array.from({ length: 10 }, (_, i) => (
                <div className="bay" key={i}>
                  <div className="id">BAY {String(i + 1).padStart(2, "0")}</div>
                  <div className="ms">&nbsp;</div>
                  <div className="st">QUEUED</div>
                </div>
              ))}
            {rows.map((b) => {
              const cls =
                b.state === "killed"
                  ? "killed"
                  : b.bay === winnerBay && b.state === "done"
                    ? "done p1"
                    : b.state;
              return (
                <div className={`bay ${cls}`} key={b.bay}>
                  <div className="id">BAY {String(b.bay).padStart(2, "0")}</div>
                  <div className="ms">{b.candidate_ms != null ? `${b.candidate_ms}ms` : " "}</div>
                  <div className="st">
                    {b.state === "queued"
                      ? "QUEUED"
                      : b.state === "run"
                        ? "RUNNING"
                        : b.state === "dq"
                          ? "DQ TESTS"
                          : (b.strategy || "").toUpperCase().slice(0, 16)}
                  </div>
                  {b.state === "run" && <div className="bar" />}
                </div>
              );
            })}
          </div>

          {winnerBay != null && pr && (
            <div className="winner">
              <div className="head">
                <span className="big">{bays[winnerBay]?.candidate_ms ?? pr.candidate_ms}ms</span>
                <span className="was">{pr.baseline_ms}ms</span>
                <span className="tagx">
                  STRATEGY: {(bays[winnerBay]?.strategy ?? pr.strategy).toUpperCase()}
                </span>
                <span className="tagx">BAY {String(winnerBay).padStart(2, "0")}</span>
              </div>
              <div className="verify">
                ✓ tests green &nbsp;·&nbsp;{" "}
                <b>re-verified from a clean checkout in a sandbox that never met the agent</b>
              </div>
              <div className="acts">
                {posted ? (
                  <a href={posted} target="_blank" rel="noreferrer">
                    posted to Discord, open the PR ↗
                  </a>
                ) : (
                  <>
                    <button onClick={approve}>APPROVE &amp; POST PR</button>
                    <button className="no" onClick={() => setRunId((n) => n + 1)}>
                      DISCARD
                    </button>
                  </>
                )}
              </div>
            </div>
          )}
        </div>

        <div>
          <div className="panel">
            <h2>Leaderboard</h2>
            <div className="lb">
              {done.length === 0 && (
                <div className="row">
                  <span className="p">·</span>
                  <span className="b">waiting for lights out</span>
                </div>
              )}
              {done.slice(0, 6).map((b, i) => (
                <div className={`row ${i === 0 ? "top" : ""}`} key={b.bay}>
                  <span className="p">P{i + 1}</span>
                  <span className="b">
                    bay {String(b.bay).padStart(2, "0")} · {b.strategy}
                  </span>
                  <span className="t">{b.candidate_ms}ms</span>
                </div>
              ))}
            </div>
          </div>

          <div className="panel" style={{ marginTop: 20 }}>
            <h2>Team radio</h2>
            <div className="radio" ref={radioRef}>
              {radio.map((m, i) => (
                <div className={`msg ${m.who}`} key={i}>
                  <b>{m.who === "you" ? "YOU, OVER RADIO" : "CREW"}</b>
                  {m.text}
                </div>
              ))}
            </div>
            <div className="cmd">
              <input
                value={cmd}
                onChange={(e) => setCmd(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && cmd.trim()) {
                    runCommand(cmd.trim());
                    setCmd("");
                  }
                }}
                placeholder="kill everything slower than 200ms"
              />
              <button
                onClick={() => {
                  if (cmd.trim()) {
                    runCommand(cmd.trim());
                    setCmd("");
                  }
                }}
              >
                SEND
              </button>
            </div>
          </div>
        </div>
      </div>

      <CopilotSidebar
        labels={{
          title: "Pit Wall",
          initial: 'Try: "kill everything slower than 200ms" or "approve the winner".',
        }}
      />
    </div>
  );
}
