import random
import time
import copy
from src.moves import available_move
from src.saves import save_game
from src.utils.logger import Logger

class KaterengaBot:
    def __init__(self, game):
        """
        constructeur : initialise une nouvelle instance de bot
        params :
            game - instance du jeu
        """
        self.game = game
        self.locked_pieces = getattr(game, 'locked_pieces', [])
        Logger.bot("KaterengaBot", "Bot initialized")

    def make_move(self):
        """
        fonction : exécute le meilleur coup trouvé
        retourne : True si un coup a été joué, False sinon
        """
        board = self.game.board.board
        size = len(board)
        best_moves = []
        camp_moves = []
        
        Logger.bot("KaterengaBot", "Finding best move")
        
        for i in range(size):
            for j in range(size):
                if board[i][j][0] == 1:
                    if (i, j) in self.locked_pieces:
                        continue
                        
                    if i == 0:
                        if board[0][0][0] is None or board[0][0][0] != 1:
                            camp_moves.append((i, j, 0, 0))
                        elif board[0][9][0] is None or board[0][9][0] != 1:
                            camp_moves.append((i, j, 0, 9))
                    possible_moves = self._get_possible_moves(i, j)
                    for move in possible_moves:
                        captures = self._simulate_move_and_count_captures(i, j, move)
                        is_approach_finish_line = (i > 1 and move[0] < i)
                        approach_value = 2 if move[0] == 0 else (1 if is_approach_finish_line else 0)
                        total_value = approach_value + captures            
                        total_value += random.uniform(0, 0.1)
                        best_moves.append({
                            'value': total_value,
                            'move': (i, j, move[0], move[1])
                        })
        
        if camp_moves:
            best_move = random.choice(camp_moves)
            Logger.bot("KaterengaBot", f"Selected camp move: {best_move}")
        else:
            if best_moves:
                best_moves.sort(key=lambda x: x['value'], reverse=True)
                top_moves_count = max(1, len(best_moves) // 4)
                top_moves = best_moves[:top_moves_count]
                best_move = random.choice(top_moves)['move']
                Logger.bot("KaterengaBot", f"Selected move with value {top_moves[0]['value']}")
            else:
                Logger.warning("KaterengaBot", "No valid moves found")
                best_move = None
        
        if best_move is None:
            self.game.render.edit_info_label("Bot can't move")
            self.game.round_turn = 0
            self.game.render.edit_info_label(f"Player {self.game.round_turn + 1}'s turn")
            save_game(self.game)
            self.game.render.render_board()
            return False
        
        start_row, start_col, end_row, end_col = best_move
        is_camp_move = (start_row == 0 and end_row == 0 and (end_col == 0 or end_col == 9))
        
        if not is_camp_move and not available_move(self.game.board.board, start_row, start_col, end_row, end_col):
            Logger.warning("KaterengaBot", "Invalid move attempted")
            self.game.render.edit_info_label("Bot tried an invalid move")
            self.game.round_turn = 0
            self.game.render.edit_info_label(f"Player {self.game.round_turn + 1}'s turn")
            save_game(self.game)
            self.game.render.render_board()
            return False
        
        player = self.game.board.board[start_row][start_col][0]
        is_capture = (self.game.board.board[end_row][end_col][0] is not None and 
                      self.game.board.board[end_row][end_col][0] != player)
        if is_capture and self.game.first_turn:
            Logger.warning("KaterengaBot", "Attempted capture on first turn")
            self.game.render.edit_info_label("No capture allowed on first turn")
            self.game.round_turn = 0
            self.game.render.edit_info_label(f"Player {self.game.round_turn + 1}'s turn")
            save_game(self.game)
            self.game.render.render_board()
            return False
        
        self.game.board.board[end_row][end_col][0] = player     
        self.game.board.board[start_row][start_col][0] = None   
        
        self.game.round_turn = 0
        self.game.first_turn = False
        self.game.render.edit_info_label(f"Player {self.game.round_turn + 1}'s turn")
        
        time.sleep(0.3)
        
        if self.game.check_win(1):
            Logger.success("KaterengaBot", "Bot won the game")
            return False
        
        save_game(self.game)
        self.game.render.render_board()
        return True

    def _simulate_move_and_count_captures(self, start_row, start_col, end):
        """
        fonction : simule un mouvement et compte les pièces adverses qui seraient capturées
        paramètres : 
            start_row - ligne de départ
            start_col - colonne de départ
            end - position d'arrivée (row, col)
        retourne : nombre de pièces capturées ou -1 si le mouvement est invalide
        """
        if not available_move(self.game.board.board, start_row, start_col, end[0], end[1]):
            return -1
            
        temp_board = copy.deepcopy(self.game.board.board)
        player = temp_board[start_row][start_col][0]
        end_row, end_col = end

        if temp_board[end_row][end_col][0] is not None and temp_board[end_row][end_col][0] != player:
            temp_board[end_row][end_col][0] = player
            temp_board[start_row][start_col][0] = None
            return 1
        
        temp_board[end_row][end_col][0] = player
        temp_board[start_row][start_col][0] = None
        return 0

    def _get_possible_moves(self, row, col):
        """
        fonction : retourne les mouvements possibles pour une pièce
        paramètres :
            row - ligne de la pièce
            col - colonne de la pièce
        retourne : liste des positions possibles (row, col)
        """
        if (row, col) in self.locked_pieces:
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
        

