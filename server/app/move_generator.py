from .board import Board
from .pieces.piece import Piece

class MoveGenerator:
    def __init__(self, board: Board):
        self.board = board
    
    def get_legal_moves(self, piece):
        legal_moves = []

        candidate_moves = piece.get_moves(self.board)
        print("candidate_moves", candidate_moves)
        if "king" in piece.get_name():
            print("casting_moves",self.get_casting_moves(piece))
            candidate_moves += self.get_casting_moves(piece)

        for x, y in candidate_moves:
            copied_grid = self.board.grid.copy()
            captured = self.board.grid[y][x]
            orig_x, orig_y = piece.x, piece.y

            # Make move
            self.board.move_piece(piece, x, y)

            king = self.board.get_king(piece.color)
            enemy_color = self.board.get_enemy_color()

            if king and not self.board.is_square_attacked(
                king.x, king.y, enemy_color
            ):
                legal_moves.append((x, y))

            # Undo move properly
            self.board.move_piece(piece, orig_x, orig_y)
            self.board.grid[y][x] = captured

            if captured:
                self.board.pieces.append(captured)
            self.board.grid = copied_grid

        return legal_moves
    

    def get_casting_moves(self, king):
        moves = []

        if not king.first_move:
            return moves

        enemy = self.board.get_enemy_color()

        if self.board.is_square_attacked(king.x, king.y, enemy):
            return moves

        y = king.y

        rook = self.board.get_piece(7, y)
        if rook and "rook" in rook.get_name() and rook.first_move:
            if self.board.is_empty(5, y) and self.board.is_empty(6, y):
                if not self.board.is_square_attacked(5, y, enemy) and \
                not self.board.is_square_attacked(6, y, enemy):
                    moves.append((6, y))

        rook = self.board.get_piece(0, y)
        if rook and "rook" in rook.get_name() and rook.first_move:
            if self.board.is_empty(1, y) and \
            self.board.is_empty(2, y) and \
            self.board.is_empty(3, y):
                if not self.board.is_square_attacked(3, y, enemy) and \
                not self.board.is_square_attacked(2, y, enemy):
                    moves.append((2, y))

        return moves