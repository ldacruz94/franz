import { useState } from "react";
import "./App.css";
import TickCircle from "./components/TickCircle";
import VoiceButton from "./components/VoiceButton";

const THEMES: Record<string, { primary: string; bright: string; dim: string; deepDim: string; bg: string }> = {
  blue:   { primary: "#00c8ff", bright: "#00e5ff", dim: "#005577", deepDim: "#003d55", bg: "#041520" },
  red:    { primary: "#ff4040", bright: "#ff7070", dim: "#660000", deepDim: "#440000", bg: "#150404" },
  green:  { primary: "#00dd77", bright: "#00ffaa", dim: "#005533", deepDim: "#003322", bg: "#041510" },
  purple: { primary: "#cc66ff", bright: "#e0aaff", dim: "#4d007a", deepDim: "#330055", bg: "#0d0415" },
  orange: { primary: "#ff9500", bright: "#ffb84d", dim: "#663300", deepDim: "#442200", bg: "#150a04" },
  gold:   { primary: "#ffd700", bright: "#ffe566", dim: "#665500", deepDim: "#443300", bg: "#151004" },
};

function applyTheme(name: string) {
  const t = THEMES[name] ?? THEMES.blue;
  const r = document.documentElement.style;
  r.setProperty("--franz-primary",  t.primary);
  r.setProperty("--franz-bright",   t.bright);
  r.setProperty("--franz-dim",      t.dim);
  r.setProperty("--franz-deep-dim", t.deepDim);
  r.setProperty("--franz-bg",       t.bg);
}

const THINKING_PROMPTS = [
  "Of course, sir. One moment.",
  "Right away, sir.",
  "Leave it to me, sir.",
  "On it, sir.",
  "Certainly, sir. Give me just a moment.",
  "At once, sir.",
  "Consider it done, sir.",
  "I'll look into that for you, sir.",
  "Very good, sir.",
];

function randomThinkingPrompt(): string {
  return THINKING_PROMPTS[Math.floor(Math.random() * THINKING_PROMPTS.length)];
}

async function chat(message: string): Promise<{ reply: string; theme?: string }> {
  const res = await fetch("http://localhost:8000/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });
  if (!res.ok) return { reply: "" };
  return res.json();
}

export default function App() {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isThinking, setIsThinking] = useState(false);

  function speak(text: string): Promise<void> {
    return fetch("http://localhost:8000/speak", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    })
      .then((res) => (res.ok ? res.blob() : Promise.reject()))
      .then((blob) => {
        const url = URL.createObjectURL(blob);
        const audio = new Audio(url);
        setIsSpeaking(true);
        audio.play();
        return new Promise<void>((resolve) => {
          audio.onended = () => {
            setIsSpeaking(false);
            URL.revokeObjectURL(url);
            resolve();
          };
          audio.onerror = () => {
            setIsSpeaking(false);
            URL.revokeObjectURL(url);
            resolve();
          };
        });
      })
      .catch(() => {});
  }

  async function handleTranscript(text: string) {
    setIsThinking(true);
    await speak(randomThinkingPrompt());
    const { reply, theme } = await chat(text);
    setIsThinking(false);
    if (theme) applyTheme(theme);
    if (reply) await speak(reply);
  }

  return (
    <div className="app">
      <TickCircle isSpeaking={isSpeaking} isThinking={isThinking} />
      <VoiceButton onTranscript={handleTranscript} />
    </div>
  );
}
