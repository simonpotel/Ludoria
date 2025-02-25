from tkinter import messagebox
from src.board import Board
from src.render import Render
from src.captures import has_valid_move
from src.saves import save_game
from src.moves import available_move


class Game:
    def __init__(self, game_save, quadrants):
        """
        constructeur : initialise une nouvelle partie de congress
        """
        self.game_save = game_save
        self.round_turn = 0  # 0 pour le joueur 1, 1 pour le joueur 2
        self.board = Board(quadrants, 2)
        self.render = Render(game=self)

    def load_game(self):
        """
        procédure : lance la boucle principale du jeu
        """
        self.render.root.mainloop()

    def check_connected_pieces(self, player):
        """
        fonction : vérifie si tous les pions d'un joueur sont connectés orthogonalement
        retourne : True si les pions sont connectés, False sinon
        """
        start_pos = None  # position de départ pour la recherche
        pieces = []  # liste des positions des pièces du joueur
        
        # recherche de toutes les pièces du joueur sur le plateau
        for i in range(8):
            for j in range(8):
                if self.board.board[i][j][0] == player:
                    pieces.append((i, j))
                    if start_pos is None:
                        start_pos = (i, j)
        
        if not start_pos:
            return False
        
        # utilise un parcours en profondeur (dfs) pour trouver toutes les pièces connectées
        visited = set()  # ensemble des positions visitées
        stack = [start_pos]  # pile pour le parcours dfs
        
        while stack:
            current = stack.pop()
            if current not in visited:
                visited.add(current)
                row, col = current
                
                # vérifie les 4 directions orthogonales possibles
                directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
                for dr, dc in directions:
                    new_row, new_col = row + dr, col + dc
                    if (0 <= new_row < 8 and 0 <= new_col < 8 and 
                        self.board.board[new_row][new_col][0] == player and 
                        (new_row, new_col) not in visited):
                        stack.append((new_row, new_col))
        
        return len(visited) == len(pieces)

    def on_click(self, row, col):
        """
        procédure : gère les clics sur le plateau de jeu
        paramètres : row (ligne), col (colonne) - coordonnées du clic
        retourne : True si le jeu continue, False si la partie est terminée
        """
        if not hasattr(self, 'selected_piece'):
            self.selected_piece = None
        
        cell = self.board.board[row][col]

        # gestion du premier clic - sélection d'une pièce
        if self.selected_piece is None:
            if cell[0] is None or cell[0] != self.round_turn:
                self.render.edit_info_label("Select your own piece")
                return True 
            self.selected_piece = (row, col)
            self.render.edit_info_label("Select destination")
            return True

        # gestion du second clic - déplacement de la pièce
        old_row, old_col = self.selected_piece
        
        # vérifie si le mouvement est valide
        if not available_move(self.board.board, old_row, old_col, row, col):
            self.selected_piece = None
            self.render.edit_info_label("Invalid move")
            return True

        # effectue le déplacement de la pièce
        self.board.board[row][col][0] = self.board.board[old_row][old_col][0]
        self.board.board[old_row][old_col][0] = None
        self.selected_piece = None

        # vérifie la condition de victoire
        if self.check_connected_pieces(self.round_turn):
            winner = "Player 1" if self.round_turn == 0 else "Player 2"
            self.render.edit_info_label(f"Game Over! {winner} wins!")
            messagebox.showinfo("Game Over", f"{winner} has won!")
            self.render.root.destroy()
            return False

        # passe au tour du joueur suivant
        self.round_turn = 1 - self.round_turn 
        self.render.edit_info_label(f"Player {self.round_turn + 1}'s turn")
        save_game(self)

        return True
