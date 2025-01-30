from tkinter import messagebox
from src.board import Board
from src.render import Render
from src.captures import has_valid_move
from src.saves import save_game
from src.moves import available_move


class Game:
    def __init__(self, game_save, quadrants):
        self.game_save = game_save
        self.round_turn = 0  # 0 pour le joueur 1, 1 pour le joueur 2
        self.board = Board(quadrants, 2)
        self.render = Render(game=self)

    def load_game(self):
        self.render.root.mainloop()

    def check_connected_pieces(self, player):
        """
        Fonction qui vérifie si tous les pions d'un joueur sont connectés
        orthogonalement (non diagonalement) entre eux
        """
        start_pos = None # position de départ
        pieces = [] #liste des pieces
        for i in range(8): # pour chaque ligne 
            for j in range(8): # pour chaque colonne
                if self.board.board[i][j][0] == player: # si la case est occupée par le joueur
                    pieces.append((i, j)) # ajoute la position de la pièce à la liste des pièces
                    if start_pos is None: # si la position de départ n'est pas encore définie
                        start_pos = (i, j) # on définit la position de départ
        
        if not start_pos:
            return False
        
        # Utilise un parcours DFS pour trouver toutes les pièces connectées
        visited = set() # ensemble des pièces visitées
        stack = [start_pos] # pile de pièces à visiter
        
        while stack: # visite tout les pièces de la pile
            current = stack.pop() # retire la dernière pièce de la pile
            if current not in visited: # si la pièce n'a pas encore été visitée
                visited.add(current) # on l'ajoute à la liste des pièces visitées
                row, col = current # on récupère la position de la pièce
                
                # Vérifie les 4 directions orthogonales
                directions = [(0, 1), (1, 0), (0, -1), (-1, 0)] # directions possibles (droite, bas, gauche, haut)
                for dr, dc in directions: # pour chaque direction
                    new_row, new_col = row + dr, col + dc # nouvelle position de la pièce
                    if (0 <= new_row < 8 and 0 <= new_col < 8 and 
                        self.board.board[new_row][new_col][0] == player and 
                        (new_row, new_col) not in visited): # si la pièce est valide
                        stack.append((new_row, new_col)) # on l'ajoute à la pile
        
        # Si toutes les pièces sont visitées, elles sont connectées
        return len(visited) == len(pieces)

    def on_click(self, row, col):
        """
        Procédure appelée lorsqu'une cellule est cliquée dans le jeu Congress
        """
        if not hasattr(self, 'selected_piece'): # si l'attribut selected_piece n'existe pas
            self.selected_piece = None
        
        cell = self.board.board[row][col] # récupère la cellule cliquée

        # Premier clic - sélection d'une pièce
        if self.selected_piece is None: # si aucune pièce n'est sélectionnée
            if cell[0] is None or cell[0] != self.round_turn: # si la cellule est vide ou n'appartient pas au joueur
                self.render.edit_info_label("Select your own piece") # affiche un message d'erreur ("Sélectionnez votre propre pièce")
                return True 
            self.selected_piece = (row, col) # on sélectionne la pièce
            self.render.edit_info_label("Select destination") # affiche un message ("Selectionnez la destination")
            return True

        # Deuxième clic - déplacement
        old_row, old_col = self.selected_piece # récupère la position de la pièce sélectionnée
        
        # Vérifie si le mouvement est valide selon les règles de déplacement
        if not available_move(self.board.board, old_row, old_col, row, col): # si le mouvement n'est pas valide
            self.selected_piece = None # déselectionne la pièce
            self.render.edit_info_label("Invalid move") # affiche un message d'erreur ("Mouvement invalide")
            return True

        # Déplace la pièce
        self.board.board[row][col][0] = self.board.board[old_row][old_col][0] # déplace la pièce
        self.board.board[old_row][old_col][0] = None # vide la case de départ
        self.selected_piece = None # déselectionne la pièce

        # Vérifie si le joueur a gagné
        if self.check_connected_pieces(self.round_turn): # si le joueur a gagné
            winner = "Player 1" if self.round_turn == 0 else "Player 2" # détermine le gagnant
            self.render.edit_info_label(f"Game Over! {winner} wins!") # affiche un message de fin de partie avec le gagnant
            messagebox.showinfo("Game Over", f"{winner} has won!") # affiche une message box avec le gagnant
            self.render.root.destroy() # ferme la fenêtre de jeu
            return False

        # Change de joueur
        self.round_turn = 1 - self.round_turn 
        self.render.edit_info_label(f"Player {self.round_turn + 1}'s turn") # affiche qui doit jouer
        save_game(self)

        return True
