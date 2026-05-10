import { useEffect, useState } from "react";
import ChessBoard from "./components/ChessBoard";
import LogRegistration from "./components/LoginRegistration";
import GameScreen from "./components/GameScreen";
import MenuScreen from "./components/MenuScreen";
import ModeSelectScreen from "./components/ModeSelection";

export type Piece = {
  name: string;
  x: number;
  y: number;
  image: string;
};

type Move = { x: number; y: number };
type Screen = "menu" | "mode-select" | "game";
type OnlineMode = "online" | "offline";

type PromotionOffer = { name: string; image: string };
type PromotionData = { x: number; y: number; color: string; offers: PromotionOffer[] };

const BASE_URL = "https://contributive-flockiest-henrietta.ngrok-free.dev";

const HEADERS = {
  "Content-Type": "application/json",
  "ngrok-skip-browser-warning": "true",
};

const styles = `
  @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700;900&family=Crimson+Text:ital,wght@0,400;0,600;1,400&display=swap');

  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    background: #0d0d0d;
    color: #e8dcc8;
    font-family: 'Crimson Text', serif;
  }

  .menu-root {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    position: relative;
    overflow: hidden;
    background: radial-gradient(ellipse at 50% 0%, #1a1208 0%, #0d0d0d 70%);
  }

  .menu-root::before {
    content: '';
    position: absolute;
    inset: 0;
    background-image:
      linear-gradient(rgba(212,175,55,0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(212,175,55,0.03) 1px, transparent 1px);
    background-size: 60px 60px;
    pointer-events: none;
  }

  .chess-crown {
    font-size: 4rem;
    margin-bottom: 0.5rem;
    filter: drop-shadow(0 0 20px rgba(212,175,55,0.5));
    animation: float 3s ease-in-out infinite;
  }

  @keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-8px); }
  }

  .game-title {
    font-family: 'Cinzel', serif;
    font-size: 3.5rem;
    font-weight: 900;
    letter-spacing: 0.15em;
    color: #d4af37;
    text-shadow: 0 0 30px rgba(212,175,55,0.4), 0 2px 0 #8b6914;
    margin-bottom: 0.25rem;
  }

  .game-subtitle {
    font-family: 'Crimson Text', serif;
    font-style: italic;
    font-size: 1.1rem;
    color: #a09070;
    letter-spacing: 0.3em;
    margin-bottom: 3rem;
  }

  .divider {
    width: 200px;
    height: 1px;
    background: linear-gradient(90deg, transparent, #d4af37, transparent);
    margin: 0 auto 2.5rem;
  }

  .btn-group {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    width: 280px;
  }

  .btn-group.horizontal {
    flex-direction: row;
    width: auto;
    gap: 1.2rem;
  }

  .btn {
    font-family: 'Cinzel', serif;
    font-size: 0.95rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    padding: 1rem 2rem;
    border: none;
    cursor: pointer;
    position: relative;
    transition: all 0.25s ease;
    text-transform: uppercase;
  }

  .btn-primary {
    background: linear-gradient(135deg, #d4af37 0%, #a07828 50%, #d4af37 100%);
    color: #0d0d0d;
    clip-path: polygon(8px 0%, 100% 0%, calc(100% - 8px) 100%, 0% 100%);
    box-shadow: 0 4px 20px rgba(212,175,55,0.3);
  }

  .btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(212,175,55,0.5);
    background: linear-gradient(135deg, #e8c84a 0%, #b8902e 50%, #e8c84a 100%);
  }

  .btn-secondary {
    background: transparent;
    color: #d4af37;
    border: 1px solid #d4af37;
    clip-path: polygon(8px 0%, 100% 0%, calc(100% - 8px) 100%, 0% 100%);
  }

  .btn-secondary:hover {
    background: rgba(212,175,55,0.1);
    transform: translateY(-2px);
    box-shadow: 0 4px 20px rgba(212,175,55,0.2);
  }

  .btn-disabled {
    background: transparent;
    color: #4a4035;
    border: 1px solid #2a2018;
    clip-path: polygon(8px 0%, 100% 0%, calc(100% - 8px) 100%, 0% 100%);
    cursor: not-allowed;
    opacity: 0.5;
  }

  .btn-back {
    font-family: 'Cinzel', serif;
    font-size: 0.75rem;
    letter-spacing: 0.2em;
    color: #6a5a40;
    background: none;
    border: none;
    cursor: pointer;
    margin-top: 2rem;
    text-transform: uppercase;
    transition: color 0.2s;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .btn-back:hover { color: #d4af37; }

  .mode-label {
    font-family: 'Cinzel', serif;
    font-size: 1.4rem;
    font-weight: 700;
    color: #d4af37;
    letter-spacing: 0.1em;
    margin-bottom: 0.75rem;
  }

  .mode-desc {
    font-family: 'Crimson Text', serif;
    font-style: italic;
    font-size: 0.95rem;
    color: #7a6a50;
    margin-bottom: 2rem;
  }

  .coming-soon-badge {
    display: inline-block;
    font-family: 'Cinzel', serif;
    font-size: 0.6rem;
    letter-spacing: 0.2em;
    padding: 0.2rem 0.5rem;
    border: 1px solid #3a2f1a;
    color: #5a4a2a;
    margin-left: 0.5rem;
    vertical-align: middle;
  }

  .game-root {
    min-height: 100vh;
    background: radial-gradient(ellipse at 50% 0%, #1a1208 0%, #0d0d0d 70%);
    display: flex;
    flex-direction: column;
    align-items: center;
    padding-top: 1.5rem;
  }

  .game-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    max-width: 700px;
    padding: 0 1rem 1rem;
    border-bottom: 1px solid rgba(212,175,55,0.15);
    margin-bottom: 1.5rem;
  }

  .game-header-title {
    font-family: 'Cinzel', serif;
    font-size: 1.2rem;
    font-weight: 700;
    color: #d4af37;
    letter-spacing: 0.1em;
  }

  .game-header-mode {
    font-family: 'Crimson Text', serif;
    font-style: italic;
    font-size: 0.95rem;
    color: #7a6a50;
  }

  .selected-info {
    font-family: 'Crimson Text', serif;
    font-style: italic;
    font-size: 1rem;
    color: #a09070;
    margin-top: 1rem;
    letter-spacing: 0.05em;
  }

  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(16px); }
    to { opacity: 1; transform: translateY(0); }
  }

  .fade-in { animation: fadeIn 0.4s ease forwards; }

  .promotion-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.85);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 100;
    animation: fadeIn 0.2s ease forwards;
  }

  .promotion-box {
    background: #1a1208;
    border: 1px solid #d4af37;
    padding: 2rem 2.5rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.5rem;
    box-shadow: 0 0 60px rgba(212,175,55,0.15);
  }

  .promotion-title {
    font-family: 'Cinzel', serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: #d4af37;
    letter-spacing: 0.2em;
    text-transform: uppercase;
  }

  .promotion-pieces {
    display: flex;
    gap: 1rem;
  }

  .promotion-piece-btn {
    background: transparent;
    border: 1px solid #3a2f1a;
    cursor: pointer;
    padding: 0.75rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    transition: all 0.2s ease;
    clip-path: polygon(8px 0%, 100% 0%, calc(100% - 8px) 100%, 0% 100%);
    min-width: 72px;
  }

  .promotion-piece-btn:hover {
    background: rgba(212,175,55,0.12);
    border-color: #d4af37;
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(212,175,55,0.2);
  }

  .promotion-piece-btn img {
    width: 56px;
    height: 56px;
    object-fit: contain;
  }

  .promotion-piece-btn span {
    font-family: 'Cinzel', serif;
    font-size: 0.6rem;
    color: #d4af37;
    letter-spacing: 0.2em;
    text-transform: uppercase;
  }
`;

