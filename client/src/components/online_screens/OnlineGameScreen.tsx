import { useEffect, useRef, useState } from "react";
import ChessBoard from "../game_components/ChessBoard";
import { Piece } from "../../App";
import { Screen } from "../../types";
import Chat  from "../game_components/Chat";

type Move = { x: number; y: number };
type PromotionOffer = { name: string; image: string };
type PromotionData = { x: number; y: number; color: string; offers: PromotionOffer[] };
type ChatMessage = { sender: string; text: string };

interface Props {
  pieces: Piece[];
  selectedPiece: Piece | null;
  validMoves: Move[];
  gameState: {
    game_state: "ongoing" | "checkmate" | "stalemate";
    current_turn: "white" | "black";
  };
  promotionData: PromotionData | null;
  myColor: "white" | "black" | null;
  chatMessages: ChatMessage[];
  sendChatMessage: (text: string) => void;
  handleBack: () => void;
  handleSquareClick: (row: number, col: number) => void;
  handlePieceClick: (piece: Piece) => void;
  handlePromotion: (pieceName: string) => void;
  setLoggedIn: (value: boolean) => void;
  setScreen: (screen: Screen) => void;
  setPieces: (pieces: Piece[]) => void;
  setSelectedPiece: (piece: Piece | null) => void;
  setValidMoves: (moves: Move[]) => void;
}

export default function OnlineGameScreen({
  pieces,
  selectedPiece,
  validMoves,
  gameState,
  promotionData,
  myColor,
  chatMessages,
  sendChatMessage,
  handleBack,
  handleSquareClick,
  handlePieceClick,
  handlePromotion,
  setLoggedIn,
  setScreen,
  setPieces,
  setSelectedPiece,
  setValidMoves,
}: Props) {
  const flipped = myColor === "black";
  const isOver =
    gameState.game_state === "checkmate" || gameState.game_state === "stalemate";
  const isMyTurn = gameState.current_turn === myColor;

  const winner = gameState.current_turn === "white" ? "Black" : "White";

  // ---------- Chat ----------
  const [draft, setDraft] = useState("");
  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const myName = localStorage.getItem("name");

  // Keep the newest message in view
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages]);

  const handleSend = () => {
    if (!draft.trim()) return;
    sendChatMessage(draft);
    setDraft("");
  };

  return (
    <div className="game-root fade-in">
      <div className="game-header">
        <div>
          <div className="game-header-title">Chess</div>
          <div className="game-header-mode">Online · 1v1</div>
        </div>
        <div style={{ display: "flex", gap: "0.75rem" }}>
          <button
            className="btn btn-secondary"
            style={{ padding: "0.5rem 1.2rem", fontSize: "0.75rem" }}
            onClick={handleBack}
          >
            ← Menu
          </button>
          <button
            className="btn btn-secondary"
            style={{ padding: "0.5rem 1.2rem", fontSize: "0.75rem", borderColor: "#8b3a3a", color: "#c0392b" }}
            onClick={() => {
              setLoggedIn(false);
              setScreen("registration");
              setPieces([]);
              setSelectedPiece(null);
              setValidMoves([]);
            }}
          >
            Sign Out
          </button>
        </div>
      </div>

      <div className="game-layout">
        {/* ---------- Left column: board ---------- */}
        <div className="game-board-area">
          {myColor && (
            <div
              style={{
                textAlign: "center",
                margin: "0 0 0.75rem",
                fontSize: "0.85rem",
                letterSpacing: "0.05em",
                opacity: isMyTurn || isOver ? 1 : 0.6,
              }}
            >
              You are {myColor === "white" ? "White" : "Black"} ·{" "}
              {isOver ? "Game over" : isMyTurn ? "Your move" : "Opponent's move"}
            </div>
          )}

          <ChessBoard
            pieces={pieces}
            selectedPiece={selectedPiece}
            validMoves={validMoves}
            onSquareClick={handleSquareClick}
            onPieceClick={handlePieceClick}
            flipped={flipped}
          />

          {selectedPiece && (
            <p className="selected-info">Selected: {selectedPiece.name}</p>
          )}

          {isOver && (
            <div style={{ marginTop: "1rem", textAlign: "center" }}>
              <p className="selected-info">
                {gameState.game_state === "checkmate"
                  ? `Checkmate — ${winner} wins`
                  : "Stalemate — draw"}
              </p>
              <button className="btn btn-primary" onClick={handleBack}>
                Back to Menu
              </button>
            </div>
          )}
        </div>

      <Chat chatMessages={chatMessages} sendChatMessage={sendChatMessage} />
      </div>

      {promotionData && promotionData.color === myColor && (
        <div className="promotion-overlay">
          <div className="promotion-box">
            <div className="promotion-pieces">
              {promotionData.offers.map(offer => (
                <button
                  key={offer.name}
                  className="promotion-piece-btn"
                  onClick={() => handlePromotion(offer.name)}
                >
                  <img
                    src={`${process.env.PUBLIC_URL}/${offer.image}`}
                    alt={offer.name}
                    width={60}
                    height={60}
                  />
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}