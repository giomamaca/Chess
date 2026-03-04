import pytest
from app.board import Board
from app.pieces.piece import Piece

# -------------------------
# Basic Setup Tests
# -------------------------

def test_board_initial_setup():
    board = Board()

    # 32 total pieces
    assert len(board.pieces) == 32

    # Kings in correct positions
    white_king = board.get_king("white")
    black_king = board.get_king("black")

    assert white_king.x == 4
    assert white_king.y == 7

    assert black_king.x == 4
    assert black_king.y == 0


def test_reset():
    board = Board()
    board.move_piece(board.get_piece(0, 6), 0, 5)

    board.reset()

    assert len(board.pieces) == 32
    assert board.get_piece(0, 6) is not None
    assert board.get_piece(0, 5) is None


# -------------------------
# Bounds & Utility Tests
# -------------------------

def test_in_bounds():
    board = Board()

    assert board.in_bounds(0, 0)
    assert board.in_bounds(7, 7)
    assert not board.in_bounds(-1, 0)
    assert not board.in_bounds(8, 3)


def test_is_empty():
    board = Board()

    assert board.is_empty(4, 4)
    assert not board.is_empty(0, 6)


def test_is_enemy():
    board = Board()

    # black pawn at (0,1)
    assert board.is_enemy(0, 1, "white")

    # white pawn at (0,6)
    assert not board.is_enemy(0, 6, "white")


def test_get_enemy_color():
    board = Board()

    board.current_turn = "white"
    assert board.get_enemy_color() == "black"

    board.current_turn = "black"
    assert board.get_enemy_color() == "white"


# -------------------------
# Move Logic Tests
# -------------------------

def test_simple_move():
    board = Board()

    pawn = board.get_piece(0, 6)
    board.move_piece(pawn, 0, 5)

    assert board.get_piece(0, 5) == pawn
    assert board.get_piece(0, 6) is None
    assert pawn.x == 0
    assert pawn.y == 5


def test_capture_piece():
    board = Board()

    white_pawn = board.get_piece(0, 6)
    black_pawn = board.get_piece(1, 1)

    # Move black pawn forward manually
    board.move_piece(black_pawn, 1, 5)

    # White pawn captures
    board.move_piece(white_pawn, 1, 5)

    assert black_pawn not in board.pieces
    assert board.get_piece(1, 5) == white_pawn


# -------------------------
# Attack Detection
# -------------------------

def test_square_attacked_by_rook():
    board = Board()

    # Clear path for white rook
    board.grid[6][0] = None
    board.grid[5][0] = None

    rook = board.get_piece(0, 7)

    # Square directly above rook should be attacked
    assert board.is_square_attacked(0, 5, "white")


# -------------------------
# Castling Tests
# -------------------------

def test_white_kingside_castling():
    board = Board()

    # Clear pieces between king and rook
    board.grid[7][5] = None
    board.grid[7][6] = None

    king = board.get_piece(4, 7)
    rook = board.get_piece(7, 7)

    board.move_piece(king, 6, 7)

    assert king.x == 6
    assert king.y == 7

    assert rook.x == 5
    assert rook.y == 7


def test_white_queenside_castling():
    board = Board()

    # Clear pieces between king and rook
    board.grid[7][1] = None
    board.grid[7][2] = None
    board.grid[7][3] = None

    king = board.get_piece(4, 7)
    rook = board.get_piece(0, 7)

    board.move_piece(king, 2, 7)

    assert king.x == 2
    assert king.y == 7

    assert rook.x == 3
    assert rook.y == 7


# -------------------------
# JSON Export Test
# -------------------------

def test_board_to_json():
    board = Board()
    data = board.board_to_json()

    assert isinstance(data, list)
    assert len(data) == 32

    first_piece = data[0]
    assert "name" in first_piece
    assert "x" in first_piece
    assert "y" in first_piece
    assert "image" in first_piece