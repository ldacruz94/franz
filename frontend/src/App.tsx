import { useState } from "react";
import "./App.css";
import TickCircle from "./components/TickCircle";
import VoiceButton from "./components/VoiceButton";

async function chat(message: string): Promise<string> {
  const res = await fetch("http://localhost:8000/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });
  if (!res.ok) return "";
  const { reply } = await res.json();
  return reply;
}

export default function App() {
  const [isSpeaking, setIsSpeaking] = useState(false);

  async function speak(text: string) {
    const res = await fetch("http://localhost:8000/speak", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    if (!res.ok) return;
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const audio = new Audio(url);
    setIsSpeaking(true);
    audio.play();
    audio.onended = () => {
      setIsSpeaking(false);
      URL.revokeObjectURL(url);
    };
  }

  async function handleTranscript(text: string) {
    const reply = await chat(text);
    if (reply) speak(reply);
  }

  return (
    <div className="app">
      <TickCircle isSpeaking={isSpeaking} />
      <VoiceButton onTranscript={handleTranscript} />
    </div>
  );
}
