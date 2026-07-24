# CopilotKit + voice wiring (idea 1)

Paste-ready pieces for the `pitcrew-ui` Next.js app. They turn a spoken or typed
command into a real change on the race, and speak the crew's reply back.

**Nothing here is verified against your installed versions**, because there is no
Next.js toolchain on the build machine. Confirm the two signatures flagged below
on the day. The typed-command box already working in `ui/live.html` is the proof
that the underlying logic is sound and the always-available fallback.

## Where each file goes

| This file | Copy to |
|---|---|
| `api-copilotkit-route.ts` | `pitcrew-ui/app/api/copilotkit/route.ts` |
| `api-tts-route.ts` | `pitcrew-ui/app/api/tts/route.ts` |
| `useRaceActions.ts` | `pitcrew-ui/components/useRaceActions.ts` |
| `VoiceButton.tsx` | `pitcrew-ui/components/VoiceButton.tsx` |
| `speak.ts` | `pitcrew-ui/lib/speak.ts` |

## Install

```bash
cd pitcrew-ui
npm install @copilotkit/react-core @copilotkit/react-ui @copilotkit/runtime openai @elevenlabs/elevenlabs-js
```

## Wire it up

1. Wrap the app in the provider (`app/layout.tsx`):

```tsx
import { CopilotKit } from "@copilotkit/react-core";
// ...
<CopilotKit runtimeUrl="/api/copilotkit">{children}</CopilotKit>
```

2. In the component that holds the race state, register the actions:

```tsx
import { useRaceActions } from "@/components/useRaceActions";
import { VoiceButton } from "@/components/VoiceButton";
import { speak } from "@/lib/speak";

// bays: Record<number, Bay>, setBays your state setter
const killBays = (pred) => {
  let n = 0;
  setBays((prev) => {
    const next = { ...prev };
    for (const b of Object.values(next)) if (pred(b)) { b.state = "killed"; n++; }
    return next;
  });
  return n;
};

useRaceActions(bays, killBays, speak);

// the same command handler, driven by voice OR the copilot OR a text box:
<VoiceButton onCommand={(text) => /* feed text to CopilotKit chat input */} />
```

## The command flow

```
you speak  ──►  VoiceButton (Web Speech API, keyless)   ──┐
you type   ──►  CopilotKit chat input                     ├─►  model extracts {thresholdMs}
                                                          │        │
                                                          │        ▼
                                              cullSlowBays handler culls the grid
                                                          │        │
                                                          ▼        ▼
                                              speak() ──► /api/tts (ElevenLabs) ──► audio
```

The model's only job is turning a sentence into `{thresholdMs: 300}`. The handler
is deterministic. That is why the demo is robust: three independent input paths
(voice, chat, text box) all hit the same handler.

## Two signatures to confirm on the day (both flagged in SETUP.md section 8)

1. **`useCopilotAction` parameters shape** in your installed `@copilotkit/react-core`.
2. **`textToSpeech.convert()`** in your installed `@elevenlabs/elevenlabs-js`.

## The fallback chain, best to worst, all still a working demo

1. Voice in (Web Speech), copilot culls, voice out. The full idea.
2. Mic fails: type into the CopilotKit chat, model culls, voice out.
3. CopilotKit flaky: the plain text box in `ui/live.html` culls directly, no model.
4. Everything network-dependent fails: the pre-recorded screen capture (SETUP.md section 10).

You are never one failure away from a dead stage.

## Signature verification (resolved 2026-07-24)

SETUP.md section 8 item 2 flagged `useCopilotAction`'s shape as unconfirmed
because their reference page 404'd. Resolved against the installed
`@copilotkit/react-core@1.63.1` type definitions:

```ts
useCopilotAction<const T extends Parameter[] | [] = []>(
  action: FrontendAction<T> | CatchAllFrontendAction,
  dependencies?: any[],
): void
```

**The shape in `useRaceActions.ts` is correct** - `{name, description,
parameters, handler}` with `parameters` as an array of `{name, type,
description, required}`. No changes needed.

One thing worth knowing: the package now describes `useCopilotAction` as
"a legacy hook maintained for backwards compatibility". It is not removed and
it works - it registers the action with CopilotContext rather than calling
hooks conditionally, so action types can change between renders. There is also
a `@copilotkit/react-core/v2` entry point.

For a one-day build, stay on `useCopilotAction`: it is the documented path,
it works in 1.63.1, and swapping to v2 on the day buys nothing a judge can see.
