from typing import List, Optional
from src.moves import available_move
from src.utils.logger import Logger

def is_threatened(board: List[List[List[Optional[int]]]], row: int, col: int, current_player: int, check_all_pieces: bool = False) -> bool:
    """
    fonction : vérifie si une case est menacée par un pion adverse
    params :
        board - plateau de jeu
        row - ligne de la case à vérifier
        col - colonne de la case à vérifier
        current_player - joueur actuel (0 ou 1)
        check_all_pieces - si True, vérifie les menaces de tous les pions (y compris amis)
    retour : bool indiquant si la case est menacée
    """
    Logger.game("Captures", f"Checking if cell ({row},{col}) is threatened for player {current_player}")
    
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j][0] is not None:
                # si check_all_pieces est True, vérifie tous les pions
                # sinon, vérifie uniquement les pions adverses
                if check_all_pieces or board[i][j][0] != current_player:
                    if available_move(board, i, j, row, col):
                        Logger.warning("Captures", f"Cell ({row},{col}) is threatened by piece at ({i},{j})")
                        return True
                    
    Logger.success("Captures", f"Cell ({row},{col}) is not threatened")
    return False

def has_valid_move(board: List[List[List[Optional[int]]]], current_player: int, check_all_pieces: bool = False) -> bool:
    """
    fonction : vérifie s'il existe des cases non menacées pour placer un pion
    params :
        board - plateau de jeu
        current_player - joueur actuel (0 ou 1)
        check_all_pieces - si True, vérifie les menaces de tous les pions (comme pour Isolation)
    retour : bool indiquant si des coups sont possibles
    """
    Logger.game("Captures", f"Checking for valid moves for player {current_player}")
    
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j][0] is None and not is_threatened(board, i, j, current_player, check_all_pieces):
                Logger.success("Captures", f"Found valid move at ({i},{j}) for player {current_player}")
                return True
                
    Logger.warning("Captures", f"No valid moves found for player {current_player}")
    return False