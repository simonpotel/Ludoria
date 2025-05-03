import random
import math
import time
from typing import List, Tuple, Optional
from copy import deepcopy
from src.captures import is_threatened, has_valid_move
from src.utils.logger import Logger

class IsolationBot:
    def __init__(self, player_id, depth=2):
        """
        constructeur: initialise le bot pour le jeu Isolation.
        
        params:
            player_id: l'identifiant du joueur pour le bot (1 ou 2)
            depth: la profondeur maximale de recherche de l'algorithme minimax (défaut=2)
        """
        self.player_id = player_id - 1
        self.opponent_id = 1 - self.player_id
        self.max_depth = depth
        self.max_time = 2.0 # temps maximum de réflexion en secondes
        
    def get_valid_moves(self, board: List[List[List]], player) -> List[Tuple[int, int]]:
        """
        fonction : retourne toutes les positions valides où un pion peut être placé par un joueur.
        
        params:
            board: l'état actuel du plateau
            player: l'identifiant du joueur (0 ou 1) pour lequel chercher les coups
            
        retour:
            list: liste des positions (row, col) valides
        """
        valid_moves = []
        rows = len(board)
        cols = len(board[0])
        for r in range(rows):
            for c in range(cols):
                # une case est valide si elle est vide et non menacée par l'adversaire du joueur indiqué
                if board[r][c][0] is None and not is_threatened(board, r, c, 1 - player):
                    valid_moves.append((r, c))
        return valid_moves
    
    def evaluate(self, board, player_turn):
        """
        fonction : évalue l'état actuel du plateau du point de vue du bot.
        
        params:
            board: l'état actuel du plateau
            player_turn: le joueur dont c'est actuellement le tour (0 ou 1)
            
        retour :
            int: score d'évaluation (positif si avantageux pour le bot, négatif sinon)
        """
        my_valid_moves = self.get_valid_moves(board, self.player_id)
        opponent_valid_moves = self.get_valid_moves(board, self.opponent_id)
        my_moves_count = len(my_valid_moves)
        opponent_moves_count = len(opponent_valid_moves)
        
        # cas de fin de partie : vérifier si le joueur actuel (player_turn) a perdu
        if player_turn == self.player_id and my_moves_count == 0:
            return -math.inf # défaite immédiate pour le bot
        if player_turn == self.opponent_id and opponent_moves_count == 0:
            return math.inf # victoire immédiate pour le bot
        
        # heuristique simple : différence du nombre de coups possibles
        # une meilleure heuristique pourrait considérer le contrôle de zone, etc.
        score = my_moves_count - opponent_moves_count
        
        # léger bonus/malus si c'est notre tour et on a plus/moins de coups
        if player_turn == self.player_id:
            score += 0.1 * (my_moves_count - opponent_moves_count)
        else:
            score -= 0.1 * (opponent_moves_count - my_moves_count)
        
        return score
    
    def minimax(self, board, depth, alpha, beta, maximizing_player, current_player_turn, start_time):
        """
        fonction : implémente l'algorithme minimax avec élagage alpha-beta et limite de temps.
        
        params:
            board: l'état actuel du plateau
            depth: la profondeur de recherche restante
            alpha: la meilleure valeur trouvée jusqu'à présent pour le joueur maximisant
            beta: la meilleure valeur trouvée jusqu'à présent pour le joueur minimisant
            maximizing_player: bool indiquant si le nœud actuel maximise (True) ou minimise (False)
            current_player_turn: l'identifiant du joueur (0 ou 1) dont c'est le tour dans cet état simulé
            start_time: le timestamp du début de l'appel à get_move pour vérifier le timeout
            
        retour:
            tuple: (score_optimal, meilleur_coup) où meilleur_coup est (row, col) ou None
        """
        # vérifie le dépassement de temps
        if time.time() - start_time > self.max_time:
            # si le temps est écoulé, retourne l'évaluation de l'état actuel sans explorer plus loin
            return self.evaluate(board, current_player_turn), None
            
        possible_moves = self.get_valid_moves(board, current_player_turn)
        
        # condition d'arrêt : profondeur max atteinte ou fin de partie (aucun coup possible)
        if depth == 0 or not possible_moves:
            return self.evaluate(board, current_player_turn), None
        
        # optimisation : trier les coups pour améliorer l'élagage alpha-beta
        # idée : explorer d'abord les coups qui semblent les meilleurs (selon une évaluation rapide)
        if depth >= 2 and len(possible_moves) > 5: # trier seulement si assez de coups et de profondeur
            move_scores = []
            for move in possible_moves:
                r, c = move
                # simulation rapide sans copie profonde complète
                original_value = board[r][c][0]
                board[r][c][0] = current_player_turn
                score = self.evaluate(board, 1 - current_player_turn) # évalue pour l'adversaire après ce coup
                board[r][c][0] = original_value # annule la simulation
                move_scores.append((move, score))
            
            # trier : maximisant veut les scores bas (mauvais pour l'adversaire), minimisant les scores hauts
            move_scores.sort(key=lambda x: x[1], reverse=not maximizing_player)
            sorted_moves = [move for move, score in move_scores]
        else:
            sorted_moves = possible_moves # pas de tri
            random.shuffle(sorted_moves) # introduire un peu d'aléatoire si pas de tri
        
        best_move_found = None
        
        if maximizing_player:
            max_eval = -math.inf
            for move in sorted_moves:
                r, c = move
                # simuler le coup sur une copie
                new_board = deepcopy(board)
                new_board[r][c][0] = current_player_turn
                
                # appel récursif pour le joueur adverse (minimisant)
                eval_score, _ = self.minimax(new_board, depth - 1, alpha, beta, False, 1 - current_player_turn, start_time)
                
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move_found = move
                
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break # élagage beta
                    
            return max_eval, best_move_found
        else: # minimizing_player
            min_eval = math.inf
            for move in sorted_moves:
                r, c = move
                # simuler le coup sur une copie
                new_board = deepcopy(board)
                new_board[r][c][0] = current_player_turn
                
                # appel récursif pour le joueur adverse (maximisant)
                eval_score, _ = self.minimax(new_board, depth - 1, alpha, beta, True, 1 - current_player_turn, start_time)
                
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move_found = move
                
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break # élagage alpha
                    
            return min_eval, best_move_found
    
    def get_move(self, board):
        """
        fonction : détermine le meilleur coup à jouer pour le bot en utilisant minimax.
        
        params:
            board: l'état actuel du plateau de jeu
            
        retour:
            tuple: position (row, col) du meilleur coup trouvé, ou lève une exception si aucun coup n'est possible.
        """
        Logger.info("Bot", f"Calculating best move for player {self.player_id + 1} with depth {self.max_depth}")
        start_time = time.time()
        
        current_valid_moves = self.get_valid_moves(board, self.player_id)
        
        if not current_valid_moves:
            Logger.error("Bot", "No valid moves available")
            raise ValueError("No valid moves available for bot")
        
        # si un seul coup est possible, le jouer directement
        if len(current_valid_moves) == 1:
            move = current_valid_moves[0]
            Logger.info("Bot", f"Only one move available: {move}")
            return move
            
        # cas spécial pour les tout premiers coups : jouer aléatoirement pour varier les ouvertures
        empty_count = sum(1 for row in board for cell in row if cell[0] is None)
        board_size = len(board) * len(board[0])
        if empty_count > board_size * 0.8: # si plus de 80% du plateau est vide
            move = random.choice(current_valid_moves)
            Logger.info("Bot", f"Early game random move: {move}")
            return move
        
        # utiliser minimax pour trouver le meilleur coup
        # on commence par maximiser car c'est le tour du bot
        score, best_move = self.minimax(
            board,
            self.max_depth, 
            -math.inf, 
            math.inf, 
            True, # le bot maximise son score
            self.player_id, # joueur actuel
            start_time
        )
        
        elapsed_time = time.time() - start_time
        
        # fallback : si minimax ne retourne pas de coup (timeout profond?), choisir un coup aléatoire
        if best_move is None:
            best_move = random.choice(current_valid_moves)
            Logger.warning("Bot", f"Minimax did not return a move (score: {score}, time: {elapsed_time:.2f}s). Fallback to random: {best_move}")
        elif best_move not in current_valid_moves:
             best_move = random.choice(current_valid_moves)
             Logger.warning("Bot", f"Minimax returned an invalid move {best_move} (score: {score}, time: {elapsed_time:.2f}s). Fallback to random: {best_move}")
        else:
            Logger.success("Bot", f"Found best move: {best_move} with score {score} in {elapsed_time:.2f}s")
            
        return best_move