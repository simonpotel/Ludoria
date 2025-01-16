from src.board import Board
from src.render import Render
from src.captures import is_threatened, has_valid_move
from tkinter import messagebox
from src.saves import save_game

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

        if cell[0] is not None:
            self.render.edit_info_label("This cell is already occupied")
            return True

        if is_threatened(self.board.board, row, col, self.round_turn):
            self.render.edit_info_label(
                "This cell is threatened by an enemy tower")
            return True

        self.board.board[row][col][0] = self.round_turn
        self.round_turn = 1 - self.round_turn
        save_game(self)

        if not has_valid_move(self.board.board, self.round_turn):
            winner = "Player 2" if self.round_turn == 0 else "Player 1"
            self.render.edit_info_label(
                f"Game ended ! {winner} wins !")
            self.render.root.update_idletasks()
            messagebox.showinfo("End Game", f"{winner} wins !")
            self.render.root.destroy()
            return False

        self.render.edit_info_label(
            f"Player {self.round_turn + 1} turn - Place your tower."
        )

        return True

    def load_game(self):
        self.render.root.mainloop()
