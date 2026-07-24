// Client-side race, so the hosted console works with no Python backend.
// If NEXT_PUBLIC_ENGINE_URL is set, page.tsx uses the live engine instead and
// this is ignored. Same shape as pitcrew/serve.py's SSE events.

export type Bay = {
  bay: number;
  state: "queued" | "run" | "done" | "dq" | "killed";
  candidate_ms: number | null;
  strategy: string;
};

// Ten strategies, the first ten of the engine's pool.
const STRATEGIES = [
  "set + join + sort once",
  "single-pass accumulate",
  "index by key, one scan",
  "presize the buffer",
  "memoise by index",
  "early-exit on match",
  "vectorise the histogram",
  "prune the search tree",
  "hash-set dedupe",
  "fold in one pass",
];

export type SimPR = {
  title: string;
  strategy: string;
  baseline_ms: number;
  candidate_ms: number;
  number: number;
  pr_url: string;
};

// Bitmask-core-flavoured demo PRs. Links resolve to a repo you own via
// NEXT_PUBLIC_SIM_REPO. These are demo scenarios, not real reviews.
const SIM_REPO = process.env.NEXT_PUBLIC_SIM_REPO ?? "Gigi3d/widget-api";
const SCENARIOS: Omit<SimPR, "number" | "pr_url">[] = [
  { title: "Speed up branch-and-bound coin selection on large UTXO sets", strategy: "prune the search tree once effective value is met", baseline_ms: 1840, candidate_ms: 22 },
  { title: "Group and cache UTXOs by descriptor instead of rescanning", strategy: "index by descriptor, single pass", baseline_ms: 960, candidate_ms: 14 },
  { title: "Avoid re-parsing the PSBT on every input finalization", strategy: "parse once, mutate in place", baseline_ms: 1220, candidate_ms: 31 },
  { title: "Vectorise fee estimation over the mempool histogram", strategy: "bucket once, cumulative sum", baseline_ms: 540, candidate_ms: 9 },
  { title: "Cache derived addresses in the descriptor wallet gap scan", strategy: "memoise derivation by index", baseline_ms: 2100, candidate_ms: 40 },
  { title: "Compute confirmed balance in one UTXO pass", strategy: "accumulate in a single fold", baseline_ms: 780, candidate_ms: 11 },
  { title: "Short-circuit SPV Merkle proof verification on match", strategy: "early-exit on root match", baseline_ms: 610, candidate_ms: 7 },
  { title: "Batch BIP32 child key derivation for account discovery", strategy: "derive siblings together", baseline_ms: 1550, candidate_ms: 28 },
];

export function pickPR(): SimPR {
  const s = SCENARIOS[Math.floor(Math.random() * SCENARIOS.length)];
  const number = 128 + Math.floor(Math.random() * 60);
  return { ...s, number, pr_url: `https://github.com/${SIM_REPO}/pull/${number}` };
}

type Ev =
  | { type: "lights_out"; bays: number }
  | { type: "bay"; bay: number; state: Bay["state"]; candidate_ms: number | null; strategy: string }
  | { type: "winner"; bay: number; strategy: string; baseline_ms: number; candidate_ms: number };

// Drive a race by calling `emit` over ~4s, mirroring the real engine's cadence.
// Aligns to the PR so the winning lap, the stats, and the winner card all show
// the same before/after numbers.
export function runSimRace(emit: (e: Ev) => void, pr: SimPR, nBays = 10): () => void {
  const timers: ReturnType<typeof setTimeout>[] = [];
  const at = (ms: number, fn: () => void) => timers.push(setTimeout(fn, ms));

  emit({ type: "lights_out", bays: nBays });
  for (let b = 1; b <= nBays; b++) {
    emit({ type: "bay", bay: b, state: "queued", candidate_ms: null, strategy: STRATEGIES[b - 1] });
  }

  // One bay is the deliberate loser (disqualified). One bay wins with exactly
  // the PR's candidate time; the rest land slower, spread between there and the
  // baseline, so the winner is unambiguously fastest.
  const dq = 1 + Math.floor(Math.random() * nBays);
  let winnerBay = 1 + Math.floor(Math.random() * nBays);
  if (winnerBay === dq) winnerBay = (winnerBay % nBays) + 1;

  const ceiling = Math.max(pr.candidate_ms + 30, Math.round(pr.baseline_ms * 0.35));
  const laps: Record<number, number> = {};
  for (let b = 1; b <= nBays; b++) {
    if (b === dq) laps[b] = 0;
    else if (b === winnerBay) laps[b] = pr.candidate_ms;
    else laps[b] = pr.candidate_ms + 15 + Math.floor(Math.random() * ceiling);
  }

  for (let b = 1; b <= nBays; b++) {
    at(300 + b * 250, () =>
      emit({
        type: "bay",
        bay: b,
        state: b === dq ? "dq" : "done",
        candidate_ms: b === dq ? null : laps[b],
        strategy: STRATEGIES[b - 1],
      }),
    );
  }
  at(300 + nBays * 250 + 400, () =>
    emit({
      type: "winner",
      bay: winnerBay,
      strategy: STRATEGIES[winnerBay - 1],
      baseline_ms: pr.baseline_ms,
      candidate_ms: pr.candidate_ms,
    }),
  );

  return () => timers.forEach(clearTimeout);
}
