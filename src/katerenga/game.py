from src.board import Board
from src.render import Render


class Game:
    def __init__(self, game_save, quadrants):
        self.game_save = game_save
        self.board = Board(quadrants, 0)
        self.render = Render(game=self)

    def load_game(self):
        self.render.root.mainloop()

    def on_click(self, row, col):
        """
        procédure appelée lorsqu'une cellule est cliquée dans le jeu Katarenga
        """
        cell = self.board.board[row][col]
        print(f"Katarenga: Clicked on cell at row {row}, col {col}")
        print(f"Cell content: {cell}")
