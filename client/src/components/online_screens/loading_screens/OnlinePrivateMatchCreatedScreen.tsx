import { useEffect, useRef, useState } from "react";

interface Props {
  roomCode: string | null;
  status: string;
  handleBack: () => void;
  connectWebSocket: (onReady?: (socket: WebSocket) => void) => void;
}

export default function OnlinePrivateMatchCreatedScreen({
  roomCode,
  status,
  handleBack,
  connectWebSocket,
}: Props) {
  const [copied, setCopied] = useState(false);
  const hasRequestedRef = useRef(false);

  useEffect(() => {
    if (hasRequestedRef.current) return;
    hasRequestedRef.current = true;

    connectWebSocket(socket => {
      socket.send(JSON.stringify({ type: "create_private_room" }));
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleCopy = async () => {
    if (!roomCode) return;
    try {
      await navigator.clipboard.writeText(roomCode);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      // Clipboard API unavailable — silently ignore, code is still visible to copy by hand.
    }
  };

  return (
    <div className="menu-root fade-in">
      <div className="waiting-spinner" aria-hidden="true">
        <div className="waiting-spinner-ring" />
      </div>

      <div className="mode-label" style={{ marginTop: "2rem" }}>
        Room Created
      </div>
      <div className="mode-desc">{status || "Waiting for an opponent..."}</div>

      {roomCode && (
        <div className="room-code-box">
          <span className="room-code-label">Share this code with a friend</span>

          <div className="room-code-chip">
            {roomCode.split("").map((char, i) => (
              <span key={i} className="room-code-char">{char}</span>
            ))}
          </div>

          <button
            className="btn btn-secondary room-code-copy-btn"
            onClick={handleCopy}
            type="button"
          >
            {copied ? "✓ Copied" : "Copy Code"}
          </button>
        </div>
      )}

      <button className="btn-back" onClick={handleBack}>
        ← Cancel
      </button>
    </div>
  );
}