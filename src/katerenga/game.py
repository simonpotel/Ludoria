from src.board import Board
from src.render import Render


class Game:
    def __init__(self, game_save, quadrants):
        self.game_save = game_save
        self.board = Board(quadrants, 0)
        self.render = Render(game=self)

    def load_game(self):
        self.render.root.mainloop()
