from typing import List, Optional
import copy
from src.utils.logger import Logger

class Board:
    """
    classe : gère le plateau de jeu et son initialisation
    structure du plateau :
        board : matrice 8x8 ou 10x10 selon le jeu
        chaque case : [joueur, type_case]
            joueur : 0 (joueur 1), 1 (joueur 2), None (case vide)
            type_case : 0-5 (voir render.py pour les couleurs)
    """
    def __init__(self, quadrants: List[List[List[List[Optional[int]]]]], game_number: int) -> None:
        """
        procédure : initialise le plateau avec les quadrants donnés
        params :
            quadrants - liste des 4 quadrants du plateau
            game_number - type de jeu (0: katerenga, 1: isolation, 2: congress)
        """
        Logger.board("Board", f"Initializing board for game {game_number}")
        self.quadrants: List[List[List[List[Optional[int]]]]] = quadrants
        self.game_number: int = game_number
        self.board: List[List[List[Optional[int]]]] = self.get_board()
        self.setup_board()
        Logger.success("Board", "Board initialized successfully")

    def setup_board(self) -> None:
        """
        procédure : place les pions initiaux selon le type de jeu
        """
        Logger.board("Board", f"Setting up board for game type {self.game_number}")
        match self.game_number:
            case 0:
                for i in range(8):
                    self.board[1][i+1][0] = 0
                    self.board[8][i+1][0] = 1

            case 1:
                pass

            case 2:
                positions = [
                    (0,1,1), (0,3,0), (0,4,1), (0,6,0),
                    (1,0,0), (1,7,1), (3,0,1), (3,7,0),
                    (4,0,0), (4,7,1), (6,0,1), (6,7,0),
                    (7,6,1), (7,4,0), (7,3,1), (7,1,0)
                ]
                for row, col, player in positions:
                    self.board[row][col][0] = player

        Logger.success("Board", "Board setup completed")

    def get_board(self) -> List[List[List[Optional[int]]]]:
        """
        fonction : crée le plateau en fusionnant les quadrants
        retour : plateau complet initialisé
        """
        Logger.board("Board", "Creating board from quadrants")
        board = [[[None, None] for _ in range(8)] for _ in range(8)]

        quadrant_positions = [
            (0, 0, 0), (0, 4, 1),
            (4, 0, 2), (4, 4, 3)
        ]

        for base_row, base_col, q in quadrant_positions:
            for i in range(4):
                for j in range(4):
                    board[base_row + i][base_col + j] = copy.deepcopy(self.quadrants[q][i][j])

        if self.game_number == 0:
            board = self._add_katerenga_camps(board)

        Logger.success("Board", "Board creation completed")
        return board

    def _add_katerenga_camps(self, board: List[List[List[Optional[int]]]]) -> List[List[List[Optional[int]]]]:
        """
        fonction : ajoute les camps pour le jeu katerenga
        params :
            board - plateau de base 8x8
        retour : plateau 10x10 avec camps
        """
        extended_board = [[[None, None] for _ in range(10)] for _ in range(10)]
        
        for i in range(8):
            for j in range(8):
                extended_board[i+1][j+1] = board[i][j]

        camps = [(0,0,4), (0,9,4), (9,0,5), (9,9,5)]
        for row, col, camp_type in camps:
            extended_board[row][col] = [None, camp_type]

        return extended_board
