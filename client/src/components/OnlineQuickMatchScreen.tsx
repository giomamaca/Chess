import { useEffect, useState } from "react";
import { Screen } from "../types";

interface Props {
  setScreen: (screen: Screen) => void;
  handleBack: () => void;
  ws: WebSocket | null;
  connectWebSocket: (cb: () => void) => void;
}

export default function OnlineQuickMatchScreen({ setScreen, handleBack, ws, connectWebSocket }: Props) {
  const [status, setStatus] = useState("Connecting...");

  useEffect(() => {
    connectWebSocket(() => {
      setStatus("Searching for an opponent...");
      ws?.send(JSON.stringify({ type: "quick_match" }));
    });
  }, []);

  useEffect(() => {
    if (!ws) return;
    const handleMessage = (event: MessageEvent) => {
      const data = JSON.parse(event.data);
      if (data.type === "game_start") setScreen("game");
      if (data.type === "searching") setStatus("Waiting for an opponent...");
      if (data.type === "error") setStatus(data.message);
    };
    ws.addEventListener("message", handleMessage);
    return () => ws.removeEventListener("message", handleMessage);
  }, [ws]);

  return (
    <div className="menu-root fade-in">
      <div className="chess-crown" style={{ fontSize: "2.5rem" }}>♟</div>
      <p className="mode-label">Quick Match</p>
      <p className="mode-desc">{status}</p>
      <div className="divider" />
      <div style={{
        width: "40px",
        height: "40px",
        border: "3px solid #2a2a2a",
        borderTop: "3px solid #d4af37",
        borderRadius: "50%",
        animation: "spin 1s linear infinite",
      }} />
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      <button className="btn-back" onClick={handleBack}>← Back</button>
    </div>
  );
}