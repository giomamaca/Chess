from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .board import Board
from .move_generator import MoveGenerator
from .rules_engine import RulesEngine

from db.auth_service import AuthService
from db.database_classes.user_account import UserAccount


app = FastAPI()
chess_board = Board()
move_generator = MoveGenerator(chess_board)
rules_engine = RulesEngine(move_generator, chess_board)
auth = AuthService()

sockets = []

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
        return {"ok": True}

    return {"error": "Piece not found"}

@app.post("/valid-moves")
async def get_valid_moves(request: Request):
    data = await request.json()
    x = data.get("x")
    y = data.get("y")
    piece = chess_board.get_piece(x, y)
    print(chess_board.current_turn)
    if not piece or piece.color != chess_board.current_turn:
        return []

    print_grid()
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
def account_login(userAccount : UserAccount):
    user = auth.login(userAccount.username, userAccount.password)
    return user

@app.post("/account-register")
def account_register(userAccount : UserAccount):
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
    sockets.append(websocket)
    

    try:
        while True:
            pass

    except WebSocketDisconnect:
        pass
        

app.mount("/static", StaticFiles(directory="D:/Chess/client/build/static"), name="static")
app.mount("/pieces", StaticFiles(directory="D:/Chess/client/build/pieces"), name="pieces")

@app.get("/")
def serve_react():
    return FileResponse("D:/Chess/client/build/index.html")
