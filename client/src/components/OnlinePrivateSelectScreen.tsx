import { Screen } from "../types";

interface Props {
  setScreen: (screen: Screen) => void;
  handleBack: () => void;
}

export default function OnlinePrivateSelectScreen({ setScreen, handleBack }: Props) {
  return (
    <div className="menu-root fade-in">
      <div className="chess-crown" style={{ fontSize: "2.5rem" }}>♜</div>
      <p className="mode-label">Private Lobby</p>
      <p className="mode-desc">Play with a friend using a private room</p>
      <div className="divider" />

      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "1rem", width: "100%" }}>
        <button
          className="btn btn-primary"
          style={{ width: "220px" }}
          onClick={() => setScreen("online-create-lobby")}
        >
          Create Room
        </button>
        <button
          className="btn btn-secondary"
          style={{ width: "220px" }}
          onClick={() => setScreen("online-join-lobby")}
        >
          Join Room
        </button>
      </div>

      <button className="btn-back" onClick={handleBack}>← Back</button>
    </div>
  );
}