from src.moves import available_move
from src.saves import save_game
import copy
import random
class Bot:

    def __init__(self, game):
        self.game = game

    def play(self):
        """Joue le meilleur coup possible pour le bot
        Stratégie de priorité:
        1. Mouvements vers la ligne adverse
        2. Mouvements qui capturent des pièces
        3. Autres mouvements valides"""
        board = self.game.board.board
        size = len(board)
        best_moves = []
        camp_moves = []
                
        for i in range(size):
            for j in range(size):
                if board[i][j][0] == 1:# Vérifie que la case contient une pièce du bot (joueur 1)
                    if (i, j) in self.game.locked_pieces:# Ignore les pièces verrouillées dans les camps
                        continue
                        
                    if i == 0:# Si la pièce est déjà sur la ligne adverse (ligne 0)
                        if board[0][0][0] is None or board[0][0][0] != 1:# Vérifie si un camp est disponible
                            camp_moves.append((i, j, 0, 0))  # Camp en haut à gauche
                        elif board[0][9][0] is None or board[0][9][0] != 1:
                            camp_moves.append((i, j, 0, 9))  # Camp en haut à droite
                    possible_moves = self.get_possible_moves(i, j)
                    for move in possible_moves:
                        captures = self.simulate_move_and_count_captures(i, j, move)
                        is_approach_finish_line = (i > 1 and move[0] < i)  # Se rapprocher de la ligne adverse
                        approach_value = 2 if move[0] == 0 else (1 if is_approach_finish_line else 0)# priorité à une pièce proche de la ligne adverse
                        total_value = approach_value + captures            
                        total_value += random.uniform(0, 0.1)# Ajout d'une valeur aléatoire pour éviter de toujours choisir le même pion
                        best_moves.append({
                            'value': total_value,
                            'move': (i, j, move[0], move[1])
                        })
        
        # Privilégier un mouvement vers un camp si disponible
        if camp_moves:
            best_move = random.choice(camp_moves)
        else:
            if best_moves:
                best_moves.sort(key=lambda x: x['value'], reverse=True) # Trier les coups par valeur décroissante
                top_moves_count = max(1, len(best_moves) // 4)
                top_moves = best_moves[:top_moves_count]
                best_move = random.choice(top_moves)['move']
            else:
                best_move = None
        
        if best_move is None:
            self.game.render.edit_info_label("Bot can't move")
            self.game.round_turn = 0
            self.game.render.edit_info_label(f"Player {self.game.round_turn + 1}'s turn")
            save_game(self.game)
            self.game.render.render_board()
            return
        
        # Effectuer le mouvement
        start_row, start_col, end_row, end_col = best_move
        is_camp_move = (start_row == 0 and end_row == 0 and (end_col == 0 or end_col == 9)) # Vérifie si c'est un mouvement vers un camp depuis la ligne adverse
        

        if not is_camp_move and not available_move(self.game.board.board, start_row, start_col, end_row, end_col):
            # Si le mouvement n'est pas valide, on passe le tour
            self.game.render.edit_info_label("Bot tried an invalid move")
            self.game.round_turn = 0
            self.game.render.edit_info_label(f"Player {self.game.round_turn + 1}'s turn")
            save_game(self.game)
            self.game.render.render_board()
            return
        
        player = self.game.board.board[start_row][start_col][0] #moise a jour du plateau de jeu
        is_capture = (self.game.board.board[end_row][end_col][0] is not None and 
                      self.game.board.board[end_row][end_col][0] != player) # Vérifie si la case d'arrivée contient une pièce adverse (capture)
        if is_capture and self.game.first_turn:
            self.game.render.edit_info_label("No capture allowed on first turn")
            self.game.round_turn = 0
            self.game.render.edit_info_label(f"Player {self.game.round_turn + 1}'s turn")
            save_game(self.game)
            self.game.render.render_board()
            return
        
        self.game.board.board[end_row][end_col][0] = player     
        self.game.board.board[start_row][start_col][0] = None   
        
        self.game.round_turn = 0
        self.game.first_turn = False
        self.game.render.edit_info_label(f"Player {self.game.round_turn + 1}'s turn")
        
        if self.game.check_win(1):
            return
        
        save_game(self.game)
        self.game.render.render_board()

    def simulate_move_and_count_captures(self, start_row, start_col, end):
        """Simule un mouvement et compte les pièces adverses qui seraient capturées"""

        if not available_move(self.game.board.board, start_row, start_col, end[0], end[1]):
            return -1  # Mouvement invalide
            
        temp_board = copy.deepcopy(self.game.board.board) # Copie du plateau pour la simulation
        player = temp_board[start_row][start_col][0]
        end_row, end_col = end

        if temp_board[end_row][end_col][0] is not None and temp_board[end_row][end_col][0] != player:
            temp_board[end_row][end_col][0] = player
            temp_board[start_row][start_col][0] = None
            return 1  # Une pièce adverse est capturée
        
        temp_board[end_row][end_col][0] = player
        temp_board[start_row][start_col][0] = None
        return 0  # Aucune pièce adverse n'est capturée

    def get_possible_moves(self, row, col):
        """Retourne les mouvements possibles pour une pièce"""
        
        if (row, col) in self.game.locked_pieces:
            return []  
        board = self.game.board.board
        size = len(board)
        moves = []
        if board[row][col][0] != 1:
            return moves
        for dest_row in range(size):
            for dest_col in range(size):
                if board[dest_row][dest_col][0] is None or board[dest_row][dest_col][0] != 1:
                    if available_move(board, row, col, dest_row, dest_col):
                        moves.append((dest_row, dest_col))
                        
        return moves
        

