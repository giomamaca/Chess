import pytest
from app.board import Board
from app.move_generator import MoveGenerator

@pytest.fixture
def board():
    b = Board()
    b.reset()
    return b

def test_legal_moves_pawn_opening(board):
    """Pawn should have 2 moves from starting position"""
    pawn = board.get_piece(0, 6)
    mg = MoveGenerator(board)
    moves = mg.get_legal_moves(pawn)
    assert len(moves) == 2
    assert (0, 5) in moves
    assert (0, 4) in moves

def test_legal_moves_blocked_pawn(board):
    """Pawn blocked by own piece should have no moves"""
    pawn = board.get_piece(0, 6)
    board.move_piece(board.get_piece(1, 7), 0, 5)
    mg = MoveGenerator(board)
    moves = mg.get_legal_moves(pawn)
    assert (0, 5) not in moves
    assert (0, 4) not in moves

def test_pinned_piece_has_restricted_moves(board):
    """A piece pinned to the king should not be able to move freely"""
    from app.pieces.king import King
    from app.pieces.rook import Rook

    board.grid = [[None]*8 for _ in range(8)]
    board.pieces = []

    white_king = King(4, 7, "white", None)
    white_rook = Rook(4, 5, "white", None)
    black_rook = Rook(4, 0, "black", None)

    board.grid[7][4] = white_king
    board.grid[5][4] = white_rook
    board.grid[0][4] = black_rook
    board.pieces = [white_king, white_rook, black_rook]

    mg = MoveGenerator(board)
    moves = mg.get_legal_moves(white_rook)

    for x, y in moves:
        assert x == 4

def test_king_cannot_move_into_check(board):
    """King should not be able to move to an attacked square"""
    from app.pieces.king import King
    from app.pieces.rook import Rook

    board.grid = [[None]*8 for _ in range(8)]
    board.pieces = []

    white_king = King(4, 7, "white", None)
    black_rook = Rook(0, 6, "black", None)

    board.grid[7][4] = white_king
    board.grid[6][0] = black_rook
    board.pieces = [white_king, black_rook]

    mg = MoveGenerator(board)
    moves = mg.get_legal_moves(white_king)

    for x, y in moves:
        assert y != 6

def test_kingside_castling_available(board):
    """King should be able to castle kingside when path is clear"""
    from app.pieces.king import King
    from app.pieces.rook import Rook

    board.grid = [[None]*8 for _ in range(8)]
    board.pieces = []

    white_king = King(4, 7, "white", None)
    white_rook = Rook(7, 7, "white", None)

    board.grid[7][4] = white_king
    board.grid[7][7] = white_rook
    board.pieces = [white_king, white_rook]

    mg = MoveGenerator(board)
    moves = mg.get_casting_moves(white_king)
    assert (6, 7) in moves

def test_queenside_castling_available(board):
    """King should be able to castle queenside when path is clear"""
    from app.pieces.king import King
    from app.pieces.rook import Rook

    board.grid = [[None]*8 for _ in range(8)]
    board.pieces = []

    white_king = King(4, 7, "white", None)
    white_rook = Rook(0, 7, "white", None)

    board.grid[7][4] = white_king
    board.grid[7][0] = white_rook
    board.pieces = [white_king, white_rook]

    mg = MoveGenerator(board)
    moves = mg.get_casting_moves(white_king)
    assert (2, 7) in moves

def test_castling_blocked_by_piece(board):
    """Castling should not be available if pieces are in the way"""
    white_king = board.get_piece(4, 7)
    mg = MoveGenerator(board)
    moves = mg.get_casting_moves(white_king)
    assert (6, 7) not in moves
    assert (2, 7) not in moves

def test_castling_not_available_after_king_moved(board):
    """Castling should not be available if king has already moved"""
    from app.pieces.king import King
    from app.pieces.rook import Rook

    board.grid = [[None]*8 for _ in range(8)]
    board.pieces = []

    white_king = King(4, 7, "white", None)
    white_king.first_move = False
    white_rook = Rook(7, 7, "white", None)

    board.grid[7][4] = white_king
    board.grid[7][7] = white_rook
    board.pieces = [white_king, white_rook]

    mg = MoveGenerator(board)
    moves = mg.get_casting_moves(white_king)
    assert (6, 7) not in moves

def test_castling_not_available_in_check(board):
    """Castling should not be available when king is in check"""
    from app.pieces.king import King
    from app.pieces.rook import Rook

    board.grid = [[None]*8 for _ in range(8)]
    board.pieces = []

    white_king = King(4, 7, "white", None)
    white_rook = Rook(7, 7, "white", None)
    black_rook = Rook(4, 0, "black", None)

    board.grid[7][4] = white_king
    board.grid[7][7] = white_rook
    board.grid[0][4] = black_rook
    board.pieces = [white_king, white_rook, black_rook]

    mg = MoveGenerator(board)
    moves = mg.get_casting_moves(white_king)
    assert (6, 7) not in moves

def test_no_legal_moves_in_checkmate(board):
    """King in checkmate should have no legal moves"""
    from app.pieces.king import King
    from app.pieces.rook import Rook
    from app.pieces.queen import Queen

    board.grid = [[None]*8 for _ in range(8)]
    board.pieces = []

    white_king = King(0, 7, "white", None)
    black_rook = Rook(7, 7, "black", None)
    black_queen = Queen(1, 5, "black", None)

    board.grid[7][0] = white_king
    board.grid[7][7] = black_rook
    board.grid[5][1] = black_queen
    board.pieces = [white_king, black_rook, black_queen]

    mg = MoveGenerator(board)
    moves = mg.get_legal_moves(white_king)
    assert moves == []