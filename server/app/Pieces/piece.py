from abc import ABC, abstractmethod

class Piece(ABC):
    def __init__(self, x, y, color, image):
        self.x = x
        self.y = y
        self.color = color
        self.image = image

    @abstractmethod
    def get_moves(self, board) -> list[tuple[int, int]]:
        """Return list of (x, y) legal moves"""
        pass

    def get_image(self):
        return self.image

    def update_position(self, new_x, new_y):
        self.x = new_x
        self.y = new_y
    
    def get_name(self):
        return f"{self.color}_{self.__class__.__name__.lower()}"

