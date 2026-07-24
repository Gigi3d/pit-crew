// Keyless speech-to-text using the browser's built-in Web Speech API (Chrome).
// This is the honest fallback for idea 1's voice-IN: no ElevenLabs STT key needed,
// works offline in Chrome. If it is unsupported, the user types instead.
//
// Push to talk -> transcript -> onCommand(text). Feed that into the same handler
// the copilot action uses.
"use client";
import { useRef, useState } from "react";

export function VoiceButton({ onCommand }: { onCommand: (text: string) => void }) {
  const [listening, setListening] = useState(false);
  const recRef = useRef<any>(null);

  function start() {
    const SR =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SR) {
      alert("Voice input is not supported in this browser. Type the command instead.");
      return;
    }
    const rec = new SR();
    rec.lang = "en-US";
    rec.interimResults = false;
    rec.maxAlternatives = 1;
    rec.onresult = (e: any) => {
      const text = e.results[0][0].transcript;
      onCommand(text);
    };
    rec.onend = () => setListening(false);
    rec.onerror = () => setListening(false);
    rec.start();
    recRef.current = rec;
    setListening(true);
  }

  function stop() {
    recRef.current?.stop();
    setListening(false);
  }

  return (
    <button onClick={listening ? stop : start}>
      {listening ? "listening…" : "🎙 speak command"}
    </button>
  );
}
