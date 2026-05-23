import "./App.css";
import TickCircle from "./components/TickCircle";
import VoiceButton from "./components/VoiceButton";

export default function App() {
  function handleTranscript(text: string) {
    console.log("Franz heard:", text);
  }

  return (
    <div className="app">
      <TickCircle />
      <VoiceButton onTranscript={handleTranscript} />
    </div>
  );
}
