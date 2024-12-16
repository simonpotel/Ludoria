from src.board import Board
from src.render import Render


class Game:
    def __init__(self, game_save, quadrants):
        self.game_save = game_save
        # self.load_game()
        # game numbers: 0 = katerenga, 1 = ...
        game_number = 0
        self.board = Board(quadrants, game_number)
        self.render = Render(game=self)


    def load_game(self):
        self.render.root.mainloop()
