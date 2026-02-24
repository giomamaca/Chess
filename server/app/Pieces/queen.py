from .piece import Piece

class Queen(Piece):
    def __init__(self, x, y, color, image):
        super().__init__(x, y, color, image)

    def get_moves(self, board) -> list[tuple[int, int]]:
        moves = []

        directions = [
            (1, 0), (-1, 0), (0, 1), (0, -1),
            (1, 1), (1, -1), (-1, 1), (-1, -1)
        ]

        for dx_dir, dy_dir in directions:
            dx, dy = self.x + dx_dir, self.y + dy_dir

            while board.in_bounds(dx, dy):
                if board.is_empty(dx, dy):
                    moves.append((dx, dy))
                elif board.is_enemy(dx, dy, self.color):
                    moves.append((dx, dy))
                    break
                else:
                    break

                dx += dx_dir
                dy += dy_dir

        return moves
