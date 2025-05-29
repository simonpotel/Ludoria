import random
from typing import List, Tuple, Optional, Dict, Set
import time
from src.captures import is_threatened, has_valid_move

class IsolationBot:
    """
    classe : bot pour le jeu d'Isolation
    """
    def __init__(self, player_id: int):
        """
        procédure : initialise le bot pour le jeu d'Isolation
        params :
            player_id - l'identifiant du joueur (1 ou 2)
        """
        self.player_id = player_id - 1 
        self.opponent_id = 1 - self.player_id
        self.time_limit = 1.0

    def get_valid_moves(self, board: List[List[List]]) -> List[Tuple[int, int]]:
        """
        fonction : trouve tous les coups valides pour un joueur
        params :
            board - plateau de jeu
        retour : liste des positions valides
        """
        valid_moves = []
        rows = len(board)
        cols = len(board[0]) if rows > 0 else 0
        
        for i in range(rows):
            for j in range(cols):
                if board[i][j][0] is None and not is_threatened(board, i, j, self.player_id, check_all_pieces=True):
                    valid_moves.append((i, j))
        
        return valid_moves

    def evaluate_move(self, board: List[List[List]], move: Tuple[int, int]) -> int:
        """
        fonction : évalue un coup en calculant combien de coups seront disponibles pour l'adversaire
        params :
            board - plateau de jeu
            move - coup à évaluer (row, col)
        retour : score du coup (plus petit = meilleur)
        """
        row, col = move
        board[row][col][0] = self.player_id
        
        opponent_moves = 0
        for i in range(len(board)):
            for j in range(len(board[0])):
                if board[i][j][0] is None and not is_threatened(board, i, j, self.opponent_id, check_all_pieces=True):
                    opponent_moves += 1
        
        board[row][col][0] = None
        
        return -opponent_moves

    def get_move(self, board: List[List[List]]) -> Optional[Tuple[int, int]]:
        """
        fonction : détermine le meilleur coup à jouer
        params :
            board - plateau de jeu
        retour : position (row, col) du meilleur coup, ou None s'il n'y a pas de coup valide
        """
        start_time = time.time()
        
        valid_moves = self.get_valid_moves(board)
        
        if not valid_moves:
            return None
        
        if len(valid_moves) == 1:
            return valid_moves[0]
        
        evaluated_moves = []
        for move in valid_moves:
            score = self.evaluate_move(board, move)
            evaluated_moves.append((move, score))
            
            if time.time() - start_time > self.time_limit:
                break
        
        evaluated_moves.sort(key=lambda x: x[1], reverse=True)
        
        top_moves = [move for move, _ in evaluated_moves[:min(3, len(evaluated_moves))]]
        return random.choice(top_moves)