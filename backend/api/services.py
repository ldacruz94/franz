import io
import os
import tempfile

import numpy as np
import soundfile as sf
from faster_whisper import WhisperModel
from kokoro import KPipeline

from agent import chat as agent_chat, pop_theme

whisper = WhisperModel("base", device="cpu", compute_type="int8")
tts = KPipeline(lang_code="b")


def transcribe_audio(data: bytes, filename: str) -> str:
    suffix = os.path.splitext(filename)[1] or ".webm"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(data)
        tmp_path = tmp.name
    try:
        segments, _ = whisper.transcribe(tmp_path, task="transcribe", language="en")
        return " ".join(seg.text.strip() for seg in segments)
    finally:
        os.unlink(tmp_path)


def chat(message: str) -> dict:
    reply = agent_chat(message)
    theme = pop_theme()
    result: dict = {"reply": reply}
    if theme:
        result["theme"] = theme
    return result


def synthesize_speech(text: str) -> bytes:
    chunks = [audio for _, _, audio in tts(text, voice="bm_george")]
    audio = np.concatenate(chunks)
    buf = io.BytesIO()
    sf.write(buf, audio, 24000, format="WAV")
    return buf.getvalue()
