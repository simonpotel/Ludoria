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
                
            if iRow != dRow:
                step = 1 if dRow > iRow else -1
                row = iRow + step
                
                # on vérifie si une case rouge est sur le chemin avant la destination
                while row != dRow:
                    # s'il y a une pièce sur le chemin
                    if board[row][iCol][0] is not None:
                        Logger.warning("Moves", f"Invalid Rook move: path blocked at ({row},{iCol})")
                        return False
                    
                    # si on rencontre une case rouge, on doit s'arrêter à cette case
                    if board[row][iCol][1] == 0:
                        Logger.warning("Moves", f"Invalid Rook move: must stop at the first red cell at ({row},{iCol})")
                        return False
                    
                    row += step
            
            if iCol != dCol:
                step = 1 if dCol > iCol else -1
                col = iCol + step
                
                # on vérifie si une case rouge est sur le chemin avant la destination
                while col != dCol:
                    # s'il y a une pièce sur le chemin
                    if board[iRow][col][0] is not None:
                        Logger.warning("Moves", f"Invalid Rook move: path blocked at ({iRow},{col})")
                        return False
                    
                    # si on rencontre une case rouge, on doit s'arrêter à cette case
                    if board[iRow][col][1] == 0:
                        Logger.warning("Moves", f"Invalid Rook move: must stop at the first red cell at ({iRow},{col})")
                        return False
                    
                    col += step
            
            Logger.success("Moves", "Valid Rook move")
            return True
            
        # case verte - déplacement comme un cavalier (Knight)
        case 1:
            valid = (abs(dRow - iRow) == 2 and abs(dCol - iCol) == 1) or \
                   (abs(dRow - iRow) == 1 and abs(dCol - iCol) == 2)
            Logger.success("Moves", "Valid Knight move") if valid else Logger.warning("Moves", "Invalid Knight move")
            return valid
            
        # case bleue - déplacement comme un roi (King)
        case 2:
            valid = abs(dRow - iRow) <= 1 and abs(dCol - iCol) <= 1
            Logger.success("Moves", "Valid King move") if valid else Logger.warning("Moves", "Invalid King move")
            return valid
            
        # case jaune - déplacement comme un fou (Bishop), arrêt à la première case jaune rencontrée
        case 3:
            if abs(dRow - iRow) != abs(dCol - iCol):
                Logger.warning("Moves", "Invalid Bishop move: must move diagonally")
                return False
                
            step_row = 1 if dRow > iRow else -1
            step_col = 1 if dCol > iCol else -1
            
            # parcourir toutes les cases diagonalement
            row, col = iRow + step_row, iCol + step_col
            
            # vérifier chaque case sur le chemin diagonal
            while row != dRow and col != dCol:
                # s'il y a une pièce sur le chemin
                if board[row][col][0] is not None:
                    Logger.warning("Moves", f"Invalid Bishop move: path blocked at ({row},{col})")
                    return False
                
                # si on rencontre une case jaune, on doit s'arrêter à cette case
                if board[row][col][1] == 3:
                    Logger.warning("Moves", f"Invalid Bishop move: must stop at the first yellow cell at ({row},{col})")
                    return False
                
                row += step_row
                col += step_col
            
            # si la destination est au-delà d'une case jaune déjà rencontrée, c'est invalide
            # vérifier si la destination elle-même est une case jaune
            if destination[1] == 3:
                # c'est valide de s'arrêter sur une case jaune
                Logger.success("Moves", "Valid Bishop move")
                return True
            
            # parcourir encore une fois pour vérifier qu'on ne dépasse pas de case jaune
            row, col = iRow + step_row, iCol + step_col
            while row != dRow and col != dCol:
                if board[row][col][1] == 3:
                    Logger.warning("Moves", f"Invalid Bishop move: must stop at the first yellow cell at ({row},{col})")
                    return False
                row += step_row
                col += step_col
            
            Logger.success("Moves", "Valid Bishop move")
            return True
            
    Logger.error("Moves", f"Invalid cell color: {initial[1]}")
    return False  
                