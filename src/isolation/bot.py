import random
from typing import List, Tuple, Optional
from src.captures import is_threatened

class IsolationBot:
    def __init__(self, player_id):
        """
        fonction : initialise le bot pour le jeu d'isolation.
        
        params :
            player_id - l'identifiant du joueur (1 ou 2)
        """
        self.player_id = player_id - 1
        self.opponent_id = 1 - self.player_id

    def get_valid_moves(self, board: List[List[List]], player) -> List[Tuple[int, int]]:
        """
        fonction : retourne tous les coups valides pour un joueur.
        
        params:
            board: l'état actuel du plateau
            player: l'identifiant du joueur (0 ou 1)
            
        retour :
            liste des positions (ligne, colonne) valides
        """
        valid_moves = []
        for row in range(len(board)):
            for column in range(len(board[0])):
                if board[row][column][0] is None and not is_threatened(board, row, column, 1 - player):
                    valid_moves.append((row, column))
        return valid_moves

    def get_move(self, board) -> Optional[Tuple[int, int]]:
        """
        fonctuon : détermine le meilleur coup à jouer.
        
        params :
            board: l'état actuel du plateau
            
        retour:
            Position (ligne, colonne) du meilleur coup
            
        raises:
            ValueError: si aucun coup n'est disponible
        """
        valid_moves = self.get_valid_moves(board, self.player_id)
        
        if not valid_moves:
            return None

        if len(valid_moves) == 1:
            return valid_moves[0]

        for move in valid_moves:
            row, column = move
            board[row][column][0] = self.player_id
            opponent_moves = self.get_valid_moves(board, self.opponent_id)
            board[row][column][0] = None
            
            if len(opponent_moves) == 0:
                return move

        return random.choice(valid_moves)