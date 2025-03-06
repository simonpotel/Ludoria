from src.board import Board
from src.render import Render
from src.captures import is_threatened, has_valid_move
from tkinter import messagebox
from src.saves import save_game
from src.game_base import GameBase
from src.utils.logger import Logger

class Game(GameBase):
    def __init__(self, game_save, quadrants, game_mode="Solo"):
        """
        constructeur : initialise une nouvelle partie d'isolation
        """
        super().__init__(game_save, quadrants, game_mode)
        self.board = Board(quadrants, 1)
        self.render = Render(game=self)
        self.round_turn = 0
        
        if self.is_network_game:
            self.update_status_message("Waiting for another player to join...")

    def on_network_action(self, action_data):
        """Handle move received from other player"""
        if not action_data:
            Logger.error("Game", "Received empty action data")
            return False
            
        board_state = action_data.get("board_state")
        if not board_state:
            Logger.error("Game", "Received empty board state")
            return False
            
        row = action_data.get("row")
        col = action_data.get("col")
        
        if None in (row, col):
            Logger.error("Game", "Missing move coordinates in action data")
            return False
            
        self.board.board = [[cell[:] for cell in row] for row in board_state["board"]]
        self.round_turn = board_state["round_turn"]
        
        save_game(self)
        self.render.render_board()
        
        if not has_valid_move(self.board.board, self.round_turn):
            winner = "Player 2" if self.round_turn == 0 else "Player 1"
            self.cleanup()
            self.render.root.destroy()
            return False
            
        return True

    def on_click(self, row, col):
        """
        procédure : gère les clics sur le plateau de jeu
        paramètres : row (ligne), col (colonne) - coordonnées du clic
        retourne : True si le jeu continue, False si la partie est terminée
        """
        if self.is_network_game:
            if not self.game_started:
                self.render.edit_info_label("Waiting for another player to join...")
                return True
            if not self.can_play():
                return True

        cell = self.board.board[row][col]

        # vérifie si la case est déjà occupée
        if cell[0] is not None:
            self.render.edit_info_label("This cell is already occupied")
            return True

        # vérifie si la case est menacée par une tour adverse
        if is_threatened(self.board.board, row, col, self.round_turn):
            self.render.edit_info_label("This cell is threatened by an enemy tower")
            return True

        if self.is_network_game:
            self.send_network_action({
                "row": row,
                "col": col,
                "board_state": self.get_board_state()
            })

        # place la tour du joueur actuel
        self.board.board[row][col][0] = self.round_turn
        self.round_turn = 1 - self.round_turn
        save_game(self)

        # vérifie si le joueur suivant a encore des mouvements possibles
        if not has_valid_move(self.board.board, self.round_turn):
            winner = "Player 2" if self.round_turn == 0 else "Player 1"
            self.render.edit_info_label(f"Game ended ! {winner} wins !")
            messagebox.showinfo("End Game", f"{winner} wins !")
            self.cleanup()
            self.render.root.destroy()
            return False

        # passe au tour du joueur suivant
        if self.is_network_game:
            if self.is_my_turn:
                self.update_status_message(f"Your turn (Player {self.player_number})", "green")
            else:
                other_player = 2 if self.player_number == 1 else 1
                self.update_status_message(f"Player {other_player}'s turn", "orange")
        else:
            self.render.edit_info_label(f"Player {self.round_turn + 1} turn - Place your tower.")

        return True

    def load_game(self):
        """
        procédure : lance la boucle principale du jeu
        """
        self.render.root.mainloop()
        self.cleanup()

    def get_board_state(self):
        return {
            "board": [[cell[:] for cell in row] for row in self.board.board],
            "round_turn": self.round_turn
        }