export default function App() {
  const [screen, setScreen] = useState<Screen>("menu");
  const [onlineMode, setOnlineMode] = useState<OnlineMode | null>(null);
  const [pieces, setPieces] = useState<Piece[]>([]);
  const [selectedPiece, setSelectedPiece] = useState<Piece | null>(null);
  const [validMoves, setValidMoves] = useState<Move[]>([]);
  const [promotionData, setPromotionData] = useState<PromotionData | null>(null);
  const [loggedIn, setLoggedIn] = useState<boolean>(false);
  const [gameState, setGameState] = useState<{
    game_state: "ongoing" | "checkmate" | "stalemate";
    current_turn: "white" | "black";
  }>({ game_state: "ongoing", current_turn: "white" });

  useEffect(() => {
    if (screen === "game") {
      fetch(`${BASE_URL}/board`, { headers: HEADERS })
        .then(res => res.json())
        .then(setPieces)
        .catch(err => console.error("Fetch error:", err));
    }
  }, [screen]);

  const refreshBoard = () =>
    fetch(`${BASE_URL}/board`, { headers: HEADERS })
      .then(res => res.json())
      .then(board => setPieces(board));

  const refreshStatus = () =>
    fetch(`${BASE_URL}/game-status`, { headers: HEADERS })
      .then(res => res.json())
      .then(status => setGameState(status));

  const checkPromotion = async () => {
    try {
      const res = await fetch(`${BASE_URL}/pawn-reached`, { headers: HEADERS });
      const data = await res.json();
      if (data?.ok) {
        console.log("Offers with images:", data.data?.offers);
        setPromotionData(data.data);
      }
    } catch (err) {
      console.error("Promotion check error:", err);
    }
  };

  const handleSquareClick = async (row: number, col: number) => {
    if (!selectedPiece) return;

    const isValid = validMoves.some(move => move.x === col && move.y === row);
    if (!isValid) return;

    setPieces(prev =>
      prev
        .filter(p => !(p.x === col && p.y === row))
        .map(p =>
          p.name === selectedPiece.name &&
          p.x === selectedPiece.x &&
          p.y === selectedPiece.y
            ? { ...p, x: col, y: row }
            : p
        )
    );

    setSelectedPiece(null);
    setValidMoves([]);

    try {
      const res = await fetch(`${BASE_URL}/move`, {
        method: "POST",
        headers: HEADERS,
        body: JSON.stringify({
          name: selectedPiece.name,
          from: [selectedPiece.x, selectedPiece.y],
          to: [col, row],
        }),
      });

      const data = await res.json();

      if (data.ok) {
        await refreshBoard();
        await refreshStatus();
        await checkPromotion();
      } else {
        console.error("Move error:", data.error);
        await refreshBoard();
      }
    } catch (err) {
      console.error("Move request failed:", err);
    }
  };

  const handlePromotion = (pieceName: string) => {
    if (!promotionData) return;

    fetch(`${BASE_URL}/promote`, {
      method: "POST",
      headers: HEADERS,
      body: JSON.stringify({ x: promotionData.x, y: promotionData.y, piece: pieceName }),
    })
      .then(res => res.json())
      .then(() => {
        setPromotionData(null);
        refreshBoard();
      })
      .catch(err => console.error("Promotion failed:", err));
  };

  const handlePieceClick = (piece: Piece) => {
    setSelectedPiece(piece);
    fetch(`${BASE_URL}/valid-moves`, {
      method: "POST",
      headers: HEADERS,
      body: JSON.stringify(piece),
    })
      .then(res => res.json())
      .then((data: Move[]) => setValidMoves(data))
      .catch(err => console.error("Valid moves error:", err));
  };

  const handleReset = () => {
    fetch(`${BASE_URL}/game-reset`, { headers: HEADERS })
      .then(res => res.json())
      .then(data => {
        if (data === null || data?.ok === undefined || data?.ok) {
          refreshBoard();
          setGameState({ game_state: "ongoing", current_turn: "white" });
        } else {
          console.error("Reset failed", data);
        }
      })
      .catch(err => console.error("Reset request failed:", err));
  };

  const handleBack = () => {
    if (screen === "game") {
      setScreen("mode-select");
      setPieces([]);
      setSelectedPiece(null);
      setValidMoves([]);
    } else if (screen === "mode-select") {
      setOnlineMode(null);
      setScreen("menu");
    }
  };

  if (!loggedIn) {
    return <LogRegistration setLoggedIn={setLoggedIn} styles={styles} />;
  }

  return (
    <>
      <style>{styles}</style>

      {screen === "menu" && (
        <MenuScreen
          setScreen={setScreen}
          setOnlineMode={setOnlineMode}
          setLoggedIn={setLoggedIn}
        />
      )}
      {screen === "mode-select" && onlineMode === "offline" && (
        <ModeSelectScreen
          setScreen={setScreen}
          handleBack={handleBack}
        />
      )}

      {screen === "game" && (
        <GameScreen
          pieces={pieces}
          selectedPiece={selectedPiece}
          validMoves={validMoves}
          gameState={gameState}
          promotionData={promotionData}
          handleBack={handleBack}
          handleSquareClick={handleSquareClick}
          handlePieceClick={handlePieceClick}
          handlePromotion={handlePromotion}
          handleReset={handleReset}
          setLoggedIn={setLoggedIn}
          setScreen={setScreen}
          setPieces={setPieces}
          setSelectedPiece={setSelectedPiece}
          setValidMoves={setValidMoves}
        />
      )}
    </>
  );
}