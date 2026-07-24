// Voice OUT. Turns the crew's reply text into speech with ElevenLabs, server-side
// so the key never reaches the browser. The client speak() helper POSTs here and
// plays the returned audio.
//
// Signature confirmed against @elevenlabs/elevenlabs-js: convert(voiceId, {
// text, modelId, outputFormat }). Model default is eleven_multilingual_v2 - the
// one from ElevenLabs' own quickstart. eleven_v3 (the original) is not a
// confirmed id; override via ELEVENLABS_TTS_MODEL if you pick another.
import { NextRequest } from "next/server";
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

// Live API + secret env; must run per-request, never at build time.
export const dynamic = "force-dynamic";

const TTS_MODEL = process.env.ELEVENLABS_TTS_MODEL ?? "eleven_multilingual_v2";

export const POST = async (req: NextRequest) => {
  const apiKey = process.env.ELEVENLABS_API_KEY;
  const voiceId = process.env.ELEVENLABS_VOICE_ID;

  // Fail soft: voice is the layer on top, not the load-bearing half. A missing
  // key or voice returns 503 so the UI's typed fallback keeps working rather
  // than the whole request throwing.
  if (!apiKey || !voiceId) {
    return new Response(
      JSON.stringify({ error: "TTS not configured (key or voice id missing)" }),
      { status: 503, headers: { "Content-Type": "application/json" } },
    );
  }

  const { text } = await req.json();
  // Client built here, not at module scope, so `next build` does not try to
  // construct it with no key during page-data collection.
  const client = new ElevenLabsClient({ apiKey });

  // convert() returns a web ReadableStream<Uint8Array> in this SDK version.
  // Stream it straight through rather than buffering - the browser can start
  // playing sooner, and there is nothing to collect or concat.
  const audio = await client.textToSpeech.convert(voiceId, {
    text,
    modelId: TTS_MODEL,
    outputFormat: "mp3_44100_128",
  });

  return new Response(audio as ReadableStream<Uint8Array>, {
    headers: { "Content-Type": "audio/mpeg", "Cache-Control": "no-store" },
  });
};
