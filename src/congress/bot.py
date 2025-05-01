import random
import time
import math 
from src.moves import available_move
from src.utils.logger import Logger
from copy import deepcopy 

class CongressBot:
    def __init__(self, game):
        """
        constructeur : initialise une nouvelle instance de bot pour Congress

        params:
            game: instance du jeu Congress
        """
        self.game = game
        self.player = 1 # le bot est toujours le joueur 1 (blanc)
        self.opponent = 0 # l'adversaire est le joueur 0 (noir)
        self.move_history = [] # historique pour éviter répétitions simples
        self.max_history = 5 # taille max de l'historique
        self.max_depth = 2 # profondeur de recherche minimax (limitée pour performance)
        self.max_time = 3.0 # temps max de réflexion en secondes
        Logger.bot("CongressBot", "Bot initialized")

    def get_move(self):
        """
        fonction : détermine le meilleur coup à jouer en utilisant une évaluation simple
                  (pas de minimax pour l'instant pour la performance/simplicité)

        retour:
            tuple: ((from_row, from_col), (to_row, to_col)) ou None si aucun coup
        """
        start_time = time.time()
        possible_moves = self._get_all_possible_moves()
        
        if not possible_moves:
            Logger.warning("CongressBot", "No valid moves found")
            return None
            
        scored_moves = []
        board = self.game.board.board # référence au plateau actuel
        
        Logger.bot("CongressBot", f"Evaluating {len(possible_moves)} possible moves")
        
        # évalue chaque coup possible
        for from_pos, to_pos in possible_moves:
            # simule le coup sur une copie temporaire pour évaluation
            temp_board = deepcopy(board)
            from_row, from_col = from_pos
            to_row, to_col = to_pos
            
            # exécute le coup sur la copie
            temp_board[to_row][to_col][0] = temp_board[from_row][from_col][0]
            temp_board[from_row][from_col][0] = None
            
            # calcule le score de la position résultante
            score = self._evaluate_position(temp_board)
            
            # pénalise les coups répétitifs (aller-retour simple)
            if len(self.move_history) > 0:
                last_from, last_to = self.move_history[-1]
                if to_pos == last_from and from_pos == last_to:
                    score -= 150 # forte pénalité pour annuler le dernier coup
            
            # pénalise les coups joués récemment (pour éviter cycles simples)
            history_penalty = self.move_history.count((from_pos, to_pos))
            if history_penalty > 0:
                 score -= 50 * history_penalty
            
            scored_moves.append((score, from_pos, to_pos))
        
        # trie les coups par score décroissant
        scored_moves.sort(key=lambda x: x[0], reverse=True)
        
        # sélection du meilleur coup avec une part d\'aléatoire
        if not scored_moves:
             Logger.warning("CongressBot", "No moves left after scoring")
             return None

        top_n = min(3, len(scored_moves)) # considère les 3 meilleurs coups
        top_moves = scored_moves[:top_n]
        
        # probabilité plus élevée de choisir le meilleur coup absolu
        if random.random() < 0.8 or len(top_moves) == 1:
            best_score, best_from, best_to = top_moves[0]
        else:
            # sinon, choisir aléatoirement parmi les 3 meilleurs
            best_score, best_from, best_to = random.choice(top_moves)
            
        elapsed_time = time.time() - start_time
        Logger.bot("CongressBot", f"Selected move from {best_from} to {best_to} with score {best_score:.2f} in {elapsed_time:.2f}s")
        
        # enregistre le coup dans l'historique
        self.move_history.append((best_from, best_to))
        if len(self.move_history) > self.max_history:
            self.move_history.pop(0) # garde l'historique à taille fixe
            
        return (best_from, best_to)
    
    def _evaluate_position(self, board):
        """
        fonction : évalue la position actuelle du plateau pour le bot

        params:
            board: état du plateau à évaluer

        retour:
            float: score de la position (positif = avantage bot)
        """
        # vérification de victoire / défaite immédiate
        if self._check_connected_pieces(board, self.player):
            return math.inf # victoire
        if self._check_connected_pieces(board, self.opponent):
            return -math.inf # défaite
        
        # évaluation basée sur la connectivité et d'autres heuristiques
        bot_score = self._calculate_connectivity_score(board, self.player)
        opponent_score = self._calculate_connectivity_score(board, self.opponent)
        
        # score final = avantage de connectivité du bot - léger désavantage pour l'adversaire
        return bot_score - opponent_score * 0.8
    
    def _calculate_connectivity_score(self, board, player):
        """
        fonction : calcule un score basé sur la connectivité des pièces d'un joueur

        params:
            board: état du plateau
            player: identifiant du joueur (0 ou 1)

        retour:
            float: score de connectivité pour ce joueur
        """
        score = 0.0
        pieces = []
        for r in range(8):
            for c in range(8):
                if board[r][c][0] == player:
                    pieces.append((r, c))
        
        if not pieces:
            return 0.0

        # bonus pour les paires adjacentes (indicateur simple de regroupement)
        adjacent_pairs = 0
        for r, c in pieces:
            # vérifier voisin de droite
            if c < 7 and board[r][c+1][0] == player:
                adjacent_pairs += 1
            # vérifier voisin du bas
            if r < 7 and board[r+1][c][0] == player:
                adjacent_pairs += 1
        # normalisé par le nombre possible de paires max (approximatif)
        score += (adjacent_pairs / (len(pieces) * 2 if pieces else 1)) * 50
        
        # bonus pour la proximité au centre
        center_proximity = 0
        for r, c in pieces:
            # distance de Manhattan au centre (3.5, 3.5)
            dist = abs(r - 3.5) + abs(c - 3.5)
            # score inversement proportionnel à la distance (max = 7)
            center_proximity += (7 - dist)
        # normalisé par la proximité max possible
        score += (center_proximity / (len(pieces) * 7 if pieces else 1)) * 20
        
        # bonus pour la taille du plus grand groupe connecté
        largest_group_size = self._find_largest_group(board, player, pieces)
        # score proportionnel à la fraction des pièces dans le plus grand groupe
        if pieces:
            score += (largest_group_size / len(pieces)) * 100
        
        return score
    
    def _find_largest_group(self, board, player, pieces):
        """
        fonction : trouve la taille du plus grand groupe de pièces connectées orthogonalement

        params:
            board: état du plateau
            player: identifiant du joueur
            pieces: liste des coordonnées (r, c) des pièces du joueur

        retour:
            int: taille du plus grand groupe trouvé
        """
        if not pieces:
            return 0
            
        visited = set()
        max_size = 0
        
        for r_start, c_start in pieces:
            if (r_start, c_start) not in visited:
                current_group_size = 0
                stack = [(r_start, c_start)] # utiliser une pile pour DFS
                group_nodes = set() # suivi des nœuds dans ce groupe spécifique
                
                while stack:
                    r, c = stack.pop()
                    if (r, c) not in visited:
                        visited.add((r, c))
                        group_nodes.add((r,c))
                        current_group_size += 1
                        
                        # explorer les voisins orthogonaux
                        for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                            nr, nc = r + dr, c + dc
                            if (0 <= nr < 8 and 0 <= nc < 8 and
                                board[nr][nc][0] == player and
                                (nr, nc) not in visited):
                                stack.append((nr, nc))
                
                max_size = max(max_size, current_group_size)
        
        return max_size
    
    def _check_connected_pieces(self, board, player):
        """
        fonction : vérifie si *toutes* les pièces d'un joueur sont connectées en un seul groupe

        params:
            board: état du plateau
            player: identifiant du joueur

        retour:
            bool: True si toutes les pièces sont connectées, False sinon
        """
        pieces = []
        for i in range(8):
            for j in range(8):
                if board[i][j][0] == player:
                    pieces.append((i, j))
        
        total_pieces = len(pieces)
        if total_pieces <= 1: # 0 ou 1 pièce sont considérées comme connectées
            return True
        
        # utilise la recherche du plus grand groupe
        largest_group = self._find_largest_group(board, player, pieces)
        
        # si la taille du plus grand groupe égale le nombre total de pièces, elles sont toutes connectées
        return largest_group == total_pieces
    
    def _get_all_possible_moves(self):
        """
        fonction : récupère tous les coups valides possibles pour le bot (joueur 1)

        retour:
            list: liste de tuples ((from_row, from_col), (to_row, to_col))
        """
        moves = []
        board = self.game.board.board
        
        for r_from in range(8):
            for c_from in range(8):
                if board[r_from][c_from][0] == self.player: # si c'est une pièce du bot
                    # vérifier toutes les destinations possibles
                    for r_to in range(8):
                        for c_to in range(8):
                            # la destination doit être vide
                            if board[r_to][c_to][0] is None:
                                try:
                                    # utilise la fonction de validation du jeu
                                    if available_move(board, r_from, c_from, r_to, c_to):
                                        moves.append(((r_from, c_from), (r_to, c_to)))
                                except (ValueError, IndexError) as e:
                                    # ignorer les erreurs potentielles de available_move si coordonnées invalides (ne devrait pas arriver)
                                    Logger.warning("CongressBot", f"Error in available_move check: {e}")
                                    continue
        
        return moves

    def make_move(self):
        """
        procédure : choisit et exécute le meilleur coup trouvé sur le plateau de jeu réel

        retour:
            bool: True si un coup a été joué, False si aucun coup n'était possible ou si le bot a gagné
        """
        best_move = self.get_move()
        
        if best_move is None:
            Logger.warning("CongressBot", "No valid moves available to make")
            return False # indique qu'aucun coup n'a été joué
            
        (from_row, from_col), (to_row, to_col) = best_move
        
        # exécute le coup sur le plateau principal du jeu
        board = self.game.board.board
        board[to_row][to_col][0] = board[from_row][from_col][0]
        board[from_row][from_col][0] = None
        
        # note: le rendu est géré par la classe Game après le retour de make_move
        # note: la vérification de victoire est aussi gérée par la classe Game
        
        # ajout d'un petit délai artificiel pour que le joueur puisse voir le mouvement
        time.sleep(0.2)
        
        return True # indique qu'un coup a été joué
