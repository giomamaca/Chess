import uuid
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from ..board import Board
from ..move_generator import MoveGenerator
from ..rules_engine import RulesEngine

router = APIRouter(prefix="/offline", tags=["offline"])

offline_games: dict = {}

def get_game(session_id: str):
    game = offline_games.get(session_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game

@router.post("/create")
def create():
    session_id = str(uuid.uuid4())
    board = Board()
    offline_games[session_id] = {
        "board": board,
        "move_generator": MoveGenerator(board),
        "rules_engine": RulesEngine(MoveGenerator(board), board)
    }
    return {"session_id": session_id}

@router.post("/reset/{session_id}")
def reset(session_id: str):
    game = get_game(session_id)
    game["board"].reset()
    return {"ok": True}

@router.get("/status/{session_id}")
def get_status(session_id: str):
    game = get_game(session_id)
    return {
        "game_state": game["rules_engine"].get_game_state(),
        "current_turn": game["board"].current_turn
    }

@router.post("/move/{session_id}")
async def move(session_id: str, request: Request):
    game = get_game(session_id)
    board = game["board"]
    rules_engine = game["rules_engine"]

    data = await request.json()
    fx, fy = data["from"]
    tx, ty = data["to"]
    piece = board.get_piece(fx, fy)

    if not piece:
        return {"error": "Piece not found"}

    board.move_piece(piece, tx, ty)
    if any(k in piece.get_name() for k in ["pawn", "king", "rook"]):
        piece.first_move = False

    promotion_raw = board.get_pawn_promotion_data()
    return {
        "ok": True,
        "board": board.board_to_json(),
        "game_status": {
            "game_state": rules_engine.get_game_state(),
            "current_turn": board.current_turn,
        },
        "promotion": {
            "ok": bool(promotion_raw),
            "data": promotion_raw,
        },
    }

@router.post("/valid-moves/{session_id}")
async def get_valid_moves(session_id: str, request: Request):
    game = get_game(session_id)
    board = game["board"]
    move_generator = game["move_generator"]

    data = await request.json()
    x, y = data.get("x"), data.get("y")
    piece = board.get_piece(x, y)

    if not piece or piece.color != board.current_turn:
        return []

    return [{"x": mx, "y": my} for mx, my in move_generator.get_legal_moves(piece)]

@router.get("/pawn-reached/{session_id}")
def pawn_reached(session_id: str):
    game = get_game(session_id)
    data = game["board"].get_pawn_promotion_data()
    return {"ok": bool(data), "data": data}

@router.post("/promote/{session_id}")
async def promote(session_id: str, request: Request):
    game = get_game(session_id)
    data = await request.json()
    game["board"].promote_pawn(data["x"], data["y"], data["piece"])
    return {"ok": True}

@router.get("/board/{session_id}")
def get_board(session_id: str):
    game = get_game(session_id)
    return JSONResponse(game["board"].board_to_json())

@router.delete("/end/{session_id}")
def end_game(session_id: str):
    offline_games.pop(session_id, None)
    return {"ok": True}