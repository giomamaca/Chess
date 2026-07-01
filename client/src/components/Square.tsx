import PieceComponent from "./Piece";
import { Piece } from "../App";

interface Props {
  x: number;
  y: number;
  piece?: Piece;
  isSelected?: boolean;
  isValidMove?: boolean;
  onClick?: () => void;
  onPieceClick?: (piece: Piece) => void;
}

export default function Square({
  x,
  y,
  piece,
  isSelected,
  isValidMove,
  onClick,
  onPieceClick,
}: Props) {
  const isDark = (x + y) % 2 === 1;
  let backgroundColor = isDark ? "#769656" : "#eeeed2";

  if (isSelected) backgroundColor = "#f6f669";
  if (isValidMove && piece) backgroundColor = "#cc4444";

  return (
    <div
      onClick={onClick}
      style={{
        width: "70px",
        height: "70px",
        backgroundColor,
        position: "relative",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        cursor: "pointer",
        userSelect: "none",
        border: "1px solid black",
      }}
    >
      {isValidMove && !piece && (
        <div
          style={{
            width: "18px",
            height: "18px",
            borderRadius: "50%",
            backgroundColor: "rgba(0,0,0,0.3)",
            position: "absolute",
          }}
        />
      )}
      {piece && (
        <PieceComponent
          piece={piece}
          onClick={isValidMove ? onClick! : () => onPieceClick?.(piece)}
        />
      )}
    </div>
  );
}