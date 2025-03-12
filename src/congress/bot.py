import random
from src.moves import available_move

class CongressBot:
    def __init__(self, game):
        self.game = game
        self.player = 1  # Le bot est toujours le joueur 2 (indice 1)

    def get_move(self):
        """
        Fonction qui détermine le meilleur coup à jouer
        Retourne: (from_pos, to_pos) où chaque position est un tuple (row, col)
        """
        # Liste de tous les coups possibles
        possible_moves = self._get_all_possible_moves()
        
        if not possible_moves:
            return None  # Aucun coup possible
            
        # Évaluer chaque coup possible et choisir le meilleur
        best_move = None
        best_score = float('-inf')
        
        for from_pos, to_pos in possible_moves:
            # Simuler le coup
            score = self._evaluate_move(from_pos, to_pos)
            
            if score > best_score:
                best_score = score
                best_move = (from_pos, to_pos)
        
        return best_move

    def _get_all_possible_moves(self):
        """
        Fonction qui récupère tous les coups possibles pour le bot
        Retourne: liste de tuples ((from_row, from_col), (to_row, to_col))
        """
        moves = []
        board = self.game.board.board
        
        # Parcourir toutes les pièces du bot
        for row in range(8):
            for col in range(8):
                if board[row][col][0] == self.player:
                    # Chercher toutes les destinations possibles
                    for to_row in range(8):
                        for to_col in range(8):
                            if available_move(board, row, col, to_row, to_col):
                                moves.append(((row, col), (to_row, to_col)))
        
        return moves

    def _evaluate_move(self, from_pos, to_pos):
        """
        Fonction qui évalue la qualité d'un coup
        Paramètres:
            from_pos: (row, col) position de départ
            to_pos: (row, col) position d'arrivée
        Retourne: score du coup
        """
        score = 0
        board = self.game.board.board
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # Bonus pour la capture d'une pièce adverse
        if board[to_row][to_col][0] == 1 - self.player:
            score += 100
            
        # Bonus pour se rapprocher du centre
        center_dist = abs(3.5 - to_row) + abs(3.5 - to_col)
        score += (8 - center_dist) * 5
        
        # Bonus pour protéger ses pièces
        if self._is_protected(to_row, to_col):
            score += 30
            
        # Malus pour s'éloigner de ses pièces
        if self._is_isolated(to_row, to_col):
            score -= 20
            
        # Bonus pour les mouvements qui menacent les pièces adverses
        threatened_pieces = self._count_threatened_pieces(to_row, to_col)
        score += threatened_pieces * 15
        
        return score

    def _is_protected(self, row, col):
        """
        Vérifie si une position est protégée par d'autres pièces alliées
        """
        board = self.game.board.board
        directions = [(0,1), (0,-1), (1,0), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)]
        
        protected = 0
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                if board[new_row][new_col][0] == self.player:
                    protected += 1
        
        return protected >= 2

    def _is_isolated(self, row, col):
        """
        Vérifie si une position est isolée des autres pièces alliées
        """
        board = self.game.board.board
        directions = [(0,1), (0,-1), (1,0), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)]
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                if board[new_row][new_col][0] == self.player:
                    return False
        return True

    def _count_threatened_pieces(self, row, col):
        """
        Compte le nombre de pièces adverses menacées depuis une position
        """
        board = self.game.board.board
        threatened = 0
        
        # Vérifier toutes les destinations possibles depuis cette position
        for to_row in range(8):
            for to_col in range(8):
                if available_move(board, row, col, to_row, to_col):
                    if board[to_row][to_col][0] == 1 - self.player:
                        threatened += 1
                        
        return threatened

    def make_move(self):
        """
        Exécute le meilleur coup trouvé
        Retourne: True si un coup a été joué, False sinon
        """
        move = self.get_move()
        if move is None:
            return False
            
        from_pos, to_pos = move
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # Effectuer le mouvement
        board = self.game.board.board
        board[to_row][to_col][0] = board[from_row][from_col][0]
        board[from_row][from_col][0] = None
        
        return True
