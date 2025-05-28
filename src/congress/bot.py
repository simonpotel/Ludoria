from typing import List, Tuple, Optional, Dict
import random
import time
import math 
from src.moves import available_move
from src.utils.logger import Logger
from copy import deepcopy 

class CongressBot:
    """
    classe : bot pour le jeu de Congress
    """
    def __init__(self, game):
        """
        procédure : initialise une nouvelle instance de bot pour Congress
        params :
            game - instance du jeu Congress
        """
        self.game = game
        self.player = 1 # le bot est toujours le joueur 1 (blanc) (index 1 mais joueur 2)
        self.opponent = 0 # l'adversaire est le joueur 0 (noir) (index 0 mais joueur 1)
        self.move_history = [] # historique pour éviter répétitions simples
        self.max_history = 5 # taille max de l'historique
        self.max_depth = 2 # profondeur de recherche minimax (limitée pour performance)
        self.max_time = 3.0 # temps max de réflexion en secondes
        Logger.bot("CongressBot", "Bot initialized")

    def get_move(self) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """
        fonction : détermine le meilleur coup à jouer en utilisant une évaluation simple
                  (pas de minimax pour l'instant pour la performance/simplicité)

        retour:
            tuple: ((from_row, from_col), (to_row, to_col)) ou None si aucun coup
        """
        start_time = time.time()
        possible_moves = self._get_all_possible_moves() # récupère tous les coups possibles
        
        if not possible_moves: # si aucun coup n'est possible
            Logger.warning("CongressBot", "No valid moves found")
            return None
            
        scored_moves = [] # liste pour stocker les coups évalués
        board = self.game.board.board 
        
        Logger.bot("CongressBot", f"Evaluating {len(possible_moves)} possible moves")
        
        # évalue chaque coup possible
        for from_pos, to_pos in possible_moves:
            # simule le coup sur une copie temporaire pour évaluation
            temp_board = deepcopy(board) # copie du tableau pour pouvoir le modifier sans affecter le tableau principal
            from_row, from_col = from_pos
            to_row, to_col = to_pos
            
            # exécute le coup sur la copie
            temp_board[to_row][to_col][0] = temp_board[from_row][from_col][0]
            temp_board[from_row][from_col][0] = None
            
            # calcule le score de la position résultante
            score = self._evaluate_position(temp_board)
            
            # pénalise les coups répétitifs (aller-retour simple)
            if len(self.move_history) > 0: # si l'historique n'est pas vide
                last_from, last_to = self.move_history[-1]
                if to_pos == last_from and from_pos == last_to:
                    score -= 150 # forte pénalité pour annuler le dernier coup
            
            # pénalise les coups joués récemment (pour éviter cycles simples)
            history_penalty = self.move_history.count((from_pos, to_pos)) # compte le nombre de fois que le coup a été joué
            if history_penalty > 0: # si le coup a été joué plusieurs fois
                 score -= 50 * history_penalty # pénalise le coup
            
            scored_moves.append((score, from_pos, to_pos)) # ajoute le coup à la liste des coups évalués
        
        # trie les coups par score décroissant
        scored_moves.sort(key=lambda x: x[0], reverse=True) # trie les coups par score décroissant
        
        # sélection du meilleur coup avec une part d\'aléatoire
        if not scored_moves: # si aucun coup n'est possible
             Logger.warning("CongressBot", "No moves left after scoring")
             return None 

        top_n = min(3, len(scored_moves)) # considère les 3 meilleurs coups
        top_moves = scored_moves[:top_n] # récupère les 3 meilleurs coups
        
        # probabilité plus élevée de choisir le meilleur coup absolu
        if random.random() < 0.8 or len(top_moves) == 1: # si la probabilité est inférieure à 0.8 ou si il n'y a qu'un seul coup
            best_score, best_from, best_to = top_moves[0] # choisit le meilleur coup
        else: # sinon, choisit aléatoirement parmi les 3 meilleurs coups
            # sinon, choisir aléatoirement parmi les 3 meilleurs
            best_score, best_from, best_to = random.choice(top_moves)
            
        elapsed_time = time.time() - start_time # temps d'exécution des calculs du bot
        Logger.bot("CongressBot", f"Selected move from {best_from} to {best_to} with score {best_score:.2f} in {elapsed_time:.2f}s")
        
        # enregistre le coup dans l'historique
        self.move_history.append((best_from, best_to)) # ajoute le coup à l'historique
        if len(self.move_history) > self.max_history: # si l'historique est trop long
            self.move_history.pop(0) # supprime le premier coup de l'historique
            
        return (best_from, best_to) # retourne le meilleur coup
    
    def _evaluate_position(self, board: List[List[List]]) -> float:
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
    
    def _calculate_connectivity_score(self, board: List[List[List]], player: int) -> float:
        """
        fonction : calcule un score basé sur la connectivité des pièces d'un joueur

        params:
            board: état du plateau
            player: identifiant du joueur (0 ou 1)

        retour:
            float: score de connectivité pour ce joueur
        """
        score = 0.0 # score de connectivité
        pieces = [] # liste des pièces du joueur
        for r in range(8): # parcourt toutes les cases du plateau
            for c in range(8):
                if board[r][c][0] == player:
                    pieces.append((r, c)) # ajoute la pièce à la liste
        
        if not pieces: # si aucune pièce n'est trouvée
            return 0.0 # retourne 0

        # bonus pour les paires adjacentes (indicateur simple de regroupement)
        adjacent_pairs = 0 # nombre de paires adjacentes
        for r, c in pieces: # parcourt toutes les pièces
            # vérifier voisin de droite
            if c < 7 and board[r][c+1][0] == player: # si le voisin de droite est le joueur
                adjacent_pairs += 1 # ajoute 1 au nombre de paires adjacentes
            # vérifier voisin du bas
            if r < 7 and board[r+1][c][0] == player: # si le voisin du bas est le joueur
                adjacent_pairs += 1 # ajoute 1 au nombre de paires adjacentes
        # normalisé par le nombre possible de paires max (approximatif)
        score += (adjacent_pairs / (len(pieces) * 2 if pieces else 1)) * 50 # ajoute le score de connectivité
        
        # bonus pour la proximité au centre
        center_proximity = 0 # score de proximité au centre
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
    
    def _find_largest_group(self, board: List[List[List]], player: int, pieces: List[Tuple[int, int]]) -> int:
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
            
        visited = set() # ensemble pour suivre les pièces déjà visitées
        max_size = 0 # taille du plus grand groupe trouvé
        
        for r_start, c_start in pieces: # parcourt toutes les pièces
            if (r_start, c_start) not in visited: # si la pièce n'a pas été visitée
                current_group_size = 0 # taille du groupe actuel
                stack = [(r_start, c_start)] # utiliser une pile pour DFS
                group_nodes = set() # suivi des nœuds dans ce groupe spécifique
                
                while stack:
                    r, c = stack.pop() # récupère la pièce à visiter
                    if (r, c) not in visited: # si la pièce n'a pas été visitée
                        visited.add((r, c)) # ajoute la pièce à l'ensemble des pièces visitées
                        group_nodes.add((r,c)) # ajoute la pièce au groupe
                        current_group_size += 1 # ajoute 1 à la taille du groupe
                        
                        # explorer les voisins orthogonaux
                        for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                            nr, nc = r + dr, c + dc # récupère les coordonnées du voisin
                            if (0 <= nr < 8 and 0 <= nc < 8 and # si le voisin est dans le plateau
                                board[nr][nc][0] == player and # si le voisin est le joueur
                                (nr, nc) not in visited): # si le voisin n'a pas été visité
                                stack.append((nr, nc)) # ajoute le voisin à la pile
                
                max_size = max(max_size, current_group_size) # met à jour la taille du plus grand groupe
        
        return max_size
    
    def _check_connected_pieces(self, board: List[List[List]], player: int) -> bool:
        """
        fonction : vérifie si *toutes* les pièces d'un joueur sont connectées en un seul groupe

        params:
            board: état du plateau
            player: identifiant du joueur

        retour:
            bool: True si toutes les pièces sont connectées, False sinon
        """
        pieces = [] # liste des pièces du joueur
        for i in range(8): # parcourt toutes les cases du plateau
            for j in range(8):
                if board[i][j][0] == player: # si la case est occupée par le joueur
                    pieces.append((i, j)) # ajoute la pièce à la liste
        
        total_pieces = len(pieces) # nombre total de pièces du joueur
        if total_pieces <= 1: # 0 ou 1 pièce sont considérées comme connectées
            return True 
        
        # utilise la recherche du plus grand groupe
        largest_group = self._find_largest_group(board, player, pieces)
        
        # si la taille du plus grand groupe égale le nombre total de pièces, elles sont toutes connectées
        return largest_group == total_pieces
    
    def _get_all_possible_moves(self) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
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

    def make_move(self) -> bool:
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
