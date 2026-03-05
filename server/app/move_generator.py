import copy
from .board import Board
from .pieces.piece import Piece

class MoveGenerator:
    def __init__(self, board: Board):
        self.board = board
    
    def get_legal_moves(self, piece):
        legal_moves = []
        candidate_moves = piece.get_moves(self.board)

        # Add castling moves for king
        if "king" in piece.get_name():
            candidate_moves += self.get_casting_moves(piece)

        def print_grid(grd):
            for i in range(8):
                for j in range(8):
                    p = grd[i][j]
                    if p is None:
                        print(" . ", end=" ")
                    else:
                        name = p.get_name()
                        parts = name.split("_")
                        short_name = parts[0][0] + parts[1][:2]
                        print(short_name, end=" ")
                print()
            print()

        for x, y in candidate_moves:
            # Save original state
            original_pos = (piece.x, piece.y)
            captured_piece = self.board.grid[y][x]  # save if a piece exists at target
            if captured_piece:
                self.board.pieces.remove(captured_piece)

            # Make the move temporarily
            self.board.grid[piece.y][piece.x] = None
            self.board.grid[y][x] = piece
            piece.x, piece.y = x, y

            king = self.board.get_king(piece.color)
            enemy_color = self.board.get_enemy_color()

            if king and not self.board.is_square_attacked(king.x, king.y, enemy_color):
                legal_moves.append((x, y))
            # Undo move
            self.board.grid[original_pos[1]][original_pos[0]] = piece
            self.board.grid[y][x] = captured_piece
            piece.x, piece.y = original_pos
            if captured_piece:
                self.board.pieces.append(captured_piece)

        return legal_moves

    def get_casting_moves(self, king):
        moves = []

        if not king.first_move:
            return moves

        enemy = self.board.get_enemy_color()

        if self.board.is_square_attacked(king.x, king.y, enemy):
            return moves

        y = king.y

        # Kingside castling
        rook = self.board.get_piece(7, y)
        if rook and "rook" in rook.get_name() and rook.first_move:
            if self.board.is_empty(5, y) and self.board.is_empty(6, y):
                if not self.board.is_square_attacked(5, y, enemy) and \
                   not self.board.is_square_attacked(6, y, enemy):
                    moves.append((6, y))

        # Queenside castling
        rook = self.board.get_piece(0, y)
        if rook and "rook" in rook.get_name() and rook.first_move:
            if self.board.is_empty(1, y) and \
               self.board.is_empty(2, y) and \
               self.board.is_empty(3, y):
                if not self.board.is_square_attacked(3, y, enemy) and \
                   not self.board.is_square_attacked(2, y, enemy):
                    moves.append((2, y))

        return moves