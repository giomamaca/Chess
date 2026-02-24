from Pieces.pawn import Pawn
from Pieces.rook import Rook
from Pieces.knight import Knight
from Pieces.bishop import Bishop
from Pieces.queen import Queen
from Pieces.king import King
from Pieces.piece import Piece
import os

class Board:
    def __init__(self):
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        self.pieces = []
        self.setup_start_board()
        self.current_turn = "white"

    def in_bounds(self, x, y):
        return 0 <= x < 8 and 0 <= y < 8

    def is_empty(self, x, y):
        return self.grid[y][x] is None

    def is_enemy(self, x, y, color):
        piece = self.grid[y][x]
        return piece is not None and piece.color != color

    def place_piece(self, piece):
        self.grid[piece.y][piece.x] = piece
        self.pieces.append(piece)

    def move_piece(self, piece, new_x, new_y):
        target = self.grid[new_y][new_x]

        if target is not None:
            if target in self.pieces:
                self.pieces.remove(target)

        self.grid[piece.y][piece.x] = None

        piece.update_position(new_x, new_y)
        self.grid[new_y][new_x] = piece

    def get_king(self, color):
        return next((p for p in self.pieces if p.get_name() == f"{color}_king"), None)
            
    def get_enemy_color(self):
        return "white" if self.current_turn is "black" else "black"

    def get_legal_moves(self, piece):
        legal_moves = []

        for x, y in piece.get_moves(self): 
            captured = self.grid[y][x]
            orig_x, orig_y = piece.x, piece.y

            self.move_piece(piece, x, y)

            king = self.get_king(piece.color)
            if king and not self.is_square_attacked(king.x, king.y, self.get_enemy_color()):
                legal_moves.append((x, y))

            self.move_piece(piece, orig_x, orig_y)
            self.grid[y][x] = captured
            if captured and captured not in self.pieces:
                self.pieces.append(captured)

        return legal_moves

    # helper function to get image path
    def get_image_path(self, color, piece_name):
        folder = "light" if color == "white" else "dark"
        return f"pieces/{folder}/{piece_name}.png"
        
    def get_piece(self, x, y):
        return self.grid[y][x]

    def setup_start_board(self):
        # Pawns
        for x in range(8):
            self.place_piece(Pawn(x, 6, "white", self.get_image_path("white", "pawn")))
            self.place_piece(Pawn(x, 1, "black", self.get_image_path("black", "pawn")))

        # Rooks
        self.place_piece(Rook(0, 7, "white", self.get_image_path("white", "rook")))
        self.place_piece(Rook(7, 7, "white", self.get_image_path("white", "rook")))
        self.place_piece(Rook(0, 0, "black", self.get_image_path("black", "rook")))
        self.place_piece(Rook(7, 0, "black", self.get_image_path("black", "rook")))

        # Knights
        self.place_piece(Knight(1, 7, "white", self.get_image_path("white", "knight")))
        self.place_piece(Knight(6, 7, "white", self.get_image_path("white", "knight")))
        self.place_piece(Knight(1, 0, "black", self.get_image_path("black", "knight")))
        self.place_piece(Knight(6, 0, "black", self.get_image_path("black", "knight")))

        # Bishops
        self.place_piece(Bishop(2, 7, "white", self.get_image_path("white", "bishop")))
        self.place_piece(Bishop(5, 7, "white", self.get_image_path("white", "bishop")))
        self.place_piece(Bishop(2, 0, "black", self.get_image_path("black", "bishop")))
        self.place_piece(Bishop(5, 0, "black", self.get_image_path("black", "bishop")))

        # Queens
        self.place_piece(Queen(3, 7, "white", self.get_image_path("white", "queen")))
        self.place_piece(Queen(3, 0, "black", self.get_image_path("black", "queen")))

        # Kings
        self.place_piece(King(4, 7, "white", self.get_image_path("white", "king")))
        self.place_piece(King(4, 0, "black", self.get_image_path("black", "king")))

    def board_to_json(self):
        """
        Export all pieces to a JSON-serializable list
        Each piece includes: name, x, y, image
        Example output:
        [
            {"name": "white_pawn", "x":0, "y":6, "image":"pieces/light/light_pawn_v2.png"},
            {"name": "black_king", "x":4, "y":0, "image":"pieces/dark/dark_king_v2.png"},
            ...
        ]
        """
        return [
            {
                "name": piece.get_name(),
                "x": piece.x,
                "y": piece.y,
                "image": piece.get_image()
            }
            for piece in self.pieces
        ]
    
    def is_square_attacked(self, x, y, by_color):
        for piece in self.pieces:
            if piece.color == by_color:
                if (x, y) in piece.get_moves(self):
                    return True
        return False