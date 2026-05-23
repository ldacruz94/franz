from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from faster_whisper import WhisperModel
from kokoro import KPipeline
from pydantic import BaseModel
from agent import chat as agent_chat, pop_theme
import numpy as np
import soundfile as sf
import tempfile
import io
import os

app = FastAPI(title="Franz")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

whisper = WhisperModel("base", device="cpu", compute_type="int8")
tts = KPipeline(lang_code="b")  # British English


class SpeakRequest(BaseModel):
    text: str


class ChatRequest(BaseModel):
    message: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    data = await audio.read()
    suffix = os.path.splitext(audio.filename or "audio.webm")[1] or ".webm"

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(data)
        tmp_path = tmp.name

    try:
        segments, _ = whisper.transcribe(tmp_path)
        transcript = " ".join(seg.text.strip() for seg in segments)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.unlink(tmp_path)

    return {"transcript": transcript}


@app.post("/chat")
def chat(req: ChatRequest):
    try:
        reply = agent_chat(req.message)
        theme = pop_theme()
    except Exception as e:
        print(f"[chat error] {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    result: dict = {"reply": reply}

    if theme:
        result["theme"] = theme

    return result


@app.post("/speak")
def speak(req: SpeakRequest):
    try:
        chunks = [audio for _, _, audio in tts(req.text, voice="bm_george")]
        audio = np.concatenate(chunks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    buf = io.BytesIO()
    sf.write(buf, audio, 24000, format="WAV")

    return Response(content=buf.getvalue(), media_type="audio/wav")
