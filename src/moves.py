from src.utils.logger import Logger

def available_move(board, iRow, iCol, dRow, dCol):
    """
    fonction : vérifie si un déplacement est possible selon les règles du jeu
    paramètres :
        board - plateau de jeu (board.board)
        iRow - ligne de départ
        iCol - colonne de départ
        dRow - ligne d'arrivée
        dCol - colonne d'arrivée
    retourne : True si le déplacement est valide, False sinon
    """
    Logger.move("Moves", f"Checking move from ({iRow},{iCol}) to ({dRow},{dCol})")
    
    initial = board[iRow][iCol]
    initialCellColor = initial[1]
    destination = board[dRow][dCol]
    destinationPlayer = destination[0]
    
    # vérifie si la case de destination est occupée
    if destinationPlayer is not None:
        Logger.warning("Moves", f"Invalid move: destination cell ({dRow},{dCol}) is occupied")
        return False
        
    # vérifie le mouvement selon la couleur de la case de départ
    match initialCellColor:
        case 0:  # rouge (tour)
            if iRow != dRow and iCol != dCol:
                Logger.warning("Moves", "Invalid Rook move: must move in straight line")
                return False
                
            if iRow == dRow:  # déplacement horizontal
                step = 1 if dCol > iCol else -1
                for col in range(iCol + step, dCol, step):
                    if board[iRow][col][0] is not None:
                        Logger.warning("Moves", f"Invalid Rook move: path blocked at ({iRow},{col})")
                        return False
            else:  # déplacement vertical
                step = 1 if dRow > iRow else -1
                for row in range(iRow + step, dRow, step):
                    if board[row][iCol][0] is not None:
                        Logger.warning("Moves", f"Invalid Rook move: path blocked at ({row},{iCol})")
                        return False
            
            Logger.success("Moves", "Valid Rook move")
            return True
            
        case 1:  # vert (cavalier)
            valid = (abs(dRow - iRow) == 2 and abs(dCol - iCol) == 1) or \
                   (abs(dRow - iRow) == 1 and abs(dCol - iCol) == 2)
            if valid:
                Logger.success("Moves", "Valid Knight move")
            else:
                Logger.warning("Moves", "Invalid Knight move: must move in L-shape")
            return valid
            
        case 2:  # bleu (roi)
            valid = abs(dRow - iRow) <= 1 and abs(dCol - iCol) <= 1
            if valid:
                Logger.success("Moves", "Valid King move")
            else:
                Logger.warning("Moves", "Invalid King move: can only move one square in any direction")
            return valid
            
        case 3:  # jaune (fou)
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
            
    Logger.error("Moves", f"Invalid piece type: {initialCellColor}")
    return False  
                