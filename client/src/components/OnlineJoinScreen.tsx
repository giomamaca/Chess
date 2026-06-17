import { useEffect, useRef, useState } from "react";
import { Screen } from "../types";

interface Props {
  setScreen: (screen: Screen) => void;
  handleBack: () => void;
  connectWebSocket: (onReady: (socket: WebSocket) => void) => void;
}

export default function OnlineJoinScreen({ setScreen, handleBack, connectWebSocket }: Props) {
  const [code, setCode] = useState("");
  const [status, setStatus] = useState("");
  const [searching, setSearching] = useState(false);
  const socketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    connectWebSocket((socket: WebSocket) => {
      socketRef.current = socket;

      socket.addEventListener("message", (event: MessageEvent) => {
        const data = JSON.parse(event.data);
        if (data.type === "game_start") setScreen("game-online");
        if (data.type === "error") {
          setStatus(data.message);
          setSearching(false);
        }
      });
    });
  }, []);

  const handleJoinPrivate = () => {
    if (!socketRef.current || !code.trim()) return;
    setSearching(true);
    setStatus("Joining room...");
    socketRef.current.send(JSON.stringify({
      type: "join_private_room",
      room_code: code.trim().toUpperCase()
    }));
  };

  return (
    <div className="menu-root fade-in">
      <div className="chess-crown" style={{ fontSize: "2.5rem" }}>♟</div>
      <p className="mode-label">Join Private Room</p>
      <p className="mode-desc">Enter the room code</p>
      <div className="divider" />

      <div style={{ width: "280px", display: "flex", flexDirection: "column", gap: "0.75rem" }}>
        <input
          type="text"
          maxLength={6}
          placeholder="Enter room code"
          value={code}
          onChange={e => setCode(e.target.value.toUpperCase())}
          style={{
            background: "#080808",
            border: "1px solid #222",
            padding: "0.7rem 0.9rem",
            color: "#e8dcc8",
            fontFamily: "Cinzel, serif",
            fontSize: "1.2rem",
            letterSpacing: "0.3em",
            textAlign: "center",
            outline: "none",
            width: "100%",
            boxSizing: "border-box",
          }}
        />
        <button
          className="btn btn-primary"
          onClick={handleJoinPrivate}
          disabled={searching || !code.trim()}
        >
          {searching ? "Joining..." : "Join Room"}
        </button>

        {status && (
          <p style={{
            textAlign: "center",
            fontFamily: "Crimson Text, serif",
            fontStyle: "italic",
            fontSize: "0.9rem",
            color: status.includes("not found") || status.includes("error") ? "#c0392b" : "#a09070",
          }}>
            {status}
          </p>
        )}
      </div>

      <button className="btn-back" onClick={handleBack}>← Back</button>
    </div>
  );
}