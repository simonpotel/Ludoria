def available_move(board, iRow, iCol, dRow, dCol):
    """
    fonction: vérifie si un déplacement est possible selon les règles du jeu du katerenga
    """
    initial = board[iRow][iCol]
    initialPlayer = initial[0]
    initialCellColor = initial[1]
    destination = board[dRow][dCol]
    destinationPlayer = destination[0]
    
    # Permettre la capture des pièces adverses
    if destinationPlayer is not None and destinationPlayer == initialPlayer:  
        return False
        
    match initialCellColor:
        case 0:  # rouge (Tour)
            if iRow != dRow and iCol != dCol:
                return False
                
            if iRow == dRow:
                step = 1 if dCol > iCol else -1
                for col in range(iCol + step, dCol, step):
                    if board[iRow][col][0] is not None:
                        return False
            else:
                step = 1 if dRow > iRow else -1
                for row in range(iRow + step, dRow, step):
                    if board[row][iCol][0] is not None:
                        return False
            return True
            
        case 1:  # vert (Cavalier)
            return (abs(dRow - iRow) == 2 and abs(dCol - iCol) == 1) or \
                   (abs(dRow - iRow) == 1 and abs(dCol - iCol) == 2) # mouvement en L
            
        case 2:  # bleu (Roi)
            return abs(dRow - iRow) <= 1 and abs(dCol - iCol) <= 1 # 1 case dans n'importe quelle direction
            
        case 3:  # jaune (Fou)
            if abs(dRow - iRow) != abs(dCol - iCol): # diagonale
                return False
                
            step_row = 1 if dRow > iRow else -1
            step_col = 1 if dCol > iCol else -1
            row, col = iRow + step_row, iCol + step_col
            
            while row != dRow and col != dCol: # chaque case du chemin doit être vide
                if board[row][col][0] is not None:  # case occupée
                    return False # déplacement invalide
                row += step_row
                col += step_col
                
            return True
            
    return False