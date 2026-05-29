import os
import json
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .board import Board
from .move_generator import MoveGenerator
from .rules_engine import RulesEngine

from db.auth_service import AuthService
from db.database_classes.user_account import UserAccount
from db.game_repository import GameRepository
from db.user_repositories import UserRepository

app = FastAPI()
chess_board = Board()
move_generator = MoveGenerator(chess_board)
rules_engine = RulesEngine(move_generator, chess_board)
auth = AuthService()
game_repo = GameRepository()
user_repo = UserRepository()

# username -> WebSocket
connected_users: dict[str, WebSocket] = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/game-reset")
def reset():
    chess_board.reset()
    return {"ok": True}

@app.get("/game-status")
def get_status():
    return {
        "game_state": rules_engine.get_game_state(),
        "current_turn": chess_board.current_turn
    }

@app.post("/move")
async def move(request: Request):
    data = await request.json()
    fx, fy = data["from"]
    tx, ty = data["to"]
    piece = chess_board.get_piece(fx, fy)

    if piece:
        chess_board.move_piece(piece, tx, ty)

        if any(k in piece.get_name() for k in ["pawn", "king", "rook"]):
            piece.first_move = False

        print_grid()

        promotion_raw = chess_board.get_pawn_promotion_data()
        return {
            "ok": True,
            "board": chess_board.board_to_json(),
            "game_status": {
                "game_state": rules_engine.get_game_state(),
                "current_turn": chess_board.current_turn,
            },
            "promotion": {
                "ok": bool(promotion_raw),
                "data": promotion_raw,
            },
        }

    return {"error": "Piece not found"}

@app.post("/valid-moves")
async def get_valid_moves(request: Request):
    data = await request.json()
    x = data.get("x")
    y = data.get("y")
    piece = chess_board.get_piece(x, y)

    if not piece or piece.color != chess_board.current_turn:
        return []

    legal_moves = move_generator.get_legal_moves(piece)
    return [{"x": mx, "y": my} for mx, my in legal_moves]

@app.get("/pawn-reached")
def pawn_reached():
    data = chess_board.get_pawn_promotion_data()
    if not data:
        return {"ok": False}
    return {"ok": True, "data": data}

@app.post("/promote")
async def promote(request: Request):
    data = await request.json()
    x = data["x"]
    y = data["y"]
    piece_name = data["piece"]
    chess_board.promote_pawn(x, y, piece_name)
    return {"ok": True}

@app.get("/board")
def get_board():
    return JSONResponse(chess_board.board_to_json())

@app.post("/account-login")
def account_login(userAccount: UserAccount):
    user = auth.login(userAccount.username, userAccount.password)
    return user

@app.post("/account-register")
def account_register(userAccount: UserAccount):
    return auth.register(userAccount.username, userAccount.password)

def print_grid():
    grd = chess_board.grid
    for i in range(8):
        for j in range(8):
            piece = grd[i][j]
            if piece is None:
                print(" . ", end=" ")
            else:
                name = piece.get_name()
                parts = name.split("_")
                short_name = parts[0][0] + parts[1][:2]
                print(short_name, end=" ")
        print()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    username = None

    try:
        # First message is always the username
        username = await websocket.receive_text()
        print("username : ", username)
        connected_users[username] = websocket
        print(f"[WS] {username} connected")

        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)
            msg_type = data.get("type")

            if msg_type == "create_private_room":
                user = user_repo.get_user_by_username(username)
                if not user:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "User not found"
                    }))
                    continue

                user_id = user[0]
                room_code = game_repo.create_private_room(user_id)
                await websocket.send_text(json.dumps({
                    "type": "room_created",
                    "room_code": room_code
                }))

            elif msg_type == "join_private_room":
                code = data.get("room_code", "").strip().upper()
                user = user_repo.get_user_by_username(username)
                if not user:
                    await websocket.send_text(json.dumps({"type": "error", "message": "User not found"}))
                    continue

                user_id = user[0]
                result = game_repo.join_private_room(code, user_id)

                if not result:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "Room not found or already full"
                    }))
                    continue

                game_id, host_id, joining_color, host_color = result
                host = user_repo.get_user_by_id(host_id)

                await websocket.send_text(json.dumps({
                    "type": "game_start",
                    "game_id": game_id,
                    "code": code,
                    "color": joining_color
                }))

                if host and host[1] in connected_users:
                    await connected_users[host[1]].send_text(json.dumps({
                        "type": "game_start",
                        "game_id": game_id,
                        "code": code,
                        "color": host_color
                    }))

            elif msg_type == "quick_match":
                user = user_repo.get_user_by_username(username)
                if not user:
                    await websocket.send_text(json.dumps({"type": "error", "message": "User not found"}))
                    continue

                user_id = user[0]
                free_game = game_repo.get_free_lobby(user_id)
                if(free_game):
                    print("ipova")
                    
                if free_game:
                    game_id, white_id, black_id, code = free_game
                    game_repo.join_lobby(game_id, user_id)

                    host_id = white_id if white_id is not None else black_id
                    joining_color = "white" if white_id is None else "black"
                    host_color = "black" if joining_color == "white" else "white"

                    host_user = user_repo.get_user_by_id(host_id)

                    await websocket.send_text(json.dumps({
                        "type": "game_start",
                        "game_id": game_id,
                        "code": code,
                        "color": joining_color
                    }))

                    if host_user and host_user[1] in connected_users:
                        await connected_users[host_user[1]].send_text(json.dumps({
                            "type": "game_start",
                            "game_id": game_id,
                            "code": code,
                            "color": host_color
                        }))
                    
                else:
                    game_id, code = game_repo.create_open_game(user_id)
                    await websocket.send_text(json.dumps({
                        "type": "searching",
                        "game_id": game_id,
                        "code": code
                    }))
                    print("serching.......")

    except WebSocketDisconnect:
        if username and username in connected_users:
            del connected_users[username]
            print(f"[WS] {username} disconnected")


BUILD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "client", "build")

app.mount("/static", StaticFiles(directory=os.path.join(BUILD_DIR, "static")), name="static")
app.mount("/pieces", StaticFiles(directory=os.path.join(BUILD_DIR, "pieces")), name="pieces")

@app.get("/")
def serve_react():
    return FileResponse(os.path.join(BUILD_DIR, "index.html"))