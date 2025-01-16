from src.board import Board
from src.render import Render
from src.captures import is_threatened, has_valid_move


class Game:
    def __init__(self, game_save, quadrants):
        self.game_save = game_save
        self.round_turn = 0  # 0 pour le joueur 1, 1 pour le joueur 2
        self.board = Board(quadrants, 1)
        self.render = Render(game=self)

    def on_click(self, row, col):
        """
        procédure appelée lorsqu'une cellule est cliquée dans le jeu Isolation
        """
        cell = self.board.board[row][col]

        if not has_valid_move(self.board.board, self.round_turn):
            winner = "Joueur 2" if self.round_turn == 0 else "Joueur 1"
            self.render.edit_info_label(
                f"Partie terminée ! {winner} a gagné !")

        if cell[0] is not None:
            self.render.edit_info_label("Cette case est déjà occupée")
            return

        if is_threatened(self.board.board, row, col, self.round_turn):
            self.render.edit_info_label(
                "Cette case est menacée par un pion adverse")
            return

        self.board.board[row][col][0] = self.round_turn
        self.round_turn = 1 - self.round_turn
        self.render.edit_info_label(
            f"Tour du Joueur {self.round_turn + 1} - Placez votre pion."
        )

    def load_game(self):
        self.render.root.mainloop()
