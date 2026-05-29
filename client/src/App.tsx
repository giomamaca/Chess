import { useEffect, useRef, useState } from "react";
import LogRegistration from "./components/LoginRegistration";
import GameScreen from "./components/GameScreen";
import MenuScreen from "./components/MenuScreen";
import OfflineSelectScreen from "./components/OfflineSelectScreen";
import OnlineSelectScreen from "./components/OnlineSelectScreen";
import OnlinePrivateLobbyScreen from "./components/OnlinePrivateSelectScreen";
import OnlineJoinScreen from "./components/OnlineJoinScreen";
import { Screen, Piece, Move, PromotionData } from "./types";

import BASE_URL from "./config";
import styles from "./styles";
import OnlineQuickMatchScreen from "./components/OnlineQuickMatchScreen";

export type { Piece };

const HEADERS = {
  "Content-Type": "application/json",
  "ngrok-skip-browser-warning": "true",
};

export default function App() {
  const ws = useRef<WebSocket | null>(null);
  const [screen, setScreen] = useState<Screen>("registration");
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

  const connectWebSocket = (name: string, onReady?: () => void) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      onReady?.();
      return;
    }

    const socket = new WebSocket(`${BASE_URL.replace("https", "wss")}/ws`);
    ws.current = socket;

    socket.onopen = () => {
      socket.send(name);
      onReady?.();
    };

    socket.onmessage = (event: MessageEvent) => {
      const data = JSON.parse(event.data);
      if (data.type === "game_start" || data.type === "game_resume") {
        localStorage.setItem("game_id", data.game_id);
        localStorage.setItem("game_color", data.color);
        setScreen("game");
      }
    };

    socket.onclose = () => {
      console.log("Disconnected");
      setTimeout(() => {
        const savedName = localStorage.getItem("name");
        if (savedName) connectWebSocket(savedName);
      }, 2000);
    };
  };

  const refreshBoard = () =>
    fetch(`${BASE_URL}/board`, { headers: HEADERS })
      .then(res => res.json())
      .then(board => setPieces(board));

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
        setPieces(data.board);
        setGameState(data.game_status);
        if (data.promotion?.ok) {
          setPromotionData(data.promotion.data);
        }
      } else {
        console.error("Move error:", data.error);
        await refreshBoard();
      }
    } catch (err) {
      console.error("Move request failed:", err);
      await refreshBoard();
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
      .then(() => { setPromotionData(null); refreshBoard(); })
      .catch(err => console.error("Promotion failed:", err));
  };

  const handlePieceClick = (piece: Piece) => {
    setSelectedPiece(piece);
    setValidMoves([]);
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
      setScreen("offline-setup");
      setPieces([]);
      setSelectedPiece(null);
      setValidMoves([]);
    } else if (screen === "offline-setup" || screen === "online-setup") {
      setScreen("menu");
    } else if (screen === "online-private") {
      setScreen("online-setup");
    } else if (screen === "online-create-lobby" || screen === "online-join-lobby") {
      setScreen("online-private");
    } else if (screen === "menu") {
      setLoggedIn(false);
      setScreen("registration");
    }
  };

  if (!loggedIn) {
    return (
      <LogRegistration
        setLoggedIn={setLoggedIn}
        setScreen={setScreen}
        styles={styles}
      />
    );
  }

  if (screen === "registration") {
    setScreen("menu");
    return null;
  }

  return (
    <>
      <style>{styles}</style>

      {screen === "menu" && (
        <MenuScreen setScreen={setScreen} setLoggedIn={setLoggedIn} />
      )}

      {screen === "offline-setup" && (
        <OfflineSelectScreen setScreen={setScreen} handleBack={handleBack} />
      )}

      {screen === "online-setup" && (
        <OnlineSelectScreen setScreen={setScreen} handleBack={handleBack} />
      )}

      {screen === "online-private" && (
        <OnlineSelectScreen
          setScreen={(s) => {
            const savedName = localStorage.getItem("name");
            if (savedName) connectWebSocket(savedName);
            setScreen(s);
          }}
          handleBack={handleBack}
        />
      )}

      {screen === "online-quick-match" && (
        <OnlineQuickMatchScreen
          setScreen={setScreen}
          handleBack={handleBack}
          ws={ws.current}
          connectWebSocket={(cb) => {
            const savedName = localStorage.getItem("name");
            if (savedName) connectWebSocket(savedName, cb);
          }}
        />
      )}

      {screen === "online-join-lobby" && (
        <OnlineJoinScreen
          setScreen={setScreen}
          handleBack={handleBack}
          ws={ws.current}
          connectWebSocket={(cb) => {
            const savedName = localStorage.getItem("name");
            if (savedName) connectWebSocket(savedName, cb);
          }}
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