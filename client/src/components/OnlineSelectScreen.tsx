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

export default function OnlineSelectScreen({ setScreen, handleBack }: Props) {
  return (
    <div className="menu-root fade-in">
      <div className="chess-crown" style={{ fontSize: "2.5rem" }}>♜</div>
      <p className="mode-label">Online Mode</p>
      <p className="mode-desc">How do you want to play?</p>
      <div className="divider" />
      <div className="btn-group">
        <button
          className="btn btn-primary"
          onClick={() => setScreen("online-lobby")}
        >
          Private Lobby
        </button>
        <button
          className="btn btn-primary"
          onClick={() => setScreen("online-join")}
        >
          Quick Match
        </button>
      </div>
      <button className="btn-back" onClick={handleBack}>← Back</button>
    </div>
  );
}