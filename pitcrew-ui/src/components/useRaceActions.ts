// The core of idea 1. Registers the copilot actions that let a spoken (or typed)
// command change the race. Drop into pitcrew-ui and call from the component that
// holds the bays state.
//
//   useRaceActions(bays, killBays, speak)
//
// The model turns "kill everything slower than 300ms" into cullSlowBays({thresholdMs:300}).
// The handler is deterministic; the model only extracts the number. That split is
// why the typed box in ui/live.html is a perfect fallback: same handler, no model.
//
// Signature note: useCopilotAction / useCopilotReadable are stable, but confirm the
// exact `parameters` shape against your installed @copilotkit/react-core version.
import { useCopilotAction, useCopilotReadable } from "@copilotkit/react-core";

export type Bay = {
  bay: number;
  state: "queued" | "run" | "done" | "dq" | "killed";
  candidate_ms: number | null;
  strategy: string;
};

export function useRaceActions(
  bays: Record<number, Bay>,
  killBays: (predicate: (b: Bay) => boolean) => number,
  speak?: (text: string) => void,
) {
  // let the copilot see the live race so it can answer questions about it
  useCopilotReadable({
    description: "The live race: every bay with its lap time in ms and state.",
    value: Object.values(bays),
  });

  // "kill everything slower than N ms"
  useCopilotAction({
    name: "cullSlowBays",
    description:
      "Retire every running bay whose lap time is slower than a threshold in milliseconds.",
    parameters: [
      {
        name: "thresholdMs",
        type: "number",
        description: "kill bays slower than this many milliseconds",
        required: true,
      },
    ],
    handler: async ({ thresholdMs }: { thresholdMs: number }) => {
      const killed = killBays(
        (b) => b.state === "done" && (b.candidate_ms ?? Infinity) > thresholdMs,
      );
      const alive = Object.values(bays).filter((b) => b.state === "done").length;
      const msg = `Copy. ${killed} bays retired. ${Math.max(alive, 0)} still running.`;
      speak?.(msg);
      return msg;
    },
  });

  // "approve the winner" -> opens PR #2 (see widget-api/DEMO.md)
  useCopilotAction({
    name: "openWinnerPR",
    description: "Approve the current winning patch and open pull request #2.",
    parameters: [],
    handler: async () => {
      const res = await fetch("/api/approve", { method: "POST" });
      const msg = res.ok
        ? "Winner approved. Pull request opening now."
        : "Could not open the pull request.";
      speak?.(msg);
      return msg;
    },
  });
}
