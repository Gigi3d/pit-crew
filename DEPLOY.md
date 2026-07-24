# Deploy the frontend to production

The console is a Next.js app in `pitcrew-ui/`. It runs the race client-side and
does the real work (Fireworks copilot, Discord post, TTS) in API routes, so a
single Vercel deploy is the whole production stack. No Python backend to host.

## One-time setup on Vercel

1. Go to https://vercel.com and sign in with GitHub.
2. **Add New > Project**, import `the-builders-burrow/pit-crew` (or `Gigi3d/pit-crew`).
3. **Set the Root Directory to `pitcrew-ui`.** This is the one thing that trips
   people up: the repo is a monorepo, and Vercel must build from the app folder,
   not the repo root. Everything else auto-detects (Next.js, build command).
4. Add the environment variables below, then **Deploy**.

## Environment variables (paste into Vercel > Settings > Environment Variables)

Server-side (never exposed to the browser):

| Var | Value |
|---|---|
| `FIREWORKS_API_KEY` | your Fireworks key (powers the copilot) |
| `DISCORD_WEBHOOK_URL` | the team channel webhook |
| `ELEVENLABS_API_KEY` | optional, for voice replies |
| `ELEVENLABS_VOICE_ID` | optional |

Public (safe, shown in the browser):

| Var | Value |
|---|---|
| `NEXT_PUBLIC_PR_URL` | the PR the demo links to, e.g. `https://github.com/Gigi3d/widget-api/pull/1` |
| `NEXT_PUBLIC_SIM_REPO` | repo the sim PR links resolve to, e.g. `Gigi3d/widget-api` |

Local values live in `pitcrew-ui/.env.local` (gitignored). The same keys go in
Vercel; the file is not uploaded.

## Deploy from the CLI instead

```bash
cd pitcrew-ui
npx vercel            # first run links the project; set root dir when asked
npx vercel --prod     # promote to production
```

Set the env vars with `npx vercel env add <NAME>` or in the dashboard.

## After deploy

Your app is at `https://<project>.vercel.app`. The race runs on load; "approve
the winner" (typed or spoken in the Pit Wall) posts the PR to Discord, where
CodeRabbit reviews it. The whole loop, on a public URL.
