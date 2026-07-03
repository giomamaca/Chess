import { useEffect } from "react";
import { Screen } from "../../../types";

interface Props {
  handleBack: () => void;
  connectWebSocket: (onReady: (socket: WebSocket) => void) => void;
  status: string;
}

export default function OnlineQuickMatchScreen({handleBack, connectWebSocket, status }: Props) {
  useEffect(() => {
    connectWebSocket((socket: WebSocket) => {
      socket.send(JSON.stringify({ type: "quick_match" }));
    });
  }, []);

  return (
    <div className="menu-root fade-in">
      <div className="chess-crown" style={{ fontSize: "2.5rem" }}>♟</div>
      <p className="mode-label">Quick Match</p>
      <p className="mode-desc">{status}</p>
      <div className="divider" />
      <div style={{
        width: "40px", height: "40px",
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