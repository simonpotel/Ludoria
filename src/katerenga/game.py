import pygame
from src.board import Board
from src.render import Render
from src.captures import has_valid_move
from src.saves import save_game
from src.moves import available_move
from src.network.client.game_base import GameBase
from src.utils.logger import Logger
from src.katerenga.bot import KaterengaBot

class Game(GameBase):
    def __init__(self, game_save, quadrants, game_mode="Solo"):
        """
        constructeur : initialise une nouvelle partie de katarenga

        params:
            game_save: sauvegarde de jeu existante ou None
            quadrants: configuration des quadrants initiaux
            game_mode: mode de jeu ("Solo", "Bot", "Network")
        """
        super().__init__(game_save, quadrants, game_mode)
        self.board = Board(quadrants, 0)
        self.render = Render(game=self)
        self.round_turn = 0
        self.first_turn = True # le premier tour a des règles spéciales (pas de capture)
        self.selected_piece = None
        self.game_mode = game_mode
        self.locked_pieces = [] # pièces arrivées dans un camp adverse
        self.bot = None
        
        self.camps = [(0, 0), (0, 9), (9, 0), (9, 9)] # positions des camps
        
        if game_mode == "Bot":
            self.bot = KaterengaBot(self)
            Logger.game("Game", "Katerenga bot mode initialized")

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
        
        # mise à jour de l'état local du plateau
        self.board.board = [[cell[:] for cell in row] for row in board_state["board"]]
        self.round_turn = board_state["round_turn"]
        self.first_turn = board_state["first_turn"]
        
        # gestion de la capture si la case d'arrivée est occupée par l'adversaire
        if self.board.board[new_row][new_col][0] is not None and self.board.board[new_row][new_col][0] != self.round_turn:
            if not self.first_turn:
                self.capture_piece(new_row, new_col)
        
        # execution du mouvement
        self.board.board[new_row][new_col][0] = self.board.board[old_row][old_col][0]
        self.board.board[old_row][old_col][0] = None
        
        # changement de tour et gestion du premier tour
        self.round_turn = 1 - self.round_turn
        if self.first_turn and self.round_turn == 0: # fin du premier tour après le coup du joueur 2
            self.first_turn = False
        
        save_game(self)
        self.render.render_board()
        
        # verification de la victoire après le coup réseau
        if self.check_win(1 - self.round_turn): # le joueur qui vient de jouer
            self.cleanup()
            return False
        
        # mise à jour du message de statut en réseau
        if self.is_network_game:
            if self.is_my_turn:
                self.update_status_message(f"Your turn (Player {self.player_number})", "green")
            else:
                other_player = 2 if self.player_number == 1 else 1
                self.update_status_message(f"Player {other_player}'s turn", "orange")
        
        return True

    def load_game(self):
        """
        procédure : lance la boucle principale de rendu et d'événements du jeu
        """
        self.render.edit_info_label(f"Player {self.round_turn + 1}'s turn")
        self.render.run_game_loop()
        self.cleanup()

    def check_win(self, player):
        """
        fonction : vérifie si un joueur a gagné la partie

        params:
            player: l'identifiant du joueur (0 ou 1) à vérifier

        retour:
            bool: True si le joueur a gagné, False sinon
        """
        opponent = 1 - player
        # définition des camps adverses en fonction du joueur
        opponent_camps = [(9, 0), (9, 9)] if player == 0 else [(0, 9), (0, 0)]

        # condition 1: occupation des deux camps adverses
        camps_occupied = []
        for camp in opponent_camps:
            if self.board.board[camp[0]][camp[1]][0] == player:
                camps_occupied.append(camp)
        
        if len(camps_occupied) == 2:
            Logger.success("Game", f"Player {player + 1} won by occupying both camps: {camps_occupied}")
            self.render.edit_info_label(f"Player {player + 1} wins by occupying both camps!")
            self.render.running = False # arrête la boucle de jeu
            return True

        # condition 2: l'adversaire ne peut plus bouger
        opponent_has_moves = False
        for row in range(10):  
            if opponent_has_moves:
                break
            for col in range(10):
                if self.board.board[row][col][0] == opponent:
                    # recherche d'au moins un mouvement valide pour l'adversaire
                    for dest_row in range(10):
                        for dest_col in range(10):
                            if (self.board.board[dest_row][dest_col][0] is None or 
                                self.board.board[dest_row][dest_col][0] != opponent): # case vide ou occupée par le joueur courant
                                if available_move(self.board.board, row, col, dest_row, dest_col):
                                    opponent_has_moves = True
                                    break # mouvement trouvé, pas besoin de chercher plus
                        if opponent_has_moves:
                            break
                if opponent_has_moves:
                    break

        if not opponent_has_moves:
            Logger.success("Game", f"Player {player + 1} won by blocking opponent from making moves")
            self.render.edit_info_label(f"Player {player + 1} wins by blocking opponent!")
            self.render.running = False # arrête la boucle de jeu
            return True

        return False # aucune condition de victoire remplie

    def capture_piece(self, row, col):
        """
        procédure : retire une pièce capturée du plateau

        params:
            row: ligne de la pièce capturée
            col: colonne de la pièce capturée
        """
        self.board.board[row][col][0] = None

    def on_click(self, row, col):
        """
        procédure : gère les clics de souris sur le plateau de jeu

        params:
            row: ligne du clic (0-9)
            col: colonne du clic (0-9)

        retour:
            bool: True si le jeu continue, False si la partie est terminée
        """
        # gestion des tours en mode réseau ou bot
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

        cell = self.board.board[row][col]

        # cas 1: aucune pièce sélectionnée
        if self.selected_piece is None:
            # selection d'une pièce du joueur courant
            if cell[0] is not None and cell[0] == self.round_turn:
                self.selected_piece = (row, col)
                self.render.edit_info_label("Select destination")
                return True
            else:
                self.render.edit_info_label("Select your own piece")
                return True

        # cas 2: une pièce est déjà sélectionnée
        old_row, old_col = self.selected_piece

        # déselectionner si on clique sur la même pièce
        if (row, col) == (old_row, old_col):
            self.selected_piece = None
            self.render.edit_info_label(f"Player {self.round_turn + 1}'s turn")
            return True

        # verification de la validité du mouvement
        if not available_move(self.board.board, old_row, old_col, row, col):
            self.selected_piece = None
            self.render.edit_info_label("Invalid move")
            return True

        # gestion de la capture
        capture_made = False
        if cell[0] is not None and cell[0] != self.round_turn:
            if not self.first_turn:
                self.capture_piece(row, col)
                capture_made = True
            else:
                # pas de capture au premier tour
                self.selected_piece = None
                self.render.edit_info_label("No capture allowed on first turn")
                return True
        elif cell[0] is not None and cell[0] == self.round_turn:
             # impossible de se déplacer sur une case alliée
             self.selected_piece = None
             self.render.edit_info_label("Cannot move to an occupied friendly cell")
             return True
        
        # execution du mouvement et vérification de victoire
        move_made = False
        is_win = False
        
        # envoi de l'action réseau si nécessaire
        if self.is_network_game:
            self.send_network_action({
                "from_row": old_row,
                "from_col": old_col,
                "to_row": row,
                "to_col": col
            })
            # la mise à jour locale se fera via on_network_action
            self.selected_piece = None # désélection après envoi
            self.render.render_board() # rafraichir pour montrer la déselection
            return True
        
        # execution locale (solo ou bot)
        finish_line = 0 if self.round_turn == 1 else 9 # ligne d'arrivée dépend du joueur
        # vérifie si le mouvement atteint un camp sur la ligne d'arrivée
        if row == finish_line and self.is_camp_position(row, col):
            self.board.board[row][col][0] = self.board.board[old_row][old_col][0]
            self.board.board[old_row][old_col][0] = None
            self.selected_piece = None
            self.locked_pieces.append((row, col)) # bloque la pièce dans le camp
            Logger.game("Game", f"Piece locked in camp at ({row}, {col}) for player {self.round_turn + 1}")
            move_made = True
            is_win = self.check_win(self.round_turn)
            if is_win: self.render.running = False
        else:
            # mouvement normal
            self.board.board[row][col][0] = self.board.board[old_row][old_col][0]
            self.board.board[old_row][old_col][0] = None
            self.selected_piece = None
            move_made = True
            is_win = self.check_win(self.round_turn)
            if is_win: self.render.running = False

        # après un mouvement réussi
        if move_made and not is_win:
            self.round_turn = 1 - self.round_turn # changement de tour
            if self.first_turn and self.round_turn == 0:
                self.first_turn = False # fin du premier tour
            self.render.edit_info_label(f"Player {self.round_turn + 1}'s turn")
            save_game(self) # sauvegarde après le coup

            # déclenchement du tour du bot si nécessaire
            if self.game_mode == "Bot" and self.round_turn == 1:
                pygame.time.set_timer(pygame.USEREVENT, 500) # délai pour le bot
                self._bot_timer_set = True
                
        elif move_made and is_win:
            # la partie est finie, le message de victoire est déjà affiché par check_win
            save_game(self) # sauvegarde l'état final
            return False # arrête le jeu
        elif capture_made:
             # si seulement une capture a été faite (ne devrait pas arriver avec les règles actuelles)
             # mais on rafraîchit au cas où
             self.render.render_board()

        if not is_win: # si le jeu n'est pas fini, on rafraîchit après toutes les opérations
             self.render.render_board() 

        return True # le jeu continue (sauf si is_win est True et traité ci-dessus)
        
    def _bot_play(self):
        """
        procédure : exécute le tour du bot (appelé via timer)

        retour:
            bool: True si le bot a joué avec succès, False si erreur ou fin de partie
        """
        try:
            Logger.game("Game", "Bot starting its move")
            move_successful = self.bot.make_move() # la logique du bot met à jour le plateau et vérifie la victoire
            
            if not move_successful:
                # cas où le bot ne peut pas jouer (peut indiquer une victoire de l'autre joueur)
                Logger.game("Game", "Bot move resulted in game end or no possible moves")
                # on revérifie la victoire pour être sûr que le message est correct
                if not self.check_win(1): # si le bot (joueur 1) n'a pas gagné...
                    if not self.check_win(0): # ... et que le joueur 0 non plus...
                        # alors le joueur 0 gagne car le bot est bloqué
                        self.render.edit_info_label("Player 1 wins! Bot has no more moves.")
                        self.check_win(0) # pour s'assurer que running est False
                self.cleanup()
                self.render.running = False
                return False
            else:
                # le coup du bot a réussi, le jeu continue ou est fini par le bot
                Logger.game("Game", "Bot completed its move successfully")
                # le changement de tour et la sauvegarde sont gérés dans bot.make_move
                # la vérification de victoire est aussi gérée dans bot.make_move
                # on met à jour l'affichage
                self.render.render_board()
                if not self.render.running: # si le bot a gagné
                     save_game(self)
                     return False
                else: # si le jeu continue
                     self.render.edit_info_label(f"Player {self.round_turn + 1}'s turn")
                     save_game(self)
                     return True
        except Exception as e:
            Logger.error("Game", f"Error during bot play: {str(e)}")
            self.render.edit_info_label(f"Error during bot play: {str(e)}")
            self.round_turn = 0 # redonne la main au joueur en cas d'erreur
            self.render.edit_info_label(f"Player {self.round_turn + 1}'s turn")
            self.render.render_board()
            return False

    def get_board_state(self):
        """
        fonction : retourne l'état actuel complet du jeu pour la sauvegarde ou le réseau

        retour:
            dict: dictionnaire contenant l'état du plateau, le tour et le flag first_turn
        """
        return {
            "board": [[cell[:] for cell in row] for row in self.board.board], # copie profonde
            "round_turn": self.round_turn,
            "first_turn": self.first_turn,
            "locked_pieces": list(self.locked_pieces) # copie de la liste
        }

    def is_camp_position(self, row, col):
        """
        fonction : vérifie si une position donnée correspond à l'un des quatre camps

        params:
            row: ligne de la position
            col: colonne de la position

        retour:
            bool: True si la position est un camp, False sinon
        """
        return (row, col) in self.camps # vérifie l'appartenance à la liste des camps 