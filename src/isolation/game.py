import pygame
from src.board import Board
from src.render import Render
from src.captures import is_threatened, has_valid_move
from src.saves import save_game
from src.network.client.game_base import GameBase
from src.utils.logger import Logger
from src.isolation.bot import IsolationBot

class Game(GameBase):
    def __init__(self, game_save, quadrants, game_mode="Solo"):
        """
        constructeur : initialise une nouvelle partie d'isolation

        params:
            game_save: sauvegarde de jeu existante ou None
            quadrants: configuration des quadrants initiaux
            game_mode: mode de jeu ("Solo", "Bot", "Network")
        """
        super().__init__(game_save, quadrants, game_mode)
        self.board = Board(quadrants, 1)
        self.render = Render(game=self)
        self.round_turn = 0
        
        self.bot = None
        if game_mode == "Bot":
            self.bot = IsolationBot(player_id=2) 
            self.render.edit_info_label("Player 1's turn - Place your tower")
        
        if self.is_network_game:
            self.update_status_message("Waiting for another player...")

    def on_network_action(self, action_data):
        """
        procédure : traite une action reçue d'un autre joueur en réseau

        params:
            action_data: dictionnaire contenant les données de l'action (mouvement)

        retour:
            bool: True si l'action a été traitée avec succès, False sinon
        """
        Logger.info("Game Isolation", f"Received network action: {action_data}")
        if not action_data:
            Logger.error("Game", "Received empty action data")
            return False
            
        board_state = action_data.get("board_state")
        if not board_state or "board" not in board_state or "round_turn" not in board_state:
            Logger.error("Game", f"Received incomplete or invalid board state: {board_state}")
            return False
            
        # applique l'état reçu directement en utilisant la méthode de la classe de base
        if not self.update_board_from_state(board_state):
            Logger.error("Game", "Failed to apply received board state in on_network_action.")
            return False 
        
        Logger.info("Game Isolation", f"Applied board state. Current turn: {self.round_turn}")
        
        save_game(self)
        self.render.needs_render = True
        

        # verifie si l'ancien joueur a des coups valides
        if not has_valid_move(self.board.board, 1 - self.round_turn):
            winner = f"Player {self.round_turn + 1}" # le joueur qui vient de jouer gagne
            Logger.success("Game Isolation", f"Game over! {winner} wins because Player {1 - self.round_turn + 1} has no valid moves!")
            self.render.edit_info_label(f"Game Over! {winner} wins! (No moves left for Player {1 - self.round_turn + 1})")
            self.render.running = False # arrête la boucle de jeu
            self.cleanup()
            return False # la partie est terminée
            
        # met à jour le message de statut en fonction du tour
        if self.is_network_game:
            if self.is_my_turn: 
                self.update_status_message(f"Your turn (Player {self.player_number}) - Place tower", "green")
            else:
                other_player_number = 1 if self.round_turn == 0 else 2
                self.update_status_message(f"Player {other_player_number}'s turn - Place tower", "orange")
        else:
             self.render.edit_info_label(f"Player {self.round_turn + 1}'s turn - Place your tower")
            
        return True # le jeu continue

    def on_click(self, row, col):
        """
        procédure : gère les clics sur le plateau de jeu

        params:
            row: ligne du clic
            col: colonne du clic

        retour:
            bool: True si le jeu continue, False si la partie est terminée
        """
        # gestion des tours en mode réseau
        if self.is_network_game:
            if not self.game_started:
                self.render.edit_info_label("Waiting for another player...")
                return True
            if not self.can_play():
                self.render.edit_info_label(f"Waiting for Player {2 if self.player_number == 1 else 1}") 
                return True

        # vérification des limites du plateau
        if row >= len(self.board.board) or col >= len(self.board.board[0]):
            self.render.edit_info_label("Invalid move: out of bounds")
            return True

        cell = self.board.board[row][col]

        # vérification si la case est déjà occupée
        if cell[0] is not None:
            self.render.edit_info_label("This cell is already occupied")
            return True

        # vérification si la case est menacée
        current_player = 0 if self.player_number == 1 else 1 if self.is_network_game else self.round_turn
        if is_threatened(self.board.board, row, col, current_player):
            self.render.edit_info_label("This cell is threatened by an enemy tower")
            return True

        # gestion du clic en mode réseau (envoi avant mise à jour locale)
        if self.is_network_game:
            self.board.board[row][col][0] = current_player # mise à jour locale pour feedback visuel
            self.render.needs_render = True # Trigger render immediately after local update
            
            self.send_network_action({
                "row": row,
                "col": col
            })
            return True # le serveur gérera le changement de tour et la sauvegarde

        # execution du mouvement en mode solo ou bot
        self.board.board[row][col][0] = self.round_turn
        player_who_moved = self.round_turn
        self.round_turn = 1 - self.round_turn # changement de tour
        save_game(self) # sauvegarde après chaque coup valide
        
        self.render.needs_render = True
        
        # vérification de la fin de partie pour le joueur suivant
        Logger.game("Game Isolation", f"Checking if Player {self.round_turn + 1} has valid moves")
        if not has_valid_move(self.board.board, self.round_turn):
            winner = f"Player {player_who_moved + 1}" # le joueur qui vient de jouer gagne
            Logger.success("Game Isolation", f"Game over! {winner} wins because Player {self.round_turn + 1} has no valid moves!")
            self.render.edit_info_label(f"Game Over! {winner} wins!")
            self.render.running = False # arrête la boucle de jeu
            return False

        # gestion du tour du bot
        if self.round_turn == 1 and self.game_mode == "Bot":
            self.render.edit_info_label("Bot is thinking...")
            pygame.time.set_timer(pygame.USEREVENT, 500) # délai pour l'action du bot
            self._bot_timer_set = True
        else:
            self.render.edit_info_label(f"Player {self.round_turn + 1}'s turn - Place your tower")
            
        return True # le jeu continue

    def _bot_play(self):
        """
        procédure : exécute le tour du bot

        retour:
            bool: True si le bot a joué avec succès, False sinon
        """
        try:
            bot_move = self.bot.get_move(self.board.board)
            if bot_move is None:
                winner = "Player 1"
                Logger.success("Game Isolation", f"Game over! {winner} wins because Bot has no valid moves!")
                self.render.edit_info_label(f"Game Over! {winner} wins!")
                self.render.running = False
                self.cleanup()
                return False
                
            bot_row, bot_col = bot_move
            self.board.board[bot_row][bot_col][0] = self.round_turn # placement de la tour du bot
            player_who_moved = self.round_turn
            self.round_turn = 1 - self.round_turn # retour au tour du joueur humain
            save_game(self)
            
            # vérification de la fin de partie après le coup du bot
            Logger.game("Game Isolation", f"Checking if Player {self.round_turn + 1} has valid moves after bot's move")
            if not has_valid_move(self.board.board, self.round_turn):
                winner = f"Player {player_who_moved + 1} (Bot)" # le bot gagne
                Logger.success("Game Isolation", f"Game over! {winner} wins because Player {self.round_turn + 1} has no valid moves!")
                self.render.edit_info_label(f"Game Over! {winner} wins!")
                self.render.running = False
                self.cleanup()
                return False
            
            self.render.edit_info_label("Player 1's turn - Place your tower") # mise à jour du message
            return True
        except Exception as e:
            Logger.error("Game", f"Bot error: {str(e)}")
            self.render.edit_info_label(f"Bot error: {str(e)}") # affiche l'erreur dans le jeu
            return False # indique un échec

    def load_game(self):
        """
        procédure : lance la boucle principale du jeu
        """
        self.render.edit_info_label(f"Player {self.round_turn + 1}'s turn - Place your tower")
        self.render.run_game_loop()
        self.cleanup() # nettoyage après la fin de la boucle de jeu

    def get_board_state(self):
        """
        fonction : retourne l'état actuel complet du jeu pour la sauvegarde ou le réseau

        retour:
            dict: dictionnaire contenant l'état du plateau et le tour
        """
        return {
            "board": [[cell[:] for cell in row] for row in self.board.board], # copie profonde du plateau
            "round_turn": self.round_turn
        }
