from tkinter import messagebox
from src.board import Board
from src.render import Render
from src.captures import has_valid_move
from src.saves import save_game
from src.moves import available_move
from src.network.client.game_base import GameBase
from src.utils.logger import Logger
from src.congress.bot import CongressBot

class Game(GameBase):
    def __init__(self, game_save, quadrants, game_mode="Solo"):
        """
        constructeur : initialise une nouvelle partie de congress
        """
        super().__init__(game_save, quadrants, game_mode)
        self.board = Board(quadrants, 2)
        self.render = Render(game=self)
        self.round_turn = 0
        self.selected_piece = None
        self.game_mode = game_mode
        self.bot = None
        if game_mode == "Bot":
            self.bot = CongressBot(self)

        if self.is_network_game:
            self.update_status_message("Waiting for another player...")

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
        
        save_game(self)
        self.render.render_board()
        
        other_player = 1 if self.player_number == 1 else 0
        if self.check_connected_pieces(other_player):
            winner = f"Player {3 - self.player_number}"
            messagebox.showinfo("Game Over", f"{winner} has won!")
            self.cleanup()
            return False
            
        if self.is_network_game:
            if self.is_my_turn:
                self.update_status_message(f"Your turn (Player {self.player_number})", "green")
            else:
                other_player = 2 if self.player_number == 1 else 1
                self.update_status_message(f"Player {other_player}'s turn", "orange")
            
        return True

    def check_connected_pieces(self, player):
        """
        fonction : vérifie si tous les pions d'un joueur sont connectés orthogonalement
        retourne : True si les pions sont connectés, False sinon
        """
        start_pos = None
        pieces = []
        
        for i in range(8):
            for j in range(8):
                if self.board.board[i][j][0] == player:
                    pieces.append((i, j))
                    if start_pos is None:
                        start_pos = (i, j)
        
        if not start_pos:
            return False
        
        visited = set()
        stack = [start_pos]
        
        while stack:
            current = stack.pop()
            if current not in visited:
                visited.add(current)
                row, col = current
                
                directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
                for dr, dc in directions:
                    new_row, new_col = row + dr, col + dc
                    if (0 <= new_row < 8 and 0 <= new_col < 8 and 
                        self.board.board[new_row][new_col][0] == player and 
                        (new_row, new_col) not in visited):
                        stack.append((new_row, new_col))
        
        return len(visited) == len(pieces)

    def on_click(self, row, col):
        """
        procédure : gère les clics sur le plateau de jeu
        paramètres : row (ligne), col (colonne) - coordonnées du clic
        retourne : True si le jeu continue, False si la partie est terminée
        """
        if self.is_network_game:
            if not self.game_started:
                self.render.edit_info_label("Waiting for another player...")
                return True
            if not self.can_play():
                return True

        # Si c'est le tour du bot (joueur 2) et que le mode bot est activé, ignorer les clics
        if self.game_mode == "Bot" and self.round_turn == 1:
            self.render.edit_info_label("C'est le tour du bot, veuillez patienter...")
            return True

        if not hasattr(self, 'selected_piece'):
            self.selected_piece = None
        
        cell = self.board.board[row][col]

        # gestion du premier clic - sélection d'une pièce
        if self.selected_piece is None:
            if self.is_network_game:
                player_pieces = 0 if self.player_number == 1 else 1
                if cell[0] is None or cell[0] != player_pieces:
                    self.render.edit_info_label("Select your own piece")
                    return True
            else:
                if cell[0] is None or cell[0] != self.round_turn:
                    self.render.edit_info_label("Select your own piece")
                    return True
                    
            self.selected_piece = (row, col)
            self.render.edit_info_label("Select destination")
            self.render.render_board()
            return True

        old_row, old_col = self.selected_piece
        
        # Vérifier que la case de destination est vide (pas de capture dans Congress)
        if cell[0] is not None:
            self.selected_piece = None
            self.render.edit_info_label("Cannot move to an occupied cell")
            return True
        
        # vérifie si le mouvement est valide
        if not available_move(self.board.board, old_row, old_col, row, col):
            self.selected_piece = None
            self.render.edit_info_label("Invalid move")
            return True

        if self.is_network_game:
            temp_piece = self.board.board[old_row][old_col][0]
            self.board.board[row][col][0] = temp_piece
            self.board.board[old_row][old_col][0] = None
            self.selected_piece = None
            self.render.render_board()
            
            self.send_network_action({
                "from_row": old_row,
                "from_col": old_col,
                "to_row": row,
                "to_col": col
            })
            return True

        self.board.board[row][col][0] = self.board.board[old_row][old_col][0]
        self.board.board[old_row][old_col][0] = None
        self.selected_piece = None

        # vérifie la condition de victoire
        if self.check_connected_pieces(self.round_turn):
            winner = f"Player {self.round_turn + 1}"
            self.render.edit_info_label(f"Game Over! {winner} wins!")
            messagebox.showinfo("Game Over", f"{winner} has won!")
            self.cleanup()
            self.render.root.destroy()
            return False

        # passe au tour du joueur suivant
        self.round_turn = 1 - self.round_turn
        save_game(self)
        
        self.render.edit_info_label(f"Player {self.round_turn + 1}'s turn")
        self.render.render_board()

        # Après le tour du joueur, faire jouer le bot si c'est son tour
        if self.game_mode == "Bot" and self.round_turn == 1:
            # Petit délai avant que le bot ne joue pour une meilleure expérience utilisateur
            self.render.root.after(500, self._bot_play)

        return True
    
    def _bot_play(self):
        """
        Méthode pour faire jouer le bot dans un thread séparé
        """
        if self.bot.make_move():
            self.round_turn = 0  # Passe au joueur 1
            self.render.edit_info_label("Player 1's turn")
            self.render.render_board()
            save_game(self)
        else:
            # Le bot ne peut plus jouer ou a gagné
            if not self.check_connected_pieces(1):  # Si le bot n'a pas gagné
                messagebox.showinfo("Game Over", "Player 1 wins! Bot has no more moves.")
            self.cleanup()
            self.render.root.destroy()

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
