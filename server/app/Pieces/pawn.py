from shutil import move
from .piece import Piece

class Pawn(Piece):
    first_move : bool
    def __init__(self, x, y, color, image):
        super().__init__(x, y, color, image)
        self.first_move = True
        
    def get_moves(self, board) -> list[tuple[int, int]]:
        moves = []

        direction = -1 if self.color == "white" else 1

        one_step = (self.x, self.y + direction)
        if board.in_bounds(*one_step) and board.is_empty(*one_step):
            moves.append(one_step)

            if self.first_move:
                two_step = (self.x, self.y + 2 * direction)
                if board.is_empty(*two_step):
                    moves.append(two_step)

        for dx in (-1, 1):
            x, y = self.x + dx, self.y + direction
            if board.in_bounds(x, y) and board.is_enemy(x, y, self.color):
                moves.append((x, y))

        return moves