from src.board import Board
from src.render import Render
from src.captures import is_threatened, has_valid_move
from tkinter import messagebox
from src.saves import save_game

class Game:
    def __init__(self, game_save, quadrants):
        """
        constructeur : initialise une nouvelle partie d'isolation
        """
        self.game_save = game_save
        self.round_turn = 0  # 0 pour le joueur 1, 1 pour le joueur 2
        self.board = Board(quadrants, 1)
        self.render = Render(game=self)

    def on_click(self, row, col):
        """
        procédure : gère les clics sur le plateau de jeu
        paramètres : row (ligne), col (colonne) - coordonnées du clic
        retourne : True si le jeu continue, False si la partie est terminée
        """
        cell = self.board.board[row][col]

        # vérifie si la case est déjà occupée
        if cell[0] is not None:
            self.render.edit_info_label("This cell is already occupied")
            return True

        # vérifie si la case est menacée par une tour adverse
        if is_threatened(self.board.board, row, col, self.round_turn):
            self.render.edit_info_label("This cell is threatened by an enemy tower")
            return True

        # place la tour du joueur actuel
        self.board.board[row][col][0] = self.round_turn
        self.round_turn = 1 - self.round_turn
        save_game(self)

        # vérifie si le joueur suivant a encore des mouvements possibles
        if not has_valid_move(self.board.board, self.round_turn):
            winner = "Player 2" if self.round_turn == 0 else "Player 1"
            self.render.edit_info_label(f"Game ended ! {winner} wins !")
            self.render.root.update_idletasks()
            messagebox.showinfo("End Game", f"{winner} wins !")
            self.render.root.destroy()
            return False

        # passe au tour du joueur suivant
        self.render.edit_info_label(f"Player {self.round_turn + 1} turn - Place your tower.")

        return True

    def load_game(self):
        """
        procédure : lance la boucle principale du jeu
        """
        self.render.root.mainloop()
