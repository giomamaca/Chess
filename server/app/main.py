from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from board import Board
from Pieces.piece import Piece

app = FastAPI()

# Allow requests from React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

chess_board = Board()


@app.post("/move")
async def move(request: Request):
    data = await request.json()
    name = data["name"]
    fx, fy = data["from"]
    tx, ty = data["to"]

    print(data)

    p = chess_board.get_piece(fx, fy)
    if p:
        chess_board.move_piece(p, tx, ty)
        if "pawn" in p.get_name() :
            p.first_move = False
        chess_board.current_turn = "black" if chess_board.current_turn == "white" else "white"
        print_grid()
        return {"ok": True}
    return {"error": "Piece not found"}

@app.post("/valid-moves")
async def get_valid_moves(request: Request):
    data = await request.json()
    x = data.get("x")
    y = data.get("y")

    piece = chess_board.get_piece(x, y)

    if not piece or piece.color != chess_board.current_turn:
        return []

    legal_moves = chess_board.get_legal_moves(piece)
    print("Moves:", legal_moves)

    return [{"x": mx, "y": my} for mx, my in legal_moves]


@app.get("/board")
def get_board():
    return JSONResponse(chess_board.board_to_json())


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
