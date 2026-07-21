from .pieces.piece import Piece
from .board import Board
from .move_generator import MoveGenerator


def enemy_of(color: str) -> str:
    return "black" if color == "white" else "white"


class RulesEngine:
    def __init__(self, move_generator : MoveGenerator, board: Board):
        self.board = board
        self.move_gen = move_generator

    def is_in_check(self, color: str) -> bool:
        """Is `color`'s king attacked right now?"""
        king = self.board.get_king(color)
        if not king:
            return False
        return self.board.is_square_attacked(king.x, king.y, enemy_of(color))

    def has_legal_moves(self, color: str) -> bool:
        return any(
            self.move_gen.get_legal_moves(p)
            for p in self.board.pieces
            if p.color == color
        )

    def get_game_state(self):
        color = self.board.current_turn

        if self.has_legal_moves(color):
            return "ongoing"

        return "checkmate" if self.is_in_check(color) else "stalemate"

    def get_winner(self):
        """The colour that won, or None for an ongoing game or a draw."""
        if self.get_game_state() != "checkmate":
            return None
        return enemy_of(self.board.current_turn)
