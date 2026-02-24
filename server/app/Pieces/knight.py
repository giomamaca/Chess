from .piece import Piece

class Knight(Piece):
    def __init__(self, x, y, color, image):
        super().__init__(x, y, color, image)

    def get_moves(self, board) -> list[tuple[int, int]]:
        moves = []

        offsets = [
            (1, 2), (2, 1), (2, -1), (1, -2),
            (-1, -2), (-2, -1), (-2, 1), (-1, 2)
        ]

        for dx, dy in offsets:
            x, y = self.x + dx, self.y + dy
            if board.in_bounds(x, y):
                if board.is_empty(x, y) or board.is_enemy(x, y, self.color):
                    moves.append((x, y))

        return moves
