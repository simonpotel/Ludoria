from src.moves import available_move
from src.utils.logger import Logger

def is_threatened(board, row, col, current_player):
    """
    fonction : vérifie si une case est menacée par un pion adverse
    params :
        board - plateau de jeu
        row - ligne de la case à vérifier
        col - colonne de la case à vérifier
        current_player - joueur actuel (0 ou 1)
    retour : bool indiquant si la case est menacée
    """
    Logger.game("Captures", f"Checking if cell ({row},{col}) is threatened for player {current_player}")
    
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j][0] is not None and board[i][j][0] != current_player:
                if available_move(board, i, j, row, col):
                    Logger.warning("Captures", f"Cell ({row},{col}) is threatened by piece at ({i},{j})")
                    return True
                    
    Logger.success("Captures", f"Cell ({row},{col}) is not threatened")
    return False

def has_valid_move(board, current_player):
    """
    fonction : vérifie s'il existe des cases non menacées pour placer un pion
    params :
        board - plateau de jeu
        current_player - joueur actuel (0 ou 1)
    retour : bool indiquant si des coups sont possibles
    """
    Logger.game("Captures", f"Checking for valid moves for player {current_player}")
    
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j][0] is None and not is_threatened(board, i, j, current_player):
                Logger.success("Captures", f"Found valid move at ({i},{j}) for player {current_player}")
                return True
                
    Logger.warning("Captures", f"No valid moves found for player {current_player}")
    return False