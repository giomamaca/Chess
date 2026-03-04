from .pieces.piece import Piece
from .board import Board
from .move_generator import MoveGenerator

class RulesEngine:
    def __init__(self, move_generator : MoveGenerator, board: Board):
        self.board = board
        self.move_gen = move_generator

    def get_game_state(self):
        color = self.board.current_turn
        pieces = [p for p in self.board.pieces if p.color == color]
        has_moves = any(self.move_gen.get_legal_moves(p) for p in pieces)

        if has_moves:
            return "ongoing"

        king = self.board.get_king(color)
        in_check = self.board.is_square_attacked(king.x, king.y,(color))

        return "checkmate" if in_check else "stalemate"
