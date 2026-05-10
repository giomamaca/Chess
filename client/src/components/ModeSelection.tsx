type Screen = "menu" | "mode-select" | "game";

interface Props {
  setScreen: (screen: Screen) => void;
  handleBack: () => void;
}

export default function ModeSelectScreen({ setScreen, handleBack }: Props) {
  return (
    <div className="menu-root fade-in">
      <div className="chess-crown" style={{ fontSize: "2.5rem" }}>♞</div>
      <p className="mode-label">Choose Your Battle</p>
      <p className="mode-desc">Offline Mode</p>
      <div className="divider" />
      <div className="btn-group horizontal">
        <button className="btn btn-primary" onClick={() => setScreen("game")}>1 v 1</button>
        <button className="btn btn-disabled" disabled>
          vs AI <span className="coming-soon-badge">Soon</span>
        </button>
      </div>
      <button className="btn-back" onClick={handleBack}>← Back</button>
    </div>
  );
}