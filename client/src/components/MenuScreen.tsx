import { Screen } from "../types";

interface Props {
  setScreen: (screen: Screen) => void;
  setLoggedIn: (value: boolean) => void;
}

export default function MenuScreen({ setScreen, setLoggedIn }: Props) {
  return (
    <div className="menu-root fade-in">
      <div style={{ position: "absolute", top: "1.5rem", right: "1.5rem" }}>
        <button
          className="btn btn-secondary"
          style={{ padding: "0.5rem 1.2rem", fontSize: "0.75rem", borderColor: "#8b3a3a", color: "#c0392b" }}
          onClick={() => setLoggedIn(false)}
        >
          Sign Out
        </button>
      </div>
      <div className="chess-crown">♛</div>
      <h1 className="game-title">Chess</h1>
      <p className="game-subtitle">A Chess Experience</p>
      <div className="divider" />
      <div className="btn-group">
        <button
          className="btn btn-primary"
          onClick={() => setScreen("offline-setup")}
        >
          Offline
        </button>
        <button
          className="btn btn-primary"
          onClick={() => setScreen("online-setup")}
        >
          Online
        </button>
      </div>
    </div>
  );
}