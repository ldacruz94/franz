import { useState, useRef } from "react";
import "./VoiceButton.css";

type Status = "idle" | "listening" | "processing" | "error";

interface Props {
  onTranscript?: (text: string) => void;
}

function mimeExtension(mimeType: string): string {
  if (mimeType.includes("ogg")) return "ogg";
  if (mimeType.includes("mp4")) return "mp4";
  return "webm";
}

export default function VoiceButton({ onTranscript }: Props) {
  const [status, setStatus] = useState<Status>("idle");
  const [transcript, setTranscript] = useState("");
  const [errorMsg, setErrorMsg] = useState("");
  const recorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const btnRef = useRef<HTMLButtonElement>(null);
  const audioCtxRef = useRef<AudioContext | null>(null);
  const animFrameRef = useRef<number>(0);

  function startVolumeAnimation(stream: MediaStream) {
    const ctx = new AudioContext();
    const analyser = ctx.createAnalyser();
    analyser.fftSize = 256;
    ctx.createMediaStreamSource(stream).connect(analyser);
    audioCtxRef.current = ctx;

    const data = new Uint8Array(analyser.frequencyBinCount);
    function frame() {
      analyser.getByteFrequencyData(data);
      const avg = data.reduce((a, b) => a + b, 0) / data.length;
      const glow = Math.round(avg * 0.6);
      const ring = Math.round(avg * 0.15);
      if (btnRef.current) {
        btnRef.current.style.boxShadow =
          `0 0 ${glow}px rgba(143, 211, 255, 0.5), 0 0 0 ${ring}px rgba(143, 211, 255, 0.15)`;
        btnRef.current.style.transform = `scale(${1 + avg / 255 * 0.18})`;
      }
      animFrameRef.current = requestAnimationFrame(frame);
    }
    animFrameRef.current = requestAnimationFrame(frame);
  }

  function stopVolumeAnimation() {
    cancelAnimationFrame(animFrameRef.current);
    audioCtxRef.current?.close();
    audioCtxRef.current = null;
    if (btnRef.current) {
      btnRef.current.style.boxShadow = "";
      btnRef.current.style.transform = "";
    }
  }

  async function toggle() {
    if (status === "listening") {
      recorderRef.current?.stop();
      return;
    }

    setTranscript("");
    setErrorMsg("");

    let stream: MediaStream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch {
      setErrorMsg("Mic access denied — check browser permissions.");
      setStatus("error");
      return;
    }

    startVolumeAnimation(stream);

    const recorder = new MediaRecorder(stream);
    recorderRef.current = recorder;
    chunksRef.current = [];

    recorder.ondataavailable = (e) => {
      if (e.data.size > 0) chunksRef.current.push(e.data);
    };

    recorder.onstop = async () => {
      stopVolumeAnimation();
      stream.getTracks().forEach((t) => t.stop());
      setStatus("processing");

      const mimeType = recorder.mimeType;
      const ext = mimeExtension(mimeType);
      const blob = new Blob(chunksRef.current, { type: mimeType });
      const form = new FormData();
      form.append("audio", blob, `audio.${ext}`);

      try {
        const res = await fetch("http://localhost:8000/transcribe", {
          method: "POST",
          body: form,
        });
        if (!res.ok) throw new Error(await res.text());
        const { transcript: text } = await res.json();
        setTranscript(text);
        onTranscript?.(text);
      } catch (err: any) {
        setErrorMsg("Transcription failed — is the backend running?");
        setStatus("error");
        return;
      }

      setStatus("idle");
    };

    recorder.start();
    setStatus("listening");
  }

  const label =
    status === "listening" ? "Stop" :
    status === "processing" ? "Processing…" :
    "Speak";

  return (
    <div className="voice-container">
      {transcript && <p className="voice-transcript">{transcript}</p>}
      {errorMsg && <p className="voice-error">{errorMsg}</p>}
      <button
        ref={btnRef}
        className={`voice-btn voice-btn--${status}`}
        onClick={toggle}
        disabled={status === "processing"}
        aria-label={label}
      >
        <MicIcon />
      </button>
    </div>
  );
}

function MicIcon() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <rect x="9" y="2" width="6" height="11" rx="3" fill="currentColor" />
      <path
        d="M5 11a7 7 0 0 0 14 0"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        fill="none"
      />
      <line x1="12" y1="18" x2="12" y2="22" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
      <line x1="8" y1="22" x2="16" y2="22" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}
