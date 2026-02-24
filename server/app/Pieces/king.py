from .piece import Piece

class King(Piece):
    def __init__(self, x, y, color, image):
        super().__init__(x, y, color, image)
        self.first_move = True

    def get_moves(self, board) -> list[tuple[int, int]]:
        moves = []
        directions = [
            (1, 0), (-1, 0), (0, 1), (0, -1),
            (1, 1), (1, -1), (-1, 1), (-1, -1)
        ]

        for dx, dy in directions:
            x, y = self.x + dx, self.y + dy
            if board.in_bounds(x, y):
                if board.is_empty(x, y) or board.is_enemy(x, y, self.color):
                    moves.append((x, y))

        return moves
