from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import Response

from .models import ChatRequest, SpeakRequest
from .services import chat, synthesize_speech, transcribe_audio

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    data = await audio.read()
    try:
        transcript = transcribe_audio(data, audio.filename or "audio.webm")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"transcript": transcript}


@router.post("/chat")
def chat_endpoint(req: ChatRequest):
    try:
        return chat(req.message)
    except Exception as e:
        print(f"[chat error] {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/speak")
def speak(req: SpeakRequest):
    try:
        return Response(content=synthesize_speech(req.text), media_type="audio/wav")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
