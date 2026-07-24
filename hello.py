"""Prove the whole stack in one run. Referenced by SETUP.md section 9.

  python hello.py

Any service whose key is missing is SKIPPED, so this runs today and tells you
exactly what is still unwired. On Friday, with .env filled, you want four OKs.
Run it again on the venue wifi at 09:45.
"""
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

G, R, Y, X = "\033[32m", "\033[31m", "\033[33m", "\033[0m"


def line(name, status, detail=""):
    col = {"ok": G, "skip": Y, "fail": R}[status]
    print(f"{name:11} {col}{status:4}{X} {detail}")


def daytona():
    if not os.environ.get("DAYTONA_API_KEY"):
        return line("daytona", "skip", "no DAYTONA_API_KEY")
    try:
        from daytona import Daytona
        sb = Daytona().create()
        out = sb.process.code_run('print("hi")').result
        sb.delete()
        line("daytona", "ok", f"sandbox created and destroyed ({out.strip()})")
    except Exception as e:
        line("daytona", "fail", f"{type(e).__name__}: {e}")


def fireworks():
    if not os.environ.get("FIREWORKS_API_KEY"):
        return line("fireworks", "skip", "no FIREWORKS_API_KEY")
    try:
        from fireworks import Fireworks
        r = Fireworks().chat.completions.create(
            model="accounts/fireworks/models/deepseek-v3p1",
            messages=[{"role": "user", "content": "reply with the single word ok"}],
        )
        line("fireworks", "ok", f"{r.usage.total_tokens} tokens")
    except Exception as e:
        line("fireworks", "fail", f"{type(e).__name__}: {e}")


def braintrust():
    if not os.environ.get("BRAINTRUST_API_KEY"):
        return line("braintrust", "skip", "no BRAINTRUST_API_KEY")
    try:
        from braintrust import Braintrust
        bt = Braintrust(project_name="pitcrew")
        with bt.trace(name="hello") as span:
            span.log(score=1.0)
        line("braintrust", "ok", "trace logged to project pitcrew")
    except Exception as e:
        line("braintrust", "fail", f"{type(e).__name__}: {e}")


def elevenlabs():
    if not os.environ.get("ELEVENLABS_API_KEY"):
        return line("elevenlabs", "skip", "no ELEVENLABS_API_KEY")
    try:
        from elevenlabs.client import ElevenLabs
        c = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])
        voice = os.environ.get("ELEVENLABS_VOICE_ID", "")
        if not voice:
            return line("elevenlabs", "skip", "no ELEVENLABS_VOICE_ID")
        audio = c.text_to_speech.convert(voice_id=voice, text="Box, box.")
        n = sum(len(chunk) for chunk in audio)
        line("elevenlabs", "ok", f"{n} bytes of audio")
    except Exception as e:
        line("elevenlabs", "fail", f"{type(e).__name__}: {e}")


if __name__ == "__main__":
    print("Pit Crew stack check\n")
    daytona(); fireworks(); braintrust(); elevenlabs()
    print("\nfour OKs means the morning is yours.")
