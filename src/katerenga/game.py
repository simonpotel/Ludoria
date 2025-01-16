from tkinter import messagebox
from src.board import Board
from src.render import Render
from src.captures import has_valid_move
from src.saves import save_game
from src.katerenga.move_k import available_move


class Game:
    def __init__(self, game_save, quadrants):
        self.game_save = game_save
        self.board = Board(quadrants, 0)
        self.render = Render(game=self)
        self.round_turn = 0
        self.first_turn = True  # Empêche les captures au premier tour

    def load_game(self):
        self.render.root.mainloop()

    def check_win(self, player):
        """
        fonction qui va vérifier si le joueur à gagné
        """
        opponent = 1 - player
        # Définir les camps adverses et la ligne d'arrivée en fonction du joueur
        opponent_camps = [(9,0), (9,9)] if player == 0 else [(0,9), (0,0)]
        finish_line = 0 if player == 0 else 9
        
        # Vérifier si le joueur occupe les deux camps adverses
        camps_occupied = sum(1 for camp in opponent_camps 
                            if self.board.board[camp[0]][camp[1]][0] == player)
        
        if camps_occupied == 2:
            messagebox.showinfo("Victory!", f"Player {player + 1} wins by occupying both camps!")
            return True
        
        # Vérifier si l'adversaire a encore des pions qui peuvent bouger
        opponent_has_moves = False
        for row in range(10):  # Plateau 10x10 pour Katarenga
            for col in range(10):
                if self.board.board[row][col][0] == opponent:
                    # Vérifier si le pion peut se déplacer
                    for dest_row in range(10):
                        for dest_col in range(10):
                            if available_move(self.board.board, row, col, dest_row, dest_col):
                                opponent_has_moves = True
                                break
                    if opponent_has_moves:
                        break
            if opponent_has_moves:
                break
        
        # Si l'adversaire ne peut plus bouger, le joueur actuel gagne
        if not opponent_has_moves:
            messagebox.showinfo("Victory!", f"Player {player + 1} wins by blocking opponent!")
            return True
            
        return False

    def capture_piece(self, row, col):
       #fonction qui va permettre de capturer une pièce
        self.board.board[row][col][0] = None

    def on_click(self, row, col):
        """
        Fonction appelée lorsqu'une cellule est cliquée dans le jeu Katarenga
        """
        # Initialiser selected_piece si nécessaire
        if not hasattr(self, 'selected_piece'):
            self.selected_piece = None
        
        cell = self.board.board[row][col]
        print(f"Clicked on cell at row {row}, col {col}")
        print(f"Cell content: {cell}")

        # Premier clic - sélection d'une pièce
        if self.selected_piece is None:
            # Vérifie si la cellule contient une pièce du joueur actuel
            if cell[0] is not None and cell[0] == self.round_turn:
                self.selected_piece = (row, col)
                self.render.edit_info_label("Select destination")
                # Mettre en surbrillance la pièce sélectionnée
                self.render.render_board()
                return True
            else:
                self.render.edit_info_label("Select your own piece")
                return True

        # Deuxième clic - déplacement
        old_row, old_col = self.selected_piece

        # Vérifier si c'est un clic sur la même pièce
        if (row, col) == (old_row, old_col):
            self.selected_piece = None
            self.render.edit_info_label("Piece unselected")
            self.render.render_board()
            return True

        # Vérifie si le mouvement est valide selon les règles de déplacement
        if not available_move(self.board.board, old_row, old_col, row, col):
            self.selected_piece = None
            self.render.edit_info_label("Invalid move")
            return True

        # Gestion de la capture
        if cell[0] is not None and cell[0] != self.round_turn:
            if not self.first_turn:  # Pas de capture au premier tour
                self.capture_piece(row, col)
            else:
                self.selected_piece = None
                self.render.edit_info_label("No capture allowed on first turn")
                return True

        # Si le joueur a atteint la ligne d'arrivée
        finish_line = 0 if self.round_turn == 1 else 9
        if row == finish_line:
            # Si la destination est un camp adverse
            if (row == 0 and (col == 0 or col == 9)) or (row == 9 and (col == 0 or col == 9)):
                # Déplace la pièce
                self.board.board[row][col][0] = self.board.board[old_row][old_col][0]
                self.board.board[old_row][old_col][0] = None
                self.selected_piece = None

                # Vérifier la victoire
                if self.check_win(self.round_turn):
                    self.render.root.destroy()
                    return False

        # Déplacement normal
        else:
            # Déplace la pièce
            self.board.board[row][col][0] = self.board.board[old_row][old_col][0]
            self.board.board[old_row][old_col][0] = None

        self.selected_piece = None
        
        # Change de joueur et met à jour le statut du premier tour
        self.round_turn = 1 - self.round_turn
        if self.first_turn and self.round_turn == 0:
            self.first_turn = False
            
        self.render.edit_info_label(f"Player {self.round_turn + 1}'s turn")
        save_game(self)
        self.render.render_board()

        return True
