"""Voice in and out, with the signatures verified against elevenlabs 2.59.0.

This resolves SETUP.md section 8 item 1: the speech-to-text call signature that
their docs did not cover. Both directions are confirmed against the installed
SDK rather than copied from a quickstart.

    ./.venv/bin/python voice.py say "Copy. Twenty two bays retired."
    ./.venv/bin/python voice.py listen recording.mp3
    ./.venv/bin/python voice.py voices        # list what your account can use

SETUP.md section 5 is emphatic: pick the crew voice tonight and hard-code the
id. Put it in .env as ELEVENLABS_VOICE_ID.
"""

import os
import sys

from dotenv import load_dotenv

load_dotenv()

# The Node quickstart's JBFqnCBsd6RMkjVDRZzb, kept as the default so `say` works
# before you have chosen. Override in .env.
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "JBFqnCBsd6RMkjVDRZzb")

# Python SDK uses snake_case; the Node SDK's modelId/outputFormat become these.
TTS_MODEL = os.getenv("ELEVENLABS_TTS_MODEL", "eleven_multilingual_v2")
OUTPUT_FORMAT = "mp3_44100_128"

# model_id is REQUIRED for speech_to_text.convert - it has no default, unlike
# every other argument. scribe_v1 is ElevenLabs' transcription model.
STT_MODEL = os.getenv("ELEVENLABS_STT_MODEL", "scribe_v1")


def client():
    key = os.getenv("ELEVENLABS_API_KEY")
    if not key or key.startswith("#"):
        sys.exit("ELEVENLABS_API_KEY is not set in .env - get one at elevenlabs.io")
    from elevenlabs.client import ElevenLabs

    return ElevenLabs(api_key=key)


def say(text):
    """Speak a line. Returns the mp3 bytes so callers can cache them."""
    from elevenlabs import play

    # NOTE: convert() returns an ITERATOR of byte chunks, not bytes. Joining is
    # what lets you both play it and save it; play() would consume the iterator.
    chunks = client().text_to_speech.convert(
        VOICE_ID,
        text=text,
        model_id=TTS_MODEL,
        output_format=OUTPUT_FORMAT,
    )
    audio = b"".join(chunks)
    print(f"{len(audio):,} bytes from voice {VOICE_ID}")
    play(audio)
    return audio


def listen(path):
    """Transcribe an audio file. This is the half that matters for idea 1."""
    with open(path, "rb") as f:
        result = client().speech_to_text.convert(file=f, model_id=STT_MODEL)
    text = getattr(result, "text", str(result))
    print(f"heard: {text!r}")
    return text


def voices():
    """List voices, so you can choose the crew voice without browsing on stage."""
    all_voices = client().voices.get_all()
    for v in all_voices.voices:
        labels = getattr(v, "labels", {}) or {}
        desc = ", ".join(f"{k}={v}" for k, v in list(labels.items())[:3])
        print(f"  {v.voice_id}  {v.name:<22} {desc}")
    print(f"\n{len(all_voices.voices)} voices. Put your pick in .env:")
    print("  ELEVENLABS_VOICE_ID=<id>")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cmd = sys.argv[1]
    if cmd == "say":
        say(" ".join(sys.argv[2:]) or "Copy. Twenty two bays retired.")
    elif cmd == "listen":
        if len(sys.argv) < 3:
            sys.exit("usage: voice.py listen <audio-file>")
        listen(sys.argv[2])
    elif cmd == "voices":
        voices()
    else:
        sys.exit(__doc__)
