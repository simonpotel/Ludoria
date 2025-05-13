import pygame
from src.board import Board
from src.windows.render.render import Render
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
        Logger.info("Game Katerenga", f"Received network action: {action_data}")
        if not action_data:
            Logger.error("Game", "Received empty action data")
            return False
        
        board_state = action_data.get("board_state")
        if not board_state or "board" not in board_state or "round_turn" not in board_state or "first_turn" not in board_state:
            Logger.error("Game", f"Received incomplete or invalid board state: {board_state}")
            return False
        
        # vérifie que locked_pieces est présent dans le board_state
        if "locked_pieces" not in board_state:
            Logger.warning("Game Katerenga", "Received board state without locked_pieces information")
            board_state["locked_pieces"] = []  # assure un état par défaut
        
        # applique l'état reçu directement
        if not self.update_board_from_state(board_state):
             Logger.error("Game", "Failed to apply received board state in on_network_action.")
             return False # indique un échec
        
        Logger.info("Game Katerenga", f"Applied board state. Current turn: {self.round_turn}, First turn: {self.first_turn}, Locked pieces: {self.locked_pieces}")

        # fin du premier tour ? (Après que J2 (index 1) ait joué et que le tour revienne à J1 (index 0))
        if self.first_turn and self.round_turn == 0:
            self.first_turn = False
            Logger.info("Game Katerenga", "First turn completed.")

        # l'état du plateau reçu *devrait* refléter l'état *après* le coup de l'adversaire,
        # y compris les captures et les verrous. Pas besoin de réappliquer la logique de mouvement ici.

        save_game(self)
        self.render.needs_render = True
        
        # détermine qui a joué en dernier en fonction du nouveau round_turn et notre numéro de joueur
        # ajuster en fonction du joueur local
        opponent_player = 0 if self.player_number == 2 else 1
        player_who_just_moved = opponent_player  # l'adversaire vient de jouer
        
        # vérifie si le joueur qui vient de jouer a gagné
        Logger.game("Game Katerenga", f"Checking victory condition for Player {player_who_just_moved + 1}")
        if self.check_win(player_who_just_moved):
            Logger.success("Game Katerenga", f"Game over! Player {player_who_just_moved + 1} wins!")
            self.render.show_end_popup(f"Player {player_who_just_moved + 1} wins!")
            return False # la partie est terminée
        
        # met à jour le message de statut en fonction du tour
        if self.is_network_game:
            if self.is_my_turn: # is_my_turn doit avoir été mis à jour par les gestionnaires de GameBase
                self.update_status_message(f"Your turn (Player {self.player_number})", "green")
            else:
                other_player = 1 if self.player_number == 2 else 2  # numéro de joueur opposé
                self.update_status_message(f"Player {other_player}'s turn", "orange")
        else:
            # fallback pour le contexte non réseau, bien que cette fonction principalement gère le réseau
            self.render.edit_info_label(f"Player {self.round_turn + 1}'s turn")

        return True # le jeu continue

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
        
        # Normaliser les coordonnées pour la comparaison
        normalized_locked = []
        for pos in self.locked_pieces:
            if isinstance(pos, list):
                normalized_locked.append(tuple(pos))
            else:
                normalized_locked.append(pos)
        
        Logger.game("Game Katerenga", f"Checking win for player {player+1}. Opponent camps: {opponent_camps}, Locked pieces: {normalized_locked}")

        # condition 1: occupation des deux camps adverses
        camps_occupied = []
        for camp in opponent_camps:
            if self.board.board[camp[0]][camp[1]][0] == player or camp in normalized_locked:
                camps_occupied.append(camp)
        
        if len(camps_occupied) == 2:
            if self.game_mode == "Bot" and player == 1:
                winner_text = "BOT WON THE GAME !"
            else:
                winner_text = f"PLAYER {player + 1} WON THE GAME !"
            self.render.show_end_popup(winner_text)
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
            if self.game_mode == "Bot" and player == 1:
                winner_text = "BOT WON THE GAME !"
            else:
                winner_text = f"PLAYER {player + 1} WON THE GAME !"
            self.render.show_end_popup(winner_text)
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
        
        # vérifie si la destination est sur le contour (case grise)
        size = len(self.board.board)
        is_edge = (row == 0 or row == size-1 or col == 0 or col == size-1)
        
        # cas 1: aucune pièce sélectionnée
        if self.selected_piece is None:
            # détermine l'index correct du joueur à vérifier
            player_index_to_select = self.player_number - 1 if self.is_network_game else self.round_turn
            
            # sélection d'une pièce du joueur dont c'est le tour (ou du joueur local en réseau)
            if cell[0] is not None and cell[0] == player_index_to_select:
                # vérification supplémentaire pour le mode réseau : s'assurer que c'est bien le tour de ce joueur
                if self.is_network_game and not self.is_my_turn:
                    self.render.edit_info_label(f"Waiting for Player {2 if self.player_number == 1 else 1}")
                    return True # pas notre tour, même si on a cliqué sur notre pièce
                    
                self.selected_piece = (row, col)
                self.render.edit_info_label("Select destination")
                self.render.needs_render = True
                return True
            elif cell[0] is not None:
                # clic sur une pièce adverse ou une case vide
                self.render.edit_info_label("Select your own piece")
                return True
            else:
                # clic sur une case vide
                self.render.edit_info_label(f"Player {self.round_turn + 1}'s turn") # ou message de statut réseau
                return True

        # cas 2: une pièce est déjà sélectionnée
        old_row, old_col = self.selected_piece

        # déselectionner si on clique sur la même pièce
        if (row, col) == (old_row, old_col):
            self.selected_piece = None
            self.render.edit_info_label(f"Player {self.round_turn + 1}'s turn")
            return True
            
        # déterminer les camps adverses en fonction du joueur
        current_player_index = self.player_number - 1 if self.is_network_game else self.round_turn
        # Pour joueur 0 (index) les camps adverses sont en bas (ligne 9), pour joueur 1 les camps sont en haut (ligne 0)
        opponent_camps = [(9, 0), (9, 9)] if current_player_index == 0 else [(0, 0), (0, 9)]
        
        # empêcher le déplacement vers les cases grises (sur le bord) sauf si c'est un camp adverse
        if is_edge and (row, col) not in opponent_camps:
            self.selected_piece = None
            self.render.edit_info_label("Cannot move to gray edge cells except opponent camps")
            return True

        # verification de la validité du mouvement
        if not available_move(self.board.board, old_row, old_col, row, col):
            self.selected_piece = None
            self.render.edit_info_label("Invalid move")
            return True
        
        # gestion de la capture
        capture_made = False
        if cell[0] is not None and cell[0] != current_player_index:
            if not self.first_turn:
                self.capture_piece(row, col)
                capture_made = True
            else:
                # pas de capture au premier tour
                self.selected_piece = None
                self.render.edit_info_label("No capture allowed on first turn")
                return True
        elif cell[0] is not None and cell[0] == current_player_index:
             # impossible de se déplacer sur une case alliée
             self.selected_piece = None
             self.render.edit_info_label("Cannot move to an occupied friendly cell")
             return True
        
        # execution du mouvement et vérification de victoire
        move_made = False
        is_win = False
        
        # envoi de l'action réseau si nécessaire
        if self.is_network_game:
            # appliquer le mouvement localement d'abord pour un feedback immédiat
            self.board.board[row][col][0] = self.board.board[old_row][old_col][0]
            self.board.board[old_row][old_col][0] = None
            current_player_who_moved = self.round_turn # stocker qui a joué
            self.selected_piece = None 

            # gérer la capture localement si nécessaire
            if capture_made:
                pass # Déjà géré ci-dessus visuellement

            # gérer le verrouillage de la pièce localement si nécessaire
            finish_line = 0 if current_player_who_moved == 1 else 9
            locked_piece_added = False
            if row == finish_line and self.is_camp_position(row, col):
                 if [row, col] not in self.locked_pieces and (row, col) not in self.locked_pieces:
                     self.locked_pieces.append([row, col]) 
                     locked_piece_added = True
                     Logger.game("Game", f"Local feedback: Piece locked at ({row}, {col}) for player {current_player_who_moved + 1}")

            # vérification de la victoire locale
            normalized_locked_pieces = [[x, y] for x, y in self.locked_pieces] if self.locked_pieces else []
            opponent_player_who_moved = 0 if current_player_who_moved == 1 else 1
            is_win = (self.check_win(current_player_who_moved) or self.check_win(opponent_player_who_moved))
            
            self.send_network_action({
                "from_row": old_row,
                "from_col": old_col,
                "to_row": row,
                "to_col": col,
                "capture_made": capture_made,
                "locked_pieces": normalized_locked_pieces
            })
            
            if is_win:
                winner = f"Player {current_player_who_moved + 1}"
                Logger.success("Game Katerenga", f"Game Over! {winner} wins! (Detected locally)")
                self.render.edit_info_label(f"Game Over! {winner} wins!")
                self.render.show_end_popup(f"{winner} WON THE GAME !")
                return False
                
            return True  # le jeu continue
        
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
            if is_win: 
                Logger.success("Game Katerenga", f"Game over! Player {self.round_turn + 1} wins!")
                self.render.show_end_popup(f"Player {self.round_turn + 1} wins!")
        else:
            # mouvement normal
            self.board.board[row][col][0] = self.board.board[old_row][old_col][0]
            self.board.board[old_row][old_col][0] = None
            self.selected_piece = None
            move_made = True
            is_win = self.check_win(self.round_turn)
            if is_win: 
                Logger.success("Game Katerenga", f"Game over! Player {self.round_turn + 1} wins!")
                self.render.show_end_popup(f"Player {self.round_turn + 1} wins!")

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
            save_game(self)
            self.render.needs_render = True

        if not is_win: # si le jeu n'est pas fini, on rafraîchit après toutes les opérations
             self.render.needs_render = True 

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
                if self.game_mode == "Bot":
                    winner_text = "BOT WON THE GAME !"
                else:
                    winner_text = f"PLAYER 1 WON THE GAME !"
                self.render.show_end_popup(winner_text)
                self.cleanup()
                return False
            else:
                if not self.render.running:
                    if self.game_mode == "Bot":
                        winner_text = "BOT WON THE GAME !"
                    else:
                        winner_text = f"PLAYER 2 WON THE GAME !"
                    self.render.show_end_popup(winner_text)
                    save_game(self)
                return False
        except Exception as e:
            Logger.error("Game", f"Error during bot play: {str(e)}")
            self.render.edit_info_label(f"Error during bot play: {str(e)}")
            self.round_turn = 0 # redonne la main au joueur en cas d'erreur
            self.render.edit_info_label(f"Player {self.round_turn + 1}'s turn")
            self.render.needs_render = True
            return False

    def get_board_state(self):
        """
        fonction : retourne l'état actuel complet du jeu pour la sauvegarde ou le réseau

        retour:
            dict: dictionnaire contenant l'état du plateau, le tour et le flag first_turn
        """
        state = {
            "board": [[cell[:] for cell in row] for row in self.board.board], # copie profonde
            "round_turn": self.round_turn,
            "first_turn": self.first_turn,
            "locked_pieces": list(self.locked_pieces) # copie de la liste
        }
        
        Logger.game("Game Katerenga", f"Generating game state: round_turn={state['round_turn']}, " 
                   f"player_number={self.player_number if hasattr(self, 'player_number') else 'N/A'}, "
                   f"locked_pieces={state['locked_pieces']}")
        return state

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