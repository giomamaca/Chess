import { useEffect, useRef, useState } from "react";
import LogRegistration from "./components/LoginRegistration";
import GameScreen from "./components/GameScreen";
import MenuScreen from "./components/MenuScreen";
import OfflineSelectScreen from "./components/OfflineSelectScreen";
import OnlineSelectScreen from "./components/OnlineSelectScreen";
import OnlinePrivateSelectScreen from "./components/OnlinePrivateSelectScreen";
import OnlineJoinScreen from "./components/OnlineJoinScreen";
import OnlineQuickMatchScreen from "./components/OnlineQuickMatchScreen";
import { Screen, Piece, Move, PromotionData } from "./types";
import BASE_URL from "./config";
import styles from "./styles";

export type { Piece };

const HEADERS = {
  "Content-Type": "application/json",
  "ngrok-skip-browser-warning": "true",
};

export default function App() {
  const ws = useRef<WebSocket | null>(null);
  const [screen, setScreen] = useState<Screen>("registration");
  const [onlineStatus, setOnlineStatus] = useState("Connecting...");
  const [pieces, setPieces] = useState<Piece[]>([]);
  const [validMoves, setValidMoves] = useState<Move[]>([]);
  const [selectedPiece, setSelectedPiece] = useState<Piece | null>(null);
  const [promotionData, setPromotionData] = useState<PromotionData | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null); 
  const [loggedIn, setLoggedIn] = useState<boolean>(false);
  const [gameType, setGameType] = useState<String | null> (null); 
  const [gameState, setGameState] = useState<{
    game_state: "ongoing" | "checkmate" | "stalemate";
    current_turn: "white" | "black";
  }>({ game_state: "ongoing", current_turn: "white" });

  const handleGameStart = async () => {
    const res = await fetch(`${BASE_URL}/${gameType}/create`, { headers: HEADERS, method: "POST" });
    const data = await res.json();
    setSessionId(data.session_id);
    setScreen("game-offline");
  };

  useEffect(() => {
    if (screen === "game-offline" && sessionId) {
      fetch(`${BASE_URL}/${gameType}/board/${sessionId}`, { headers: HEADERS })
        .then(res => res.json())
        .then(setPieces);
    }
  }, [screen, sessionId]);

  useEffect(() => {
    if (screen === "game-offline") {
      setGameType("offline")
    }else if (screen === "game-online"){
      setGameType("online");
    }
  }, [screen]);

  const connectWebSocket = (onReady?: (socket: WebSocket) => void) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      onReady?.(ws.current);
      return;
    }

    const socket = new WebSocket(`${BASE_URL.replace("https", "wss")}/ws`);
    ws.current = socket;

    socket.addEventListener("open", () => {
      const savedName = localStorage.getItem("name");
      if (savedName) socket.send(savedName);
      onReady?.(socket);
    });
    
    socket.addEventListener("message", (event: MessageEvent) => {
      const data = JSON.parse(event.data);
      if (data.type === "game_start") setScreen("game-online");
      if (data.type === "searching") setOnlineStatus("Waiting for an opponent...");
      if (data.type === "error") setOnlineStatus(data.message);
    });

    socket.addEventListener("close", () => {
      console.log("Disconnected");
      setTimeout(() => {
        const savedName = localStorage.getItem("name");
        if (savedName) connectWebSocket();
      }, 2000);
    });

    socket.addEventListener("error", (err) => {
      console.error("WebSocket error:", err);
    });
  };

  const refreshBoard = () =>
    fetch(`${BASE_URL}/${gameType}/board/${sessionId}`, { headers: HEADERS })
      .then(res => res.json())
      .then(setPieces);

  const handleSquareClick = async (row: number, col: number) => {
    if (!selectedPiece) return;
    const isValid = validMoves.some(move => move.x === col && move.y === row);
    if (!isValid) return;

    setPieces(prev =>
      prev
        .filter(p => !(p.x === col && p.y === row))
        .map(p =>
          p.name === selectedPiece.name && p.x === selectedPiece.x && p.y === selectedPiece.y
            ? { ...p, x: col, y: row }
            : p
        )
    );
    setSelectedPiece(null);
    setValidMoves([]);

    try {
      const res = await fetch(`${BASE_URL}/${gameType}/move/${sessionId}`, {
        method: "POST",
        headers: HEADERS,
        body: JSON.stringify({
          from: [selectedPiece.x, selectedPiece.y],
          to: [col, row],
        }),
      });
      const data = await res.json();
      if (data.ok) {
        setPieces(data.board);
        setGameState(data.game_status);
        if (data.promotion?.ok) setPromotionData(data.promotion.data);
      } else {
        await refreshBoard();
      }
    } catch {
      await refreshBoard();
    }
  };

  const handlePromotion = (pieceName: string) => {
    if (!promotionData) return;
    fetch(`${BASE_URL}/${gameType}/promote/${sessionId}`, {
      method: "POST",
      headers: HEADERS,
      body: JSON.stringify({ x: promotionData.x, y: promotionData.y, piece: pieceName }),
    })
      .then(res => res.json())
      .then(() => { setPromotionData(null); refreshBoard(); });
  };

  const handlePieceClick = (piece: Piece) => {
    setSelectedPiece(piece);
    setValidMoves([]);
    fetch(`${BASE_URL}/${gameType}/valid-moves/${sessionId}`, {
      method: "POST",
      headers: HEADERS,
      body: JSON.stringify(piece),
    })
      .then(res => res.json())
      .then((data: Move[]) => setValidMoves(data));
  };

  const handleReset = () => {
    fetch(`${BASE_URL}/${gameType}/reset/${sessionId}`, { method: "POST", headers: HEADERS })
      .then(res => res.json())
      .then(data => {
        if (data?.ok) {
          refreshBoard();
          setGameState({ game_state: "ongoing", current_turn: "white" });
        }
      });
  };

  const handleBack = () => {
    if (screen === "game-offline") {
      // end session when leaving
      fetch(`${BASE_URL}/${gameType}/end/${sessionId}`, { method: "DELETE", headers: HEADERS });
      setSessionId(null);
      setScreen("offline-setup");
      setPieces([]);
      setSelectedPiece(null);
      setValidMoves([]);
    } else if (screen === "offline-setup" || screen === "online-setup") {
      setScreen("menu");
    } else if (screen === "online-private") {
      setScreen("online-setup");
    } else if (
      screen === "online-create-lobby" ||
      screen === "online-join-lobby" ||
      screen === "online-quick-match"
    ) {
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
        <OfflineSelectScreen
          setScreen={setScreen}
          handleBack={handleBack}
          onStartGame={handleGameStart}
        />
      )}
      {screen === "online-setup" && (
        <OnlineSelectScreen setScreen={setScreen} handleBack={handleBack} />
      )}

      {screen === "online-private" && (
        <OnlinePrivateSelectScreen setScreen={setScreen} handleBack={handleBack} />
      )}
      
      {screen === "online-quick-match" && (
        <OnlineQuickMatchScreen
          setScreen={setScreen}
          handleBack={handleBack}
          connectWebSocket={connectWebSocket}
          status={onlineStatus}
        />
      )}

      {screen === "online-join-lobby" && (
        <OnlineJoinScreen
          setScreen={setScreen}
          handleBack={handleBack}
          connectWebSocket={connectWebSocket}
        />
      )}

      {screen === "game-offline" && (
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