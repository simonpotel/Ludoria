import random
import math
import time
from typing import List, Tuple, Optional
from copy import deepcopy
from src.captures import is_threatened, has_valid_move
from src.utils.logger import Logger

class IsolationBot:
    def __init__(self, player_id, depth = 2):
        """
        fonction :Initialise le bot pour le jeu Isolation.
        
        params:
            player_id: L'identifiant du joueur (1 ou 2)
            depth: La profondeur maximale de l'algorithme min-max
        """
        self.player_id = player_id - 1
        self.opponent_id = 1 - self.player_id
        self.max_depth = depth
        self.max_time = 2.0 
        
    def get_valid_moves(self, board: List[List[List]]) -> List[Tuple[int, int]]:
        """
        fonction : Retourne toutes les positions valides où un pion peut être placé.
        
        params:
            board: L'état actuel du plateau
            
        retour :
            Liste des positions (row, col) valides
        """
        valid_moves = []
        for row in range(len(board)):
            for col in range(len(board[0])):
                if board[row][col][0] is None and not is_threatened(board, row, col, self.player_id):
                    valid_moves.append((row, col))
        return valid_moves
    
    def evaluate(self, board, player_turn):
        """
        fonction : Évalue l'état du plateau du point de vue du joueur actuel.
        
        params:
            board: L'état actuel du plateau
            player_turn: Le joueur dont c'est le tour (0 ou 1)
            
        retour :
            Score d'évaluation (plus élevé est meilleur pour le joueur)
        """
        my_moves = 0
        opponent_moves = 0
        
        # Échantillonnage: ne vérifier qu'un sous-ensemble des cases pour accélérer l'évaluation
        # Sur un plateau 8x8, vérifier une case sur deux est généralement suffisant
        for row in range(0, len(board), 2):
            for col in range(0, len(board[0]), 2):
                if board[row][col][0] is None:
                    if not is_threatened(board, row, col, self.player_id):
                        my_moves += 1
                    if not is_threatened(board, row, col, self.opponent_id):
                        opponent_moves += 1
        
        # dans le cas ou le joueur actuel a perdu (pas de coups possibles)
        # renvoie un score bas pour indiquer une défaite
        if player_turn == self.player_id and my_moves == 0:
            return -100
        
        # dans le cas ou le joueur actuel a gagné (adversaire sans coups possibles)
        # renvoie un score haut pour indiquer une victoire
        if player_turn == self.opponent_id and opponent_moves == 0:
            return 100
        
        # sinon, le score est basé sur la différence de coups possibles
        # un score positif indique que le bot a plus de coups possibles que l'adversaire
        return my_moves - opponent_moves
    
    def minimax(self, board, depth, alpha, beta, maximizing_player, player_turn, start_time):
        """
        fonction : Implémentation de l'algorithme minimax avec élagage alpha-beta et limite de temps.
        
        params:
            board: L'état actuel du plateau
            depth: La profondeur restante
            alpha: La valeur alpha pour l'élagage
            beta: La valeur beta pour l'élagage
            maximizing_player: True si c'est le tour du joueur maximisant
            player_turn: Le joueur dont c'est le tour (0 ou 1)
            start_time: Temps de départ pour la limite de temps
            
        retour :
            Tuple (score, meilleur_coup) où meilleur_coup est (row, col) ou None
        """
        # vérifie si le temps est écoulé
        if time.time() - start_time > self.max_time:
            return self.evaluate(board, player_turn), None
            
        valid_moves = self.get_valid_moves(board)
        
        # cas de base : profondeur atteinte ou fin de partie
        if depth == 0 or not valid_moves:
            return self.evaluate(board, player_turn), None
        
        # trier les coups pour améliorer l'élagage alpha-beta
        # pour le joueur maximisant, essayer d'abord les coups qui semblent bons
        # pour le joueur minimisant, essayer d'abord les coups qui semblent mauvais
        if len(valid_moves) > 3:  # ne pas trier si peu de coups
            # évaluation rapide pour le tri
            move_scores = []
            for move in valid_moves[:10]:  # limiter à 10 coups pour le tri
                row, col = move
                new_board = [[[cell[0], cell[1]] for cell in row] for row in board]  # copie plus légère
                new_board[row][col][0] = player_turn
                score = self.evaluate(new_board, player_turn)
                move_scores.append((move, score))
            
            # trier les coups
            if maximizing_player:
                move_scores.sort(key=lambda x: x[1], reverse=True)
            else:
                move_scores.sort(key=lambda x: x[1])
                
            # prendre les meilleurs coups
            sorted_moves = [move for move, _ in move_scores]
            valid_moves = sorted_moves[:5] + [m for m in valid_moves if m not in sorted_moves[:5]]
        
        if maximizing_player:
            max_eval = -math.inf
            best_move = None
            
            for move in valid_moves:
                if time.time() - start_time > self.max_time:
                    return max_eval, best_move
                    
                row, col = move
                new_board = [[[cell[0], cell[1]] for cell in row] for row in board]
                new_board[row][col][0] = player_turn
                
                eval_score, _ = self.minimax(new_board, depth - 1, alpha, beta, False, 1 - player_turn, start_time)
                
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
                
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
                    
            return max_eval, best_move
        else:
            min_eval = math.inf
            best_move = None
            
            for move in valid_moves:
                if time.time() - start_time > self.max_time:
                    return min_eval, best_move
                    
                row, col = move
                new_board = [[[cell[0], cell[1]] for cell in row] for row in board]
                new_board[row][col][0] = player_turn
                
                eval_score, _ = self.minimax(new_board, depth - 1, alpha, beta, True, 1 - player_turn, start_time)
                
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
                
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
                    
            return min_eval, best_move
    
    def get_move(self, board):
        """
        fonction : Détermine le meilleur coup à jouer.

        params:
            board: L'état actuel du plateau
            
        retour :
            Position (row, col) du meilleur coup
        """
        Logger.info("Bot", "Calculating best move...")
        start_time = time.time()
        
        valid_moves = self.get_valid_moves(board)
        
        if not valid_moves:
            Logger.error("Bot", "No valid moves available")
            raise ValueError("Aucun coup valide disponible")
        
        # si un seul coup est possible, le jouer directement
        if len(valid_moves) == 1:
            Logger.info("Bot", f"Only one move available: {valid_moves[0]}")
            return valid_moves[0]
            
        # pour les premiers coups, jouer de façon aléatoire pour varier le jeu
        empty_count = sum(1 for row in board for cell in row if cell[0] is None)
        if empty_count > 50:  # si plus de 50 cases vides, c'est le début de partie
            move = random.choice(valid_moves)
            Logger.info("Bot", f"Early game random move: {move}")
            return move
        
        # adapter la profondeur en fonction du nombre de coups possibles
        adaptive_depth = min(self.max_depth, 4 - len(valid_moves) // 10)
        adaptive_depth = max(1, adaptive_depth)  # au moins profondeur 1
        
        # utiliser minimax pour trouver le meilleur coup
        _, best_move = self.minimax(
            board, 
            adaptive_depth, 
            -math.inf, 
            math.inf, 
            True, 
            self.player_id,
            start_time
        )
        
        # si pour une raison quelconque minimax ne retourne pas de coup valide,
        # choisir un coup aléatoire parmi les coups valides
        if best_move is None:
            best_move = random.choice(valid_moves)
            Logger.warning("Bot", f"Fallback to random move: {best_move}")
        else:
            Logger.success("Bot", f"Found best move: {best_move} in {time.time() - start_time:.2f}s")
            
        return best_move