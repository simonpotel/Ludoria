from src.moves import available_move

def is_threatened(board, row, col, current_player):
    """
    fonction: vérifie si une case est menacée par un pion adverse
    
    board: plateau de jeu (board.board)
    row: ligne de la case à vérifier
    col: colonne de la case à vérifier
    current_player: index du joueur actuel (0 ou 1)
    return: True si la case est menacée par un pion adverse, False sinon
    """
    for i in range(len(board)):
        for j in range(len(board[i])):
            if (board[i][j][0] is not None and 
                board[i][j][0] != current_player):  
                if available_move(board, i, j, row, col):
                    return True
    return False

def has_valid_move(board, current_player):
    """
    fonction: vérifie s'il reste des cases non menacées où placer un pion pour le joueur actuel
    
    board: plateau de jeu (board.board)
    current_player: index du joueur actuel (0 ou 1)
    return: True s'il reste des coups possibles pour ce joueur, False sinon
    """
    for i in range(len(board)):
        for j in range(len(board[i])):
            if (board[i][j][0] is None and 
                not is_threatened(board, i, j, current_player)):
                return True
    return False