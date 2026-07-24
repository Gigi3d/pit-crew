// Client helper: POST text to /api/tts and play the audio. Fails silently, so a
// missing ElevenLabs key degrades to a silent-but-working demo, never a crash.
export async function speak(text: string): Promise<void> {
  try {
    const res = await fetch("/api/tts", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    if (!res.ok) return;
    const buf = await res.arrayBuffer();
    const url = URL.createObjectURL(new Blob([buf], { type: "audio/mpeg" }));
    const audio = new Audio(url);
    audio.onended = () => URL.revokeObjectURL(url);
    await audio.play();
  } catch {
    /* no voice is fine; the transcript still shows on screen */
  }
}
