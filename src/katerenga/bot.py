import random
import time
import copy
from src.moves import available_move
from src.saves import save_game
from src.utils.logger import Logger

class KaterengaBot:
    def __init__(self, game):
        """
        constructeur : initialise une nouvelle instance de bot pour Katerenga

        params:
            game: instance du jeu Katerenga
        """
        self.game = game
        self.locked_pieces = game.locked_pieces
        Logger.bot("KaterengaBot", "Bot initialized")

    def make_move(self):
        """
        fonction : détermine et exécute le meilleur coup pour le bot

        retour:
            bool: True si un coup a été joué avec succès, False sinon (pas de coup possible ou victoire)
        """
        self.locked_pieces = self.game.locked_pieces
        
        board = self.game.board.board
        size = len(board)
        best_moves = []
        camp_moves = [] # mouvements directs vers un camp adverse
        
        Logger.bot("KaterengaBot", "Finding best move")
        
        # camps que le bot (joueur 1, pièces blanches) doit atteindre (ligne 0)
        bot_camps = [(row, col) for row, col in self.game.camps if row == 0]
        
        for i in range(size):
            for j in range(size):
                if board[i][j][0] == 1:  # pièce appartenant au bot
                    # ignore les pièces déjà arrivées dans un camp
                    if (i, j) in self.locked_pieces:
                        Logger.bot("KaterengaBot", f"Piece at ({i}, {j}) is locked in a camp, skipping")
                        continue
                    
                    # priorise les mouvements directs vers un camp adverse libre
                    for camp_row, camp_col in bot_camps:
                        if (board[camp_row][camp_col][0] is None or board[camp_row][camp_col][0] != 1) and \
                           available_move(board, i, j, camp_row, camp_col):
                            Logger.bot("KaterengaBot", f"Found possible camp move from ({i}, {j}) to ({camp_row}, {camp_col})")
                            camp_moves.append((i, j, camp_row, camp_col))
                    
                    # évalue les autres mouvements possibles
                    possible_moves = self._get_possible_moves(i, j)
                    for move_row, move_col in possible_moves:
                        captures = self._simulate_move_and_count_captures(i, j, (move_row, move_col))
                        # favorise les mouvements vers la ligne d'arrivée (ligne 0 pour le bot)
                        is_approach_finish_line = (i > 1 and move_row < i)
                        approach_value = 2 if move_row == 0 else (1 if is_approach_finish_line else 0)
                        # valeur totale = approche + captures + petit aléa pour départager
                        total_value = approach_value + captures
                        total_value += random.uniform(0, 0.1)
                        best_moves.append({
                            'value': total_value,
                            'move': (i, j, move_row, move_col)
                        })
        
        # sélection du mouvement final
        if camp_moves:
            # si un mouvement vers un camp est possible, le choisir aléatoirement parmi ceux-ci
            best_move = random.choice(camp_moves)
            Logger.bot("KaterengaBot", f"Selected camp move: {best_move}")
        elif best_moves:
            # sinon, trier les mouvements par valeur décroissante
            best_moves.sort(key=lambda x: x['value'], reverse=True)
            # choisir aléatoirement parmi le premier quart des meilleurs mouvements
            top_moves_count = max(1, len(best_moves) // 4)
            top_moves = best_moves[:top_moves_count]
            best_move = random.choice(top_moves)['move']
            Logger.bot("KaterengaBot", f"Selected move with value {best_moves[0]['value']}") # Log la valeur du meilleur mouvement
        else:
            Logger.warning("KaterengaBot", "No valid moves found")
            best_move = None
        
        # si aucun mouvement n'est possible, passer le tour
        if best_move is None:
            self.game.render.edit_info_label("Bot can't move")
            self.game.round_turn = 0
            self.game.render.edit_info_label(f"Player {self.game.round_turn + 1}'s turn")
            save_game(self.game)
            self.game.render.render_board()
            return False
        
        start_row, start_col, end_row, end_col = best_move
        
        Logger.bot("KaterengaBot", f"Executing move from ({start_row},{start_col}) to ({end_row},{end_col})")
        
        # vérification de validité (normalement inutile car déjà filtré, mais sécurité)
        if not self.is_camp_move(end_row, end_col, bot_camps) and not available_move(self.game.board.board, start_row, start_col, end_row, end_col):
            Logger.warning("KaterengaBot", "Invalid move attempted during execution")
            # gère le cas d'erreur sans crasher le jeu
            self.game.render.edit_info_label("Bot error: tried invalid move")
            self.game.round_turn = 0
            save_game(self.game)
            return False # indique un échec
        
        player = self.game.board.board[start_row][start_col][0]
        
        # vérifier capture invalide au premier tour
        is_capture = (self.game.board.board[end_row][end_col][0] is not None and
                      self.game.board.board[end_row][end_col][0] != player)
        if is_capture and self.game.first_turn:
            Logger.warning("KaterengaBot", "Attempted capture on first turn, re-evaluating")
            # si une capture est tentée au premier tour, on devrait relancer make_move (simplifié ici en passant le tour)
            self.game.render.edit_info_label("Bot attempted illegal first turn capture")
            self.game.round_turn = 0
            save_game(self.game)
            return False
        
        # execution du mouvement sur le plateau réel
        self.game.board.board[end_row][end_col][0] = player
        self.game.board.board[start_row][start_col][0] = None
        
        # mettre à jour l'état du jeu
        self.game.round_turn = 0 # c'est maintenant au tour du joueur 0
        self.game.first_turn = False # le premier tour est passé
        self.game.render.edit_info_label(f"Player {self.game.round_turn + 1}'s turn")
        
        time.sleep(0.3) # délai pour la visibilité du coup
        
        # vérifier si le bot a gagné
        if self.game.check_win(1): # bot est joueur 1
            Logger.success("KaterengaBot", "Bot won the game")
            # check_win met déjà à jour le label et running
            return False # le jeu est terminé
        
        save_game(self.game)
        self.game.render.render_board()
        return True # coup réussi

    def _simulate_move_and_count_captures(self, start_row, start_col, end):
        """
        fonction : simule un mouvement et évalue sa valeur (capture, approche, camp)

        params:
            start_row: ligne de départ de la pièce
            start_col: colonne de départ de la pièce
            end: tuple (ligne, colonne) de la destination

        retour:
            int: valeur du mouvement simulé (-1 si invalide, 0 si neutre, 1 si capture, 5 si vers camp)
        """
        end_row, end_col = end
        bot_camps = [(r, c) for r, c in self.game.camps if r == 0] # Camps du bot

        # valeur élevée pour les mouvements vers un camp libre
        if self.is_camp_move(end_row, end_col, bot_camps):
             if self.game.board.board[end_row][end_col][0] is None or self.game.board.board[end_row][end_col][0] != 1:
                 return 5
             else:
                 return -1 # camp déjà occupé par le bot

        # vérifie la validité du mouvement simulé
        if not available_move(self.game.board.board, start_row, start_col, end_row, end_col):
            return -1

        # simule le mouvement sur une copie du plateau
        temp_board = copy.deepcopy(self.game.board.board)
        player = temp_board[start_row][start_col][0]

        # vérifie si le mouvement résulte en une capture
        if temp_board[end_row][end_col][0] is not None and temp_board[end_row][end_col][0] != player:
            # ne pas autoriser la capture au premier tour
            if self.game.first_turn:
                return -1 # invalide
            return 1 # mouvement de capture
        
        # mouvement sans capture
        return 0

    def _get_possible_moves(self, row, col):
        """
        fonction : retourne tous les mouvements valides pour une pièce donnée

        params:
            row: ligne de la pièce
            col: colonne de la pièce

        retour:
            list: liste de tuples (dest_row, dest_col) représentant les mouvements possibles
        """
        # pièce bloquée dans un camp ne peut pas bouger
        if (row, col) in self.locked_pieces:
            return []
            
        board = self.game.board.board
        size = len(board)
        moves = []
        # ne devrait pas arriver, mais sécurité
        if board[row][col][0] != 1: # vérifie que c'est une pièce du bot
            return moves
            
        # itère sur toutes les cases de destination possibles
        for dest_row in range(size):
            for dest_col in range(size):
                # vérifie si la destination est sur le contour (case grise) mais pas dans un coin
                is_edge = (dest_row == 0 or dest_row == size-1 or dest_col == 0 or dest_col == size-1)
                is_mycorner = (dest_row == 0 and dest_col == 0) or (dest_row == 0 and dest_col == size-1)
                is_botcorner = (dest_row == size-1 and dest_col == 0) or (dest_row == size-1 and dest_col == size-1)
                
                # ignorer les cases grises (sur le bord mais pas dans les coins)
                if is_edge and not is_mycorner:
                    continue
                if is_botcorner:
                    continue
                
                # destination vide ou occupée par adversaire (capture possible hors 1er tour)
                if board[dest_row][dest_col][0] is None or board[dest_row][dest_col][0] == 0:
                    if available_move(board, row, col, dest_row, dest_col):
                        moves.append((dest_row, dest_col))
                        
        return moves

    def is_camp_move(self, row, col, camps):
        """
        fonction : vérifie si une position est un camp du bot

        params:
            row: ligne de la position
            col: colonne de la position
            camps: liste des coordonnées des camps du bot

        retour:
            bool: True si la position est un camp du bot, False sinon
        """
        return (row, col) in camps
    

