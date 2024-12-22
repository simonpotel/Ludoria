import copy

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
                et joueur (0 = joueur 1 et 1 = joueur 2)
                et case = 0 / 1 / 2 / 3 / 4 / 5 
                voir src.render.Render.QUADRANTS_CELLS_COLORS
    "board est donc une représentation du plateau de jeu avec les pions placés en 
    fonction du jeu formés avec les quadrants fusionnés"     

    """

    def __init__(self, quadrants, game_number):
        self.quadrants = copy.deepcopy(quadrants)
        self.game_number = game_number
        self.board = self.get_board()
        self.setup_board()

    def setup_board(self):
        """
        procédure : place les pions sur le plateau de jeu en fonction du jeu pour que la partie puisse démarrer
        """
        match self.game_number:
            case 0:  # katerenga
                for i in range(8):
                    self.board[1][i+1][0] = 0
                for i in range(8):
                    self.board[8][i+1][0] = 1

            case 1:  # congress
                pass  # à faire plus tard

            case 2:  # isolation
                pass  # pas de pions à l'initialisation

    def get_board(self):
        board = [[[None, None] for _ in range(8)] for _ in range(8)]

        for quadrant in range(4):
            # i & j = 4 car on a 4 quadrants de 4x4 cases
            for i in range(4):
                for j in range(4):
                    match quadrant:  # on gére la disposition car HAUT GAUCHE = Q0, HAUT DROITE = Q1, BAS GAUCHE = Q2, BAS DROITE = Q3
                        case 0:
                            board[i][j] = self.quadrants[quadrant][i][j]
                        case 1:
                            board[i][j + 4] = self.quadrants[quadrant][i][j]
                        case 2:
                            board[i + 4][j] = self.quadrants[quadrant][i][j]
                        case 3:
                            board[i + 4][j + 4] = self.quadrants[quadrant][i][j]

        if self.game_number == 0:  # katerenga
            # ajout d'une de colonne et ligne aux extrémités du plateau pour les camps
            for i in range(len(board)):
                board[i] = [[None, None]] + board[i] + [[None, None]]
            board = [[[None, None] for _ in range(
                10)]] + board + [[[None, None] for _ in range(10)]]

            board[0][0] = [None, 4]  # black camp 1 (player 1 (index 0))
            board[0][9] = [None, 4]  # black camp 2 (player 1 (index 0))
            board[9][0] = [None, 5]  # white camp 1 (player 2 (index 1))
            board[9][9] = [None, 5]  # white camp 2 (player 2 (index 1))
        return board
