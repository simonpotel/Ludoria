from src.utils.logger import Logger

def available_move(board, iRow, iCol, dRow, dCol):
    """
    fonction : vérifie la validité d'un déplacement selon les règles du jeu
    params :
        board - plateau de jeu
        iRow - ligne de départ
        iCol - colonne de départ
        dRow - ligne d'arrivée
        dCol - colonne d'arrivée
    retour : bool indiquant si le déplacement est valide
    """
    Logger.move("Moves", f"Checking move from ({iRow},{iCol}) to ({dRow},{dCol})")
    
    initial = board[iRow][iCol]
    destination = board[dRow][dCol]
    
    if destination[0] is not None and destination[0] == initial[0]:
        Logger.warning("Moves", f"Invalid move: destination cell ({dRow},{dCol}) is occupied by your own piece")
        return False
        
    match initial[1]:
        case 0:
            if iRow != dRow and iCol != dCol:
                Logger.warning("Moves", "Invalid Rook move: must move in straight line")
                return False
                
            step = 1 if dCol > iCol else -1 if iCol > dCol else 0
            for i in range(iRow + (0 if step else 1), dRow, 1 if dRow > iRow else -1):
                if board[i][iCol][0] is not None:
                    Logger.warning("Moves", f"Invalid Rook move: path blocked at ({i},{iCol})")
                    return False
                    
            for j in range(iCol + step, dCol, step):
                if board[iRow][j][0] is not None:
                    Logger.warning("Moves", f"Invalid Rook move: path blocked at ({iRow},{j})")
                    return False
            
            Logger.success("Moves", "Valid Rook move")
            return True
            
        case 1:
            valid = (abs(dRow - iRow) == 2 and abs(dCol - iCol) == 1) or \
                   (abs(dRow - iRow) == 1 and abs(dCol - iCol) == 2)
            Logger.success("Moves", "Valid Knight move") if valid else Logger.warning("Moves", "Invalid Knight move")
            return valid
            
        case 2:
            valid = abs(dRow - iRow) <= 1 and abs(dCol - iCol) <= 1
            Logger.success("Moves", "Valid King move") if valid else Logger.warning("Moves", "Invalid King move")
            return valid
            
        case 3:
            if abs(dRow - iRow) != abs(dCol - iCol):
                Logger.warning("Moves", "Invalid Bishop move: must move diagonally")
                return False
                
            step_row = 1 if dRow > iRow else -1
            step_col = 1 if dCol > iCol else -1
            row, col = iRow + step_row, iCol + step_col
            
            while row != dRow and col != dCol:
                if board[row][col][0] is not None:
                    Logger.warning("Moves", f"Invalid Bishop move: path blocked at ({row},{col})")
                    return False
                row += step_row
                col += step_col
                
            Logger.success("Moves", "Valid Bishop move")
            return True
            
    Logger.error("Moves", f"Invalid piece type: {initial[1]}")
    return False  
                