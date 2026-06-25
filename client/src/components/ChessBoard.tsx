import Square from "./Square";
import { Piece } from "../App";

interface Props {
  pieces: Piece[];
  validMoves: { x: number; y: number }[];
  onSquareClick?: (row: number, col: number) => void;
  onPieceClick?: (piece: Piece) => void;
  selectedPiece?: Piece | null;
  flipped?: boolean;
}

export default function ChessBoard({
  pieces,
  validMoves,
  onSquareClick,
  onPieceClick,
  selectedPiece,
  flipped = false,
}: Props) {
  const getPieceAt = (x: number, y: number) =>
    pieces.find(p => p.x === x && p.y === y);

  const isValidMove = (x: number, y: number) =>
    validMoves.some(move => move.x === x && move.y === y);

  return (
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: "80vh",
      }}
    >
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(8, 70px)",
          gridTemplateRows: "repeat(8, 70px)",
          border: "4px solid black",
        }}
      >
        {Array.from({ length: 8 }).map((_, vRow) =>
          Array.from({ length: 8 }).map((_, vCol) => {
            // Map the on-screen cell to logical board coordinates.
            // When flipped (black's view) the board is rotated 180°,
            // but lookups + click handlers always use absolute coords.
            const col = flipped ? 7 - vCol : vCol;
            const row = flipped ? 7 - vRow : vRow;

            const piece = getPieceAt(col, row);
            const selected =
              selectedPiece?.x === col && selectedPiece?.y === row;

            return (
              <Square
                key={`${vRow}-${vCol}`}
                x={col}
                y={row}
                piece={piece}
                isSelected={selected}
                isValidMove={isValidMove(col, row)}
                onClick={() => onSquareClick?.(row, col)}
                onPieceClick={onPieceClick}
              />
            );
          })
        )}
      </div>
    </div>
  );
}