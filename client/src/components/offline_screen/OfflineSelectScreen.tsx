import { Screen } from "../../types";

interface Props {
  handleBack: () => void;
  onStartGame: () => void;
}

export default function OfflineSelectScreen({handleBack, onStartGame }: Props) {
  return (
    <div className="menu-root fade-in">
      <div className="chess-crown" style={{ fontSize: "2.5rem" }}>♟</div>
      <p className="mode-label">Offline Mode</p>
      <p className="mode-desc">Choose your opponent</p>
      <div className="divider" />
      <div className="btn-group">
        <button
          className="btn btn-primary"
          onClick={onStartGame}
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