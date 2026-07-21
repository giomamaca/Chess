"""Check, checkmate and stalemate detection on real positions.

Regression cover for the bug where `is_square_attacked` was asked whether a
king was attacked by its OWN colour. That is never true, so `in_check` was
always False and every checkmate was reported as a stalemate — a win showed up
as a draw.
"""

import pytest

from app.board import Board
from app.move_generator import MoveGenerator
from app.pieces.king import King
from app.pieces.queen import Queen
from app.pieces.rook import Rook
from app.rules_engine import RulesEngine


def empty_board(turn="white"):
    board = Board()
    board.grid = [[None for _ in range(8)] for _ in range(8)]
    board.pieces = []
    board.current_turn = turn
    return board


def place(board, cls, x, y, color):
    piece = cls(x, y, color, board.get_image_path(color, cls.__name__.lower()))
    board.place_piece(piece)
    return piece


def engine_for(board):
    return RulesEngine(MoveGenerator(board), board)


# Coordinates are (x, y) with y=0 the black back rank, matching Board.setup.

def back_rank_mate():
    """White queen on a8 mates the black king on h8, rook on a1 guarding.

        a8 Q . . . . . . k h8
        a1 R . . . . . . .
    """
    board = empty_board(turn="black")
    place(board, King, 7, 0, "black")
    place(board, Queen, 6, 0, "white")   # adjacent, supported
    place(board, Rook, 6, 1, "white")    # guards the queen and the 7th rank
    place(board, King, 0, 7, "white")
    return board


def stalemate_position():
    """Black king on h8 has no legal move but is not attacked."""
    board = empty_board(turn="black")
    place(board, King, 7, 0, "black")
    place(board, Queen, 5, 1, "white")   # covers g8/g7/h7, not h8
    place(board, King, 0, 7, "white")
    return board


# ── The bug ───────────────────────────────────────────────────────

def test_checkmate_is_not_reported_as_stalemate():
    engine = engine_for(back_rank_mate())

    assert engine.get_game_state() == "checkmate"


def test_the_mated_king_is_seen_as_in_check():
    engine = engine_for(back_rank_mate())

    assert engine.is_in_check("black") is True


def test_a_king_is_never_in_check_from_its_own_pieces():
    """The exact confusion behind the bug: own pieces must not count."""
    board = back_rank_mate()
    engine = engine_for(board)

    king = board.get_king("black")
    assert board.is_square_attacked(king.x, king.y, "white") is True
    assert board.is_square_attacked(king.x, king.y, "black") is False


# ── Winner ────────────────────────────────────────────────────────

def test_winner_is_the_side_that_delivered_mate():
    engine = engine_for(back_rank_mate())

    assert engine.get_winner() == "white"


def test_winner_follows_the_mated_colour():
    """Same shape mirrored: white to move and mated, so black won."""
    board = empty_board(turn="white")
    place(board, King, 7, 7, "white")
    place(board, Queen, 6, 7, "black")
    place(board, Rook, 6, 6, "black")
    place(board, King, 0, 0, "black")

    assert engine_for(board).get_winner() == "black"


def test_no_winner_while_the_game_is_running():
    engine = engine_for(Board())

    assert engine.get_game_state() == "ongoing"
    assert engine.get_winner() is None


def test_a_stalemate_has_no_winner():
    engine = engine_for(stalemate_position())

    assert engine.get_game_state() == "stalemate"
    assert engine.get_winner() is None


# ── Stalemate still works ─────────────────────────────────────────

def test_stalemate_is_not_reported_as_checkmate():
    engine = engine_for(stalemate_position())

    assert engine.get_game_state() == "stalemate"


def test_the_stalemated_king_is_not_in_check():
    engine = engine_for(stalemate_position())

    assert engine.is_in_check("black") is False


# ── Check without mate ────────────────────────────────────────────

def test_a_king_in_check_that_can_escape_is_still_ongoing():
    board = empty_board(turn="black")
    place(board, King, 4, 0, "black")
    place(board, Rook, 4, 4, "white")    # checks down the file
    place(board, King, 0, 7, "white")
    engine = engine_for(board)

    assert engine.is_in_check("black") is True
    assert engine.get_game_state() == "ongoing"
    assert engine.get_winner() is None


def test_an_unattacked_king_is_not_in_check():
    engine = engine_for(Board())

    assert engine.is_in_check("white") is False
    assert engine.is_in_check("black") is False


# ── has_legal_moves ───────────────────────────────────────────────

def test_both_sides_start_with_legal_moves():
    engine = engine_for(Board())

    assert engine.has_legal_moves("white") is True
    assert engine.has_legal_moves("black") is True


def test_a_mated_side_has_no_legal_moves():
    engine = engine_for(back_rank_mate())

    assert engine.has_legal_moves("black") is False
