import random
from src.moves import available_move
import time

class CongressBot:
    def __init__(self, game):
        self.game = game
        self.player = 1  # Le bot est toujours le joueur 2 (indice 1)
        self.move_history = []  # Historique des derniers mouvements
        self.max_history = 5    # Nombre de mouvements à mémoriser

    def get_move(self):
        """
        Fonction qui détermine le meilleur coup à jouer
        Retourne: (from_pos, to_pos) où chaque position est un tuple (row, col)
        """
        # Liste de tous les coups possibles
        possible_moves = self._get_all_possible_moves()
        
        if not possible_moves:
            return None  # Aucun coup possible
            
        # Évaluer chaque coup possible
        scored_moves = []
        
        for from_pos, to_pos in possible_moves:
            # Simuler le coup
            score = self._evaluate_move(from_pos, to_pos)
            
            # Pénaliser les mouvements récemment joués pour éviter les boucles
            if (from_pos, to_pos) in self.move_history:
                score -= 100 * (self.move_history.count((from_pos, to_pos)))
            
            # Pénaliser les mouvements qui annulent le dernier mouvement
            if len(self.move_history) > 0:
                last_from, last_to = self.move_history[-1]
                if to_pos == last_from and from_pos == last_to:
                    score -= 200
            
            scored_moves.append((score, from_pos, to_pos))
        
        # Trier les mouvements par score
        scored_moves.sort(reverse=True)
        
        # Sélectionner un mouvement parmi les meilleurs avec un peu d'aléatoire
        # Prendre les 3 meilleurs mouvements et en choisir un au hasard
        top_n = min(3, len(scored_moves))
        if top_n > 0:
            # 70% de chance de choisir le meilleur mouvement, 30% de choisir parmi les autres bons mouvements
            if random.random() < 0.7 and scored_moves[0][0] > 0:
                best_score, best_from, best_to = scored_moves[0]
            else:
                best_score, best_from, best_to = random.choice(scored_moves[:top_n])
            
            # Ajouter le mouvement à l'historique
            self.move_history.append((best_from, best_to))
            if len(self.move_history) > self.max_history:
                self.move_history.pop(0)
                
            return (best_from, best_to)
        
        return None

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
                            # Éviter de vérifier le mouvement vers la même position
                            if row == to_row and col == to_col:
                                continue
                            try:
                                if available_move(board, row, col, to_row, to_col):
                                    moves.append(((row, col), (to_row, to_col)))
                            except ValueError:
                                # Ignorer les erreurs de range() avec step=0
                                continue
        
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
        
        # Vérifier que la destination est vide (pas de capture dans Congress)
        if board[to_row][to_col][0] is not None:
            return float('-inf')  # Mouvement invalide, retourner un score très négatif
        
        # Simuler le mouvement
        temp_board = [[cell[:] for cell in row] for row in board]
        temp_board[to_row][to_col][0] = temp_board[from_row][from_col][0]
        temp_board[from_row][from_col][0] = None
        
        # Bonus pour se rapprocher des autres pions (favoriser la connexion)
        adjacent_count = 0
        directions = [(0,1), (0,-1), (1,0), (-1,0)]
        for dr, dc in directions:
            new_row, new_col = to_row + dr, to_col + dc
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                if board[new_row][new_col][0] == self.player:
                    adjacent_count += 1
        
        # Bonus important pour la connexion avec d'autres pions
        score += adjacent_count * 50
        
        # Bonus pour les mouvements qui contribuent à former un bloc
        # Plus le nombre de pions connectés est grand, plus le score est élevé
        connected_count = self._count_connected_pieces(temp_board, to_row, to_col)
        score += connected_count * 30
        
        # Bonus pour se rapprocher du centre (stratégie générale)
        center_dist = abs(3.5 - to_row) + abs(3.5 - to_col)
        score += (8 - center_dist) * 2
        
        return score

    def _count_connected_pieces(self, board, row, col):
        """
        Compte le nombre de pièces alliées connectées à partir d'une position
        """
        if not (0 <= row < 8 and 0 <= col < 8) or board[row][col][0] != self.player:
            return 0
        
        visited = set()
        stack = [(row, col)]
        
        while stack:
            current = stack.pop()
            if current not in visited:
                visited.add(current)
                r, c = current
                
                directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
                for dr, dc in directions:
                    new_r, new_c = r + dr, c + dc
                    if (0 <= new_r < 8 and 0 <= new_c < 8 and 
                        board[new_r][new_c][0] == self.player and 
                        (new_r, new_c) not in visited):
                        stack.append((new_r, new_c))
        
        return len(visited)

    def _count_threatened_pieces(self, row, col):
        """
        Cette méthode n'est plus utilisée car il n'y a pas de capture dans Congress
        """
        return 0

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
        
        # Forcer le rendu du plateau avant de vérifier la victoire
        self.game.render.render_board()
        
        # Ajouter un petit délai pour que le joueur puisse voir le mouvement
        time.sleep(0.5)
        
        # Vérifier si le bot a gagné (tous les pions sont connectés)
        if self.game.check_connected_pieces(self.player):
            from tkinter import messagebox
            messagebox.showinfo("Game Over", "Bot wins!")
            return False
        
        return True
