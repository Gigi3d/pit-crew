// Destination: pitcrew-ui/app/api/tts/route.ts
//
// Voice OUT. Turns the crew's reply text into speech with ElevenLabs, server-side
// so the key never reaches the browser. The client speak() helper POSTs here and
// plays the returned audio.
//
// Needs: npm install @elevenlabs/elevenlabs-js
// Confirm the convert() signature against your installed SDK version. As of the
// docs checked, it is convert(voiceId, { text, modelId }). Set ELEVENLABS_VOICE_ID.
import { NextRequest } from "next/server";
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

const client = new ElevenLabsClient({ apiKey: process.env.ELEVENLABS_API_KEY! });

export const POST = async (req: NextRequest) => {
  const { text } = await req.json();
  const voiceId = process.env.ELEVENLABS_VOICE_ID!;

  const audio = await client.textToSpeech.convert(voiceId, {
    text,
    modelId: "eleven_v3",
  });

  // the SDK returns an async iterable of chunks; collect to one buffer
  const chunks: Uint8Array[] = [];
  for await (const chunk of audio as any) chunks.push(chunk);
  const body = Buffer.concat(chunks);

  return new Response(body, {
    headers: { "Content-Type": "audio/mpeg", "Cache-Control": "no-store" },
  });
};
