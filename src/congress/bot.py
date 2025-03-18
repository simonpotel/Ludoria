import random
import time
from src.moves import available_move
from src.utils.logger import Logger

class CongressBot:
    def __init__(self, game):
        """
        constructeur : initialise une nouvelle instance de bot
        params :
            game - instance du jeu
        """
        self.game = game
        self.player = 1
        self.opponent = 0
        self.move_history = []
        self.max_history = 5
        self.max_depth = 2      # profondeur de recherche 
        Logger.bot("CongressBot", "Bot initialized")

    def get_move(self):
        """
        fonction : détermine le meilleur coup à jouer
        retour : (from_pos, to_pos) où chaque position est un tuple (row, col)
        """
        possible_moves = self._get_all_possible_moves()
        
        if not possible_moves:
            Logger.warning("CongressBot", "No valid moves found")
            return None
            
        scored_moves = []
        
        # créer une copie du plateau pour la simulation
        board = self.game.board.board
        
        Logger.bot("CongressBot", "Evaluating possible moves")
        
        for from_pos, to_pos in possible_moves:
            from_row, from_col = from_pos
            to_row, to_col = to_pos
            
            temp = board[to_row][to_col][0]
            
            board[to_row][to_col][0] = board[from_row][from_col][0]
            board[from_row][from_col][0] = None
            
            score = self._evaluate_position(board)
            
            board[from_row][from_col][0] = board[to_row][to_col][0]
            board[to_row][to_col][0] = temp
            
            # enleve des points si le coup a été joué récemment 
            if (from_pos, to_pos) in self.move_history:
                score -= 50 * (self.move_history.count((from_pos, to_pos)))
            
            # enleve des points si le coup annule le dernier coup
            if len(self.move_history) > 0:
                last_from, last_to = self.move_history[-1]
                if to_pos == last_from and from_pos == last_to:
                    score -= 100
            
            scored_moves.append((score, from_pos, to_pos))
        
        # remet les coups par ordre de score pour connaitre le meilleur coup
        scored_moves.sort(reverse=True)
        
        # choisi aléatoirement parmi les meilleurs coups 
        top_n = min(3, len(scored_moves))
        if top_n > 0:
            # 80% de chance de choisir le meilleur mouvement, 20% de choisir parmi les autres bons mouvements
            if random.random() < 0.8 and scored_moves[0][0] > 0:
                best_score, best_from, best_to = scored_moves[0]
            else:
                best_score, best_from, best_to = random.choice(scored_moves[:top_n])
            
            Logger.bot("CongressBot", f"Selected move from {best_from} to {best_to} with score {best_score}")
            
            # enregistrer le coup dans l'historique
            self.move_history.append((best_from, best_to))
            if len(self.move_history) > self.max_history:
                self.move_history.pop(0)
                
            return (best_from, best_to)
        
        return None
    
    def _evaluate_position(self, board):
        """
        fonction : Évalue la position actuelle du plateau de manière optimisée
        params : 
            board - plateau de jeu
        retourne : score de la position
        """
        if self._check_connected_pieces(board, self.player):
            return 1000
        
        if self._check_connected_pieces(board, self.opponent):
            return -1000
        
        bot_score = self._calculate_connectivity_score(board, self.player)
        opponent_score = self._calculate_connectivity_score(board, self.opponent)
        
        # Favorise la connectivité du bot et pénalise celle de l'adversaire
        return bot_score - opponent_score * 0.7
    
    def _calculate_connectivity_score(self, board, player):
        """
        fonction : calcule un score de connectivité optimisé
        params :
            board - plateau de jeu
            player - joueur
        retourne : score de connectivité
        """
        score = 0
        
        # Compter les paires adjacentes (méthode rapide)
        adjacent_pairs = 0
        for i in range(8):
            for j in range(8):
                if board[i][j][0] == player:
                    # Vérifier à droite
                    if j < 7 and board[i][j+1][0] == player:
                        adjacent_pairs += 1
                    # Vérifier en bas
                    if i < 7 and board[i+1][j][0] == player:
                        adjacent_pairs += 1
        
        score += adjacent_pairs * 20
        
        # bonus pour les pions proches du centre
        center_proximity = 0
        for i in range(8):
            for j in range(8):
                if board[i][j][0] == player:
                    # distance au centre (3.5, 3.5)
                    center_dist = abs(i - 3.5) + abs(j - 3.5)
                    center_proximity += (8 - center_dist)
        
        score += center_proximity * 2
        
        # bonus pour le plus grand groupe connecté
        largest_group = self._find_largest_group(board, player)
        score += largest_group * 30
        
        return score
    
    def _find_largest_group(self, board, player):
        """
        fonction : trouve la taille du plus grand groupe connecté de pions
        params :
            board - plateau de jeu
            player - joueur
        retourne : taille du plus grand groupe connecté
        """
        visited = set()
        max_size = 0
        
        for i in range(8):
            for j in range(8):
                if board[i][j][0] == player and (i, j) not in visited:
                    size = 0
                    stack = [(i, j)]
                    while stack:
                        r, c = stack.pop()
                        if (r, c) not in visited:
                            visited.add((r, c))
                            size += 1
                            
                            for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                                nr, nc = r + dr, c + dc
                                if (0 <= nr < 8 and 0 <= nc < 8 and 
                                    board[nr][nc][0] == player and 
                                    (nr, nc) not in visited):
                                    stack.append((nr, nc))
                    
                    max_size = max(max_size, size)
        
        return max_size
    
    def _check_connected_pieces(self, board, player):
        """
        fonction : vérifie si tous les pions d'un joueur sont connectés
        params :
            board - plateau de jeu
            player - joueur
        retourne : True si tous les pions sont connectés, False sinon
        """
        start_pos = None
        total_pieces = 0
        
        for i in range(8):
            for j in range(8):
                if board[i][j][0] == player:
                    total_pieces += 1
                    if start_pos is None:
                        start_pos = (i, j)
        
        if total_pieces == 0:
            return False
        
        visited = set()
        stack = [start_pos]
        
        while stack:
            r, c = stack.pop()
            if (r, c) not in visited:
                visited.add((r, c))
                
                for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    nr, nc = r + dr, c + dc
                    if (0 <= nr < 8 and 0 <= nc < 8 and 
                        board[nr][nc][0] == player and 
                        (nr, nc) not in visited):
                        stack.append((nr, nc))
        
        # si tous les pions sont visités, ils sont tous connectés
        return len(visited) == total_pieces
    
    def _get_all_possible_moves(self):
        """
        fonction : récupère tous les coups possibles pour le bot
        Version optimisée
        params :
            board - plateau de jeu
        retourne : liste de coups possibles
        """
        moves = []
        board = self.game.board.board
        
        for row in range(8):
            for col in range(8):
                if board[row][col][0] == self.player:
                    for to_row in range(8):
                        for to_col in range(8):
                            if row == to_row and col == to_col:
                                continue
                            if board[to_row][to_col][0] is not None:
                                continue
                            try:
                                if available_move(board, row, col, to_row, to_col):
                                    moves.append(((row, col), (to_row, to_col)))
                            except (ValueError, IndexError):
                                continue
        
        return moves

    def make_move(self):
        """
        fonction : exécute le meilleur coup trouvé
        params :
            board - plateau de jeu
        retour : True si un coup a été joué, False sinon
        """
        move = self.get_move()
        if move is None:
            Logger.warning("CongressBot", "No valid moves available")
            return False
            
        from_pos, to_pos = move
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        board = self.game.board.board
        board[to_row][to_col][0] = board[from_row][from_col][0]
        board[from_row][from_col][0] = None
        
        self.game.render.render_board()
        
        # ajout d'un petit délai pour que le joueur puisse voir le mouvement
        time.sleep(0.3)
        
        # vérifie si le bot a gagné (tous les pions sont connectés)
        if self.game.check_connected_pieces(self.player):
            from tkinter import messagebox
            Logger.success("CongressBot", "Bot won the game")
            messagebox.showinfo("Game Over", "Bot wins!")
            return False
        
        return True
