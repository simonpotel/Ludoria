import pygame
from src.board import Board
from src.windows.render.render import Render
from src.saves import save_game
from src.moves import available_move
from src.network.client.game_base import GameBase
from src.utils.logger import Logger
from src.congress.bot import CongressBot

class Game(GameBase):
    def __init__(self, game_save, quadrants, game_mode="Solo"):
        """
        constructeur : initialise une nouvelle partie de congress

        params:
            game_save: sauvegarde de jeu existante ou None
            quadrants: configuration des quadrants initiaux
            game_mode: mode de jeu ("Solo", "Bot", "Network")
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
            Logger.game("Game", "Congress bot mode initialized")

        if self.is_network_game:
            self.update_status_message("Waiting for another player...")

    def on_network_action(self, action_data):
        """
        procédure : gère une action reçue via le réseau (mouvement d'un autre joueur)

        params:
            action_data: dictionnaire contenant les données de l'action

        retour :
            bool: True si l'action a été traitée avec succès, False sinon
        """
        Logger.info("Game Congress", f"Received network action: {action_data}")
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

        Logger.info("Game Congress", f"Applied board state. Current turn: {self.round_turn}")
        
        save_game(self)
        
        # informe le renderer qu'une mise à jour est nécessaire
        self.render.needs_render = True
        
        # détermine qui a joué en dernier
        player_who_just_moved = 1 - self.round_turn
        
        Logger.game("Game Congress", f"Board state after network action for player {player_who_just_moved + 1}:")
        piece_positions = []
        for i in range(8):
            for j in range(8):
                if self.board.board[i][j][0] == player_who_just_moved:
                    piece_positions.append((i, j))
        Logger.game("Game Congress", f"Pieces for player {player_who_just_moved + 1}: {piece_positions}")
        
        # vérifie si le joueur qui a joué en dernier a gagné
        Logger.game("Game Congress", f"Checking victory condition for Player {player_who_just_moved + 1}")
        if self.check_connected_pieces(player_who_just_moved):
            if self.game_mode == "Bot" and player_who_just_moved == 1:
                winner_text = "BOT WON THE GAME !"
            else:
                winner_text = f"PLAYER {player_who_just_moved + 1} WON THE GAME !"
            self.render.show_end_popup(winner_text)
            
            # envoyer l'action réseau avant le nettoyage
            self.cleanup()
            return False  # le jeu est terminé

        # met à jour le message de statut en fonction du tour
        if self.is_network_game:
            if self.is_my_turn: 
                self.update_status_message(f"Your turn (Player {self.player_number})", "green")
            else:
                other_player_number = 1 if self.round_turn == 0 else 2
                self.update_status_message(f"Player {other_player_number}'s turn", "orange")
        else:
            self.render.edit_info_label(f"Player {self.round_turn + 1}'s turn")
            
        return True # le jeu continue

    def check_connected_pieces(self, player):
        """
        fonction : vérifie si tous les pions d'un joueur sont connectés orthogonalement via un parcours en profondeur (DFS)

        params:
            player: l'identifiant du joueur (0 ou 1)

        retour :
            bool: True si les pions sont connectés, False sinon
        """
        start_pos = None
        pieces = []
        
        # collecte des positions de toutes les pièces du joueur
        for i in range(8):
            for j in range(8):
                if self.board.board[i][j][0] == player:
                    pieces.append((i, j))
                    if start_pos is None:
                        start_pos = (i, j) # point de départ pour le parcours
        
        # si le joueur n'a pas de pièces, ils ne sont pas connectés (ou jeu fini)
        if not start_pos:
            Logger.warning("Game Congress", f"Player {player + 1} has no pieces on the board!")
            return False
        
        # si le joueur n'a qu'une seule pièce, elle est techniquement connectée
        if len(pieces) == 1:
            Logger.success("Game Congress", f"Player {player + 1} has only one piece, which is connected by default!")
            return True
        
        visited = set()
        stack = [start_pos]
        
        # parcours en profondeur (DFS) pour trouver toutes les pièces connectées
        while stack:
            current = stack.pop()
            if current not in visited:
                visited.add(current)
                row, col = current
                
                directions = [(0, 1), (1, 0), (0, -1), (-1, 0)] # mouvements orthogonaux
                for dr, dc in directions:
                    new_row, new_col = row + dr, col + dc
                    # vérifie les limites et si la case voisine appartient au joueur et n'a pas été visitée
                    if (0 <= new_row < 8 and 0 <= new_col < 8 and 
                        self.board.board[new_row][new_col][0] == player and 
                        (new_row, new_col) not in visited):
                        stack.append((new_row, new_col))
        
        # si le nombre de pièces visitées égale le nombre total de pièces, elles sont toutes connectées
        connected = len(visited) == len(pieces)
        
        Logger.game("Game Congress", f"Player {player + 1} has {len(pieces)} pieces, {len(visited)} connected")
        if not connected:
            unconnected = [p for p in pieces if p not in visited]
            Logger.warning("Game Congress", f"Unconnected pieces: {unconnected}")
        else:
            Logger.success("Game Congress", f"Player {player + 1} has all {len(pieces)} pieces connected!")
        
        return connected

    def on_click(self, row, col):
        """
        procédure : gère les clics de souris sur le plateau de jeu

        params:
            row: ligne du clic (0-7)
            col: colonne du clic (0-7)

        retour :
            bool: True si le jeu continue, False si la partie est terminée
        """
        if self.is_network_game:
            if not self.game_started:
                self.render.edit_info_label("Waiting for another player...")
                return True
            if not self.can_play():
                self.render.edit_info_label(f"Waiting for Player {2 if self.player_number == 1 else 1}")
                return True

        if self.game_mode == "Bot" and self.round_turn == 1:
            self.render.edit_info_label("C'est le tour du bot, veuillez patienter...")
            return True

        if not hasattr(self, 'selected_piece') or self.selected_piece is None:
             # cas : sélection d'une pièce
            cell = self.board.board[row][col]
            
            # détermine l'index correct du joueur à vérifier
            # mode réseau : utiliser assigned player_number (0 ou 1). Solo/Bot: utiliser current round_turn (0 ou 1).
            player_index_to_select = (self.player_number - 1) if self.is_network_game else self.round_turn
            
            # vérifie si la case contient une pièce appartenant au joueur correct
            if cell[0] is not None and cell[0] == player_index_to_select:
                # vérification supplémentaire pour le mode réseau : s'assurer que c'est bien le tour de ce joueur
                if self.is_network_game and not self.is_my_turn:
                    self.render.edit_info_label(f"Waiting for Player {2 if self.player_number == 1 else 1}")
                    return True # pas notre tour, même si on a cliqué sur notre pièce
                    
                self.selected_piece = (row, col)
                self.render.edit_info_label("Select destination")
                self.render.needs_render = True # redessine pour montrer la sélection
                return True
            elif cell[0] is not None:
                 # clic sur une pièce adverse ou une case vide lors de la tentative de sélection
                self.render.edit_info_label("Select your own piece")
                return True
            else:
                # clic sur une case vide lors de la tentative de sélection
                self.render.edit_info_label(f"Player {self.round_turn + 1}'s turn") # ou message de statut réseau
                return True
        else:
            # cas : déplacement d'une pièce sélectionnée
            old_row, old_col = self.selected_piece
            cell = self.board.board[row][col]
            
            # annuler la sélection si on clique sur la même pièce
            if (row, col) == (old_row, old_col):
                 self.selected_piece = None
                 self.render.edit_info_label(f"Player {self.round_turn + 1}'s turn")
                 self.render.needs_render = True # redessine pour enlever la surbrillance
                 return True

            # vérifier si la case de destination est occupée
            if cell[0] is not None:
                self.selected_piece = None
                self.render.edit_info_label("Cannot move to an occupied cell")
                self.render.needs_render = True # redessine pour enlever la surbrillance
                return True
            
            # vérifier si le mouvement est valide selon les règles du jeu
            if not available_move(self.board.board, old_row, old_col, row, col):
                self.selected_piece = None
                self.render.edit_info_label("Invalid move")
                self.render.needs_render = True # redessine pour enlever la surbrillance
                return True

            # execution du mouvement
            if self.is_network_game:
                  self.board.board[row][col][0] = self.board.board[old_row][old_col][0]
                  self.board.board[old_row][old_col][0] = None
                  self.selected_piece = None
                  
                  # vérification de victoire immédiate après le mouvement local
                  player_who_moved = self.player_number - 1
                  if self.check_connected_pieces(player_who_moved):
                      if self.game_mode == "Bot" and player_who_moved == 1:
                          winner_text = "BOT WON THE GAME !"
                      else:
                          winner_text = f"PLAYER {player_who_moved + 1} WON THE GAME !"
                      self.render.show_end_popup(winner_text)
                      
                      self.send_network_action({
                          "from_row": old_row,
                          "from_col": old_col,
                          "to_row": row,
                          "to_col": col
                      })
                      self.cleanup()
                      return False

                  # si pas de victoire, informer le renderer et envoyer l'action normalement
                  self.render.needs_render = True
                  self.send_network_action({
                      "from_row": old_row,
                      "from_col": old_col,
                      "to_row": row,
                      "to_col": col
                  })
                  return True

            # execution pour jeu Solo ou contre Bot
            self.board.board[row][col][0] = self.board.board[old_row][old_col][0]
            self.board.board[old_row][old_col][0] = None
            player_who_moved = self.round_turn
            self.selected_piece = None

            # vérifier si le joueur qui vient de jouer a gagné
            if self.check_connected_pieces(player_who_moved):
                if self.game_mode == "Bot" and player_who_moved == 1:
                    winner_text = "BOT WON THE GAME !"
                else:
                    winner_text = f"PLAYER {player_who_moved + 1} WON THE GAME !"
                self.render.show_end_popup(winner_text)
                self.render.needs_render = True
                return False

            self.round_turn = 1 - self.round_turn # changement de tour
            save_game(self)
            self.render.edit_info_label(f"Player {self.round_turn + 1}'s turn")
            self.render.needs_render = True

            # si c'est au tour du bot, déclenche son action après un court délai
            if self.game_mode == "Bot" and self.round_turn == 1:
                pygame.time.set_timer(pygame.USEREVENT, 500) # délai de 500ms
                self._bot_timer_set = True

            return True # clic géré, le jeu continue
    
    def _bot_play(self):
        """
        procédure : exécute le tour du bot

        retour :
            bool: True si le bot a joué avec succès, False si le bot ne peut pas jouer ou une erreur survient
        """
        try:
            if self.bot.make_move(): # la logique du bot met à jour le plateau
                player_who_moved = 1 # le bot est toujours le joueur 1
                # vérifie si le bot a gagné après son mouvement
                if self.check_connected_pieces(player_who_moved):
                    if self.game_mode == "Bot" and player_who_moved == 1:
                        winner_text = "BOT WON THE GAME !"
                    else:
                        winner_text = f"PLAYER {player_who_moved + 1} WON THE GAME !"
                    self.render.show_end_popup(winner_text)
                    self.cleanup()
                else:
                    self.round_turn = 0  # retour au tour du joueur 0
                    self.render.edit_info_label("Player 1's turn")
                    save_game(self)
                return True # mouvement réussi
            else:
                self.render.show_end_popup("PLAYER 1 WON THE GAME !")
                self.cleanup()
            return True # mouvement réussi
        except Exception as e:
            Logger.error("Game", f"Error during bot play: {str(e)}")
            self.render.edit_info_label(f"Error during bot play: {str(e)}")
            self.round_turn = 0 # assure que le contrôle revient au joueur
            self.render.edit_info_label("Player 1's turn")
            return False # indique que le mouvement a échoué

    def load_game(self):
        """
        procédure : lance la boucle principale de rendu et d'événements du jeu
        """
        self.render.edit_info_label(f"Player {self.round_turn + 1}'s turn")
        self.render.run_game_loop()
        if getattr(self.render, "end_popup_action", None) == "play_again":
            from src.windows.selector.selector import Selector
            Selector()
        self.cleanup()

    def get_board_state(self):
        """
        fonction : retourne l'état actuel du plateau et le tour

        retour :
            dict: un dictionnaire contenant une copie du plateau et le joueur actuel
        """
        return {
            "board": [
                [cell[:] for cell in row] for row in self.board.board
            ],
            "round_turn": self.round_turn
        }
