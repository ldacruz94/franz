from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str


class SpeakRequest(BaseModel):
    text: str
