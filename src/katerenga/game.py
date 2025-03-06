from tkinter import messagebox
from src.board import Board
from src.render import Render
from src.captures import has_valid_move
from src.saves import save_game
from src.moves import available_move
from src.game_base import GameBase
from src.utils.logger import Logger

class Game(GameBase):
    def __init__(self, game_save, quadrants, game_mode="Solo"):
        """
        constructeur : initialise une nouvelle partie de katarenga
        """
        super().__init__(game_save, quadrants, game_mode)
        self.board = Board(quadrants, 0)
        self.render = Render(game=self)
        self.round_turn = 0
        self.first_turn = True
        self.selected_piece = None

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
        
        old_row = action_data.get("from_row")
        old_col = action_data.get("from_col")
        new_row = action_data.get("to_row")
        new_col = action_data.get("to_col")
        
        if None in (old_row, old_col, new_row, new_col):
            Logger.error("Game", "Missing move coordinates in action data")
            return False
        
        self.board.board = [[cell[:] for cell in row] for row in board_state["board"]]
        self.round_turn = board_state["round_turn"]
        self.first_turn = board_state["first_turn"]
        
        if self.board.board[new_row][new_col][0] is not None:
            if not self.first_turn:
                self.capture_piece(new_row, new_col)
        
        self.board.board[new_row][new_col][0] = self.board.board[old_row][old_col][0]
        self.board.board[old_row][old_col][0] = None
        
        self.round_turn = 1 - self.round_turn
        if self.first_turn and self.round_turn == 0:
            self.first_turn = False
        
        save_game(self)
        self.render.render_board()
        
        if self.check_win(1 - self.round_turn):
            self.cleanup()
            self.render.root.destroy()
            return False
        
        if self.is_network_game:
            if self.is_my_turn:
                self.update_status_message(f"Your turn (Player {self.player_number})", "green")
            else:
                other_player = 2 if self.player_number == 1 else 1
                self.update_status_message(f"Player {other_player}'s turn", "orange")
        
        return True

    def load_game(self):
        """
        procédure : lance la boucle principale du jeu
        """
        self.render.root.mainloop()
        self.cleanup()

    def check_win(self, player):
        """
        fonction : vérifie les conditions de victoire pour un joueur
        paramètres : player - indice du joueur (0 ou 1)
        retourne : True si le joueur a gagné, False sinon
        """
        opponent = 1 - player
        opponent_camps = [(9, 0), (9, 9)] if player == 0 else [(0, 9), (0, 0)]

        # vérifie si le joueur occupe les deux camps adverses
        camps_occupied = sum(1 for camp in opponent_camps
                             if self.board.board[camp[0]][camp[1]][0] == player)

        if camps_occupied == 2:
            messagebox.showinfo("Victory!", f"Player {player + 1} wins by occupying both camps!")
            return True

        # vérifie si l'adversaire n'a plus de mouvements possibles
        opponent_has_moves = False
        for row in range(10):  
            if opponent_has_moves:
                break
            for col in range(10):
                if self.board.board[row][col][0] == opponent:
                    for dest_row in range(10):
                        for dest_col in range(10):
                            if (self.board.board[dest_row][dest_col][0] is None or 
                                self.board.board[dest_row][dest_col][0] != opponent):
                                if available_move(self.board.board, row, col, dest_row, dest_col):
                                    opponent_has_moves = True
                                    break
                        if opponent_has_moves:
                            break
                if opponent_has_moves:
                    break

        if not opponent_has_moves:
            messagebox.showinfo("Victory!", f"Player {player + 1} wins by blocking opponent!")
            return True

        return False

    def capture_piece(self, row, col):
        """
        procédure : capture une pièce en la retirant du plateau
        paramètres : row (ligne), col (colonne) - position de la pièce à capturer
        """
        self.board.board[row][col][0] = None

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

        # gestion du premier clic - sélection d'une pièce
        if self.selected_piece is None:
            if cell[0] is not None and cell[0] == self.round_turn:
                self.selected_piece = (row, col)
                self.render.edit_info_label("Select destination")
                self.render.render_board()
                return True
            else:
                self.render.edit_info_label("Select your own piece")
                return True

        old_row, old_col = self.selected_piece

        # annulation de la sélection si on reclique sur la même pièce
        if (row, col) == (old_row, old_col):
            self.selected_piece = None
            self.render.edit_info_label("Piece unselected")
            self.render.render_board()
            return True

        # vérifie si le mouvement est valide
        if not available_move(self.board.board, old_row, old_col, row, col):
            self.selected_piece = None
            self.render.edit_info_label("Invalid move")
            return True

        # gestion de la capture de pièce
        if cell[0] is not None and cell[0] != self.round_turn:
            if not self.first_turn:
                self.capture_piece(row, col)
            else:
                self.selected_piece = None
                self.render.edit_info_label("No capture allowed on first turn")
                return True

        if self.is_network_game:
            self.send_network_action({
                "from_row": old_row,
                "from_col": old_col,
                "to_row": row,
                "to_col": col
            })

        # vérifie si la pièce atteint un camp adverse
        finish_line = 0 if self.round_turn == 1 else 9
        if row == finish_line:
            if (row == 0 and (col == 0 or col == 9)) or (row == 9 and (col == 0 or col == 9)):
                self.board.board[row][col][0] = self.board.board[old_row][old_col][0]
                self.board.board[old_row][old_col][0] = None
                self.selected_piece = None

                if self.check_win(self.round_turn):
                    self.cleanup()
                    self.render.root.destroy()
                    return False

        else:
            # effectue le déplacement normal
            self.board.board[row][col][0] = self.board.board[old_row][old_col][0]
            self.board.board[old_row][old_col][0] = None

        self.selected_piece = None

        # passe au tour du joueur suivant
        self.round_turn = 1 - self.round_turn
        if self.first_turn and self.round_turn == 0:
            self.first_turn = False

        self.render.edit_info_label(f"Player {self.round_turn + 1}'s turn")
        save_game(self)
        self.render.render_board()

        return True 