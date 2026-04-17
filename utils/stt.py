import os
from dotenv import load_dotenv

load_dotenv()

USE_LOCAL_STT = os.getenv("USE_LOCAL_STT", "false").lower() == "true"
USE_GROQ_API  = os.getenv("USE_GROQ_API", "false").lower() == "true"

def _transcribe_groq(audio_path: str) -> str:
    """Fast cloud STT via Groq Whisper (near-instant, great accuracy)."""
    from openai import OpenAI
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY missing in .env")
    client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
    print("STT -> Groq whisper-large-v3-turbo ...")
    with open(audio_path, "rb") as f:
        result = client.audio.transcriptions.create(model="whisper-large-v3-turbo", file=f)
    return result.text.strip()

def _transcribe_local(audio_path: str) -> str:
    """Local STT via faster-whisper (requires C++ build tools + GPU recommended)."""
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        raise ImportError("faster-whisper not installed. Set USE_LOCAL_STT=false in .env to use Groq instead.")
    print("STT -> Local faster-whisper (base, CPU) - this may take a few minutes ...")
    model = WhisperModel("base", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(audio_path, beam_size=3)
    return " ".join(s.text for s in segments).strip()

def transcribe_audio(audio_path: str) -> str:
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio not found: {audio_path}")
    if USE_LOCAL_STT:
        return _transcribe_local(audio_path)
    # Default: Groq API (fastest path)
    return _transcribe_groq(audio_path)
