type Screen =
  | "registration"
  | "menu"
  | "offline-select"
  | "online-select"
  | "online-lobby"
  | "online-join"
  | "game";

interface Props {
  setScreen: (screen: Screen) => void;
  handleBack: () => void;
}

export default function OfflineSelectScreen({ setScreen, handleBack }: Props) {
  return (
    <div className="menu-root fade-in">
      <div className="chess-crown" style={{ fontSize: "2.5rem" }}>♟</div>
      <p className="mode-label">Offline Mode</p>
      <p className="mode-desc">Choose your opponent</p>
      <div className="divider" />
      <div className="btn-group">
        <button
          className="btn btn-primary"
          onClick={() => setScreen("game")}
        >
          1 v 1
        </button>
        <button className="btn btn-disabled" disabled>
          vs AI <span className="coming-soon-badge">Soon</span>
        </button>
      </div>
      <button className="btn-back" onClick={handleBack}>← Back</button>
    </div>
  );
}