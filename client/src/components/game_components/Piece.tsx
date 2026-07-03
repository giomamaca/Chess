import { Piece } from "../../App";

interface Props {
  piece: Piece;
  onClick: () => void;
}

export default function PieceComponent({ piece, onClick }: Props) {
  return (
    <img
      src={`${process.env.PUBLIC_URL}/${piece.image}`}
      alt={piece.name}
      draggable={false}
      onClick={onClick}
      style={{
        width: "90%",
        height: "90%",
        position: "absolute",
        top: "50%",
        left: "50%",
        transform: "translate(-50%, -50%)",
        cursor: "grab",
      }}
    />
  );
}