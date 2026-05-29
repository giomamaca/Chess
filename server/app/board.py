from .pieces.pawn import Pawn
from .pieces.rook import Rook
from .pieces.knight import Knight
from .pieces.bishop import Bishop
from .pieces.queen import Queen
from .pieces.king import King
import random
import os

class Board:
    def __init__(self):
        self.reset()

    def reset(self):
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
        if "king" in piece.get_name() and piece.first_move:
            if new_x == 6:
                print("new_x  = 6")
                rook = self.get_piece(7, piece.y)
                if rook and "rook" in rook.get_name() and rook.first_move:
                    self.grid[piece.y][7] = None
                    rook.update_position(5, piece.y)
                    self.grid[piece.y][5] = rook
                    self.grid[piece.y][6] = piece
                    self.grid[piece.y][4] = None
                    piece.update_position(6, piece.y)
                    return
            if new_x == 2 and rook.first_move:
                print("new_x = 2")
                rook = self.get_piece(0, piece.y)
                if rook and "rook" in rook.get_name():
                    self.grid[piece.y][0] = None
                    rook.update_position(3, piece.y)
                    self.grid[piece.y][3] = rook
                    self.grid[piece.y][2] = piece
                    self.grid[piece.y][4] = None
                    piece.update_position(2, piece.y)
                    return

        if target is not None:
            if target in self.pieces:
                print(new_x, new_y)
                print(target.get_name())
                self.pieces.remove(target)

        self.grid[piece.y][piece.x] = None
        piece.update_position(new_x, new_y)
        self.grid[new_y][new_x] = piece
        self.current_turn = "black" if self.current_turn == "white" else "white"


    def get_pawn_promotion_data(self):
        if self.current_turn == "black":
            for i in range(8):
                piece = self.grid[0][i]
                if piece and piece.get_name() == "white_pawn":
                    return {
                        "x": piece.x,
                        "y": piece.y,
                        "offers": [
                            {"name": "queen",  "image": self.get_image_path("white", "queen")},
                            {"name": "rook",   "image": self.get_image_path("white", "rook")},
                            {"name": "bishop", "image": self.get_image_path("white", "bishop")},
                            {"name": "knight", "image": self.get_image_path("white", "knight")},
                        ]
                    }
        else:
            for i in range(8):
                piece = self.grid[7][i]
                if piece and piece.get_name() == "black_pawn":
                    return {
                        "x": piece.x,
                        "y": piece.y,
                        "offers": [
                            {"name": "queen",  "image": self.get_image_path("black", "queen")},
                            {"name": "rook",   "image": self.get_image_path("black", "rook")},
                            {"name": "bishop", "image": self.get_image_path("black", "bishop")},
                            {"name": "knight", "image": self.get_image_path("black", "knight")},
                        ]
                    }
        return None

    def promote_pawn(self, x, y, piece_name):
        piece = self.get_piece(x, y)
        if not piece:
            return
        
        color = piece.color
        image = self.get_image_path(color, piece_name)
        
        piece_map = {
            "queen":  Queen,
            "rook":   Rook,
            "bishop": Bishop,
            "knight": Knight,
        }
        
        cls = piece_map.get(piece_name)
        if not cls:
            return
        
        self.pieces.remove(piece)
        new_piece = cls(x, y, color, image)
        self.grid[y][x] = new_piece
        self.pieces.append(new_piece)



    def get_king(self, color):
        return next((p for p in self.pieces if p.get_name() == f"{color}_king"), None)
            
    def get_enemy_color(self):
        return "white" if self.current_turn == "black" else "black"

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
        return [
            {
                "name": piece.get_name(),
                "x": piece.x,
                "y": piece.y,
                "image": piece.get_image()
            }
            for piece in self.pieces
        ]
    
    @classmethod
    def board_from_json(cls, data):
        board = cls()

        board.grid = [[None for _ in range(8)] for _ in range(8)]
        board.pieces = []

        piece_map = {
            "pawn": Pawn,
            "rook": Rook,
            "knight": Knight,
            "bishop": Bishop,
            "queen": Queen,
            "king": King,
        }

        for item in data:
            full_name = item["name"]

            color, piece_name = full_name.split("_")

            piece_class = piece_map[piece_name]

            piece = piece_class(
                item["x"],
                item["y"],
                color,
                item["image"]
            )

            board.place_piece(piece)

        return board

    def is_square_attacked(self, x, y, by_color):
        for piece in self.pieces:
            if piece.color == by_color:
                if (x, y) in piece.get_moves(self):
                    return True
        return False