import ChessBoard from "./ChessBoard";
import { Piece } from "../App";

type Move = { x: number; y: number };
type PromotionOffer = { name: string; image: string };
type PromotionData = { x: number; y: number; color: string; offers: PromotionOffer[] };

interface Props {
  pieces: Piece[];
  selectedPiece: Piece | null;
  validMoves: Move[];
  gameState: {
    game_state: "ongoing" | "checkmate" | "stalemate";
    current_turn: "white" | "black";
  };
  promotionData: PromotionData | null;
  handleBack: () => void;
  handleSquareClick: (row: number, col: number) => void;
  handlePieceClick: (piece: Piece) => void;
  handlePromotion: (pieceName: string) => void;
  handleReset: () => void;
  setLoggedIn: (value: boolean) => void;
  setScreen: (screen: "menu" | "mode-select" | "game") => void;
  setPieces: (pieces: Piece[]) => void;
  setSelectedPiece: (piece: Piece | null) => void;
  setValidMoves: (moves: Move[]) => void;
}

export default function GameScreen({
  pieces,
  selectedPiece,
  validMoves,
  gameState,
  promotionData,
  handleBack,
  handleSquareClick,
  handlePieceClick,
  handlePromotion,
  handleReset,
  setLoggedIn,
  setScreen,
  setPieces,
  setSelectedPiece,
  setValidMoves,
}: Props) {
  return (
    <div className="game-root fade-in">
      <div className="game-header">
        <div>
          <div className="game-header-title">REGICIDE</div>
          <div className="game-header-mode">Offline · 1v1</div>
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
              setScreen("menu");
              setPieces([]);
              setSelectedPiece(null);
              setValidMoves([]);
            }}
          >
            Leave
          </button>
        </div>
      </div>

      <ChessBoard
        pieces={pieces}
        selectedPiece={selectedPiece}
        validMoves={validMoves}
        onSquareClick={handleSquareClick}
        onPieceClick={handlePieceClick}
      />

      {selectedPiece && (
        <p className="selected-info">Selected: {selectedPiece.name}</p>
      )}

      {(gameState.game_state === "checkmate" || gameState.game_state === "stalemate") && (
        <button className="btn btn-primary" style={{ marginTop: "1rem" }} onClick={handleReset}>
          Reset Game
        </button>
      )}

      {promotionData && (
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