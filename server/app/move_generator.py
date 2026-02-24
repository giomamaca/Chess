from board import Board
from Pieces.piece import Piece

class MoveGenerator:
    def __init__(self, board: Board):
        self.board = board
    
    def get_legal_moves(self, piece):
        legal_moves = []

        for x, y in piece.get_moves(self.board):

            captured = self.board.grid[y][x]
            orig_x, orig_y = piece.x, piece.y

            # Make move
            self.board.move_piece(piece, x, y)

            king = self.board.get_king(piece.color)
            enemy_color = self.board.get_enemy_color(piece.color)

            if king and not self.board.is_square_attacked(
                king.x, king.y, enemy_color
            ):
                legal_moves.append((x, y))

            # Undo move properly
            self.board.move_piece(piece, orig_x, orig_y)
            self.board.grid[y][x] = captured

            if captured:
                self.board.pieces.append(captured)

        return legal_moves