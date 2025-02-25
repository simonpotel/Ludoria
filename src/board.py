import copy
from src.utils.logger import Logger

class Board:
    """
    class Board: représente le plateau de jeu
    en fonction du jeu (Katerega, Congress, Isolation), les pions sont placés différemment
    au démarrage.

    structure:
    quadrants: liste de 4 quadrants
        chaque quadrant est une liste de 4 lignes
            chaque ligne est une liste de 4 cases
                chaque case est une liste de 2 éléments:
                    (joueur, case)
                    et joueur (0 = joueur 1 et 1 = joueur 2)
                    et case = 0 / 1 / 2 / 3 / 4 / 5 
                    voir src.render.Render.QUADRANTS_CELLS_COLORS

    board: liste de 8/10 lignes
        chaque ligne est une liste de 8/10 cases
            chaque case est une liste de 2 éléments:
                (joueur, case)
                et joueur (0 = joueur 1 et 1 = joueur 2 ou None si la cellule n'est pas occupé)
                et case = 0 / 1 / 2 / 3 / 4 / 5 
                voir src.render.Render.QUADRANTS_CELLS_COLORS
    "board est donc une représentation du plateau de jeu avec les pions placés en 
    fonction du jeu formés avec les quadrants fusionnés"     

    """


    def __init__(self, quadrants, game_number):
        Logger.board("Board", f"Initializing board for game {game_number}")
        self.quadrants = quadrants
        self.game_number = game_number
        self.board = self.get_board()
        self.setup_board()
        Logger.success("Board", "Board initialized successfully")

    def setup_board(self):
        """
        procédure : place les pions sur le plateau de jeu en fonction du jeu pour que la partie puisse démarrer
        """
        Logger.board("Board", f"Setting up board for game type {self.game_number}")
        match self.game_number:
            case 0:  # katerenga
                Logger.board("Board", "Setting up Katerenga initial positions")
                for i in range(8):
                    self.board[1][i+1][0] = 0
                for i in range(8):
                    self.board[8][i+1][0] = 1
                Logger.success("Board", "Katerenga pieces placed successfully")

            case 1:  # isolation
                Logger.board("Board", "Setting up Isolation board (no initial pieces)")
                pass  # pas de pions à l'initialisation

            case 2:  # congress
                Logger.board("Board", "Setting up Congress initial positions")
                self.board[0][1][0] = 1
                self.board[0][3][0] = 0
                self.board[0][4][0] = 1
                self.board[0][6][0] = 0
                self.board[1][0][0] = 0
                self.board[1][7][0] = 1
                self.board[3][0][0] = 1
                self.board[3][7][0] = 0
                self.board[4][0][0] = 0
                self.board[4][7][0] = 1
                self.board[6][0][0] = 1
                self.board[6][7][0] = 0
                self.board[7][6][0] = 1
                self.board[7][4][0] = 0
                self.board[7][3][0] = 1
                self.board[7][1][0] = 0
                Logger.success("Board", "Congress pieces placed successfully")

    def get_board(self):
        Logger.board("Board", "Creating board from quadrants")
        board = [[[None, None] for _ in range(8)] for _ in range(8)]

        for quadrant in range(4):
            Logger.board("Board", f"Processing quadrant {quadrant}")
            # i & j = 4 car on a 4 quadrants de 4x4 cases
            for i in range(4):
                for j in range(4):
                    match quadrant:  # on gére la disposition car HAUT GAUCHE = Q0, HAUT DROITE = Q1, BAS GAUCHE = Q2, BAS DROITE = Q3
                        case 0:
                            board[i][j] = copy.deepcopy(self.quadrants[quadrant][i][j])
                        case 1:
                            board[i][j + 4] = copy.deepcopy(self.quadrants[quadrant][i][j])
                        case 2:
                            board[i + 4][j] = copy.deepcopy(self.quadrants[quadrant][i][j])
                        case 3:
                            board[i + 4][j + 4] = copy.deepcopy(self.quadrants[quadrant][i][j])

        if self.game_number == 0:  # katerenga
            Logger.board("Board", "Adding Katerenga camps to the board")
            # ajout d'une de colonne et ligne aux extrémités du plateau pour les camps
            for i in range(len(board)):
                board[i] = [[None, None]] + board[i] + [[None, None]]
            board = [[[None, None] for _ in range(
                10)]] + board + [[[None, None] for _ in range(10)]]

            board[0][0] = [None, 4]  # black camp 1 (player 1 (index 0))
            board[0][9] = [None, 4]  # black camp 2 (player 1 (index 0))
            board[9][0] = [None, 5]  # white camp 1 (player 2 (index 1))
            board[9][9] = [None, 5]  # white camp 2 (player 2 (index 1))
            Logger.success("Board", "Katerenga camps added successfully")
        
        Logger.success("Board", "Board creation completed")
        return board
