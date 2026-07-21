from .board import Board
from .move_generator import MoveGenerator
from .rules_engine import RulesEngine


def _status(game: dict) -> dict:
    """Game state plus, on a checkmate, who actually won. Computed once —
    working out the state means generating every legal move."""
    rules_engine = game["rules_engine"]
    state = rules_engine.get_game_state()
    current_turn = game["board"].current_turn

    return {
        "game_state": state,
        "current_turn": current_turn,
        # The mated side is the one to move, so the winner is the other one.
        "winner": ("black" if current_turn == "white" else "white")
                  if state == "checkmate" else None,
    }


def create_game(board: Board | None = None) -> dict:
    board = board if board is not None else Board()
    move_generator = MoveGenerator(board)
    return {
        "board": board,
        "move_generator": move_generator,
        "rules_engine": RulesEngine(move_generator, board),
    }


def get_valid_moves(game: dict, x, y) -> list:
    board = game["board"]
    move_generator = game["move_generator"]
    piece = board.get_piece(x, y)

    if not piece or piece.color != board.current_turn:
        return []

    return [{"x": mx, "y": my} for mx, my in move_generator.get_legal_moves(piece)]


def make_move(game: dict, fx: int, fy: int, tx: int, ty: int) -> dict:
    board = game["board"]
    rules_engine = game["rules_engine"]
    piece = board.get_piece(fx, fy)

    if not piece:
        return {"ok": False, "error": "Piece not found"}

    board.move_piece(piece, tx, ty)
    if any(k in piece.get_name() for k in ["pawn", "king", "rook"]):
        piece.first_move = False

    promotion_raw = board.get_pawn_promotion_data()
    return {
        "ok": True,
        "board": board.board_to_json(),
        "game_status": _status(game),
        "promotion": {
            "ok": bool(promotion_raw),
            "data": promotion_raw,
        },
    }


def promote_pawn(game: dict, x: int, y: int, piece_name: str) -> dict:
    game["board"].promote_pawn(x, y, piece_name)
    return {"ok": True}


def get_status(game: dict) -> dict:
    return _status(game)