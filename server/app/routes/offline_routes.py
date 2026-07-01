import uuid
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from .. import game_service

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
    offline_games[session_id] = game_service.create_game()
    return {"session_id": session_id}

@router.post("/reset/{session_id}")
def reset(session_id: str):
    get_game(session_id)["board"].reset()
    return {"ok": True}

@router.get("/status/{session_id}")
def get_status(session_id: str):
    return game_service.get_status(get_game(session_id))

@router.post("/move/{session_id}")
async def move(session_id: str, request: Request):
    game = get_game(session_id)
    data = await request.json()
    fx, fy = data["from"]
    tx, ty = data["to"]
    return game_service.make_move(game, fx, fy, tx, ty)

@router.post("/valid-moves/{session_id}")
async def get_valid_moves(session_id: str, request: Request):
    game = get_game(session_id)
    data = await request.json()
    return game_service.get_valid_moves(game, data.get("x"), data.get("y"))

@router.get("/pawn-reached/{session_id}")
def pawn_reached(session_id: str):
    data = get_game(session_id)["board"].get_pawn_promotion_data()
    return {"ok": bool(data), "data": data}

@router.post("/promote/{session_id}")
async def promote(session_id: str, request: Request):
    game = get_game(session_id)
    data = await request.json()
    return game_service.promote_pawn(game, data["x"], data["y"], data["piece"])

@router.get("/board/{session_id}")
def get_board(session_id: str):
    return JSONResponse(get_game(session_id)["board"].board_to_json())

@router.delete("/end/{session_id}")
def end_game(session_id: str):
    offline_games.pop(session_id, None)
    return {"ok": True}