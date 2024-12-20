class Board:
    def __init__(self, quadrants, game_number):
        self.quadrants = quadrants
        self.game_number = game_number
        self.initialize_board()

        if game_number == 0:  # Seulement pour Katarenga
            self.has_outer_cells = True
            self.outer_cells = self.initialize_outer_cells()
        else:
            self.has_outer_cells = False

    def initialize_board(self):  # prépose les pions sur le plateau
        match self.game_number:
            case 0:  # katerenga
                for i in range(4):
                    self.quadrants[0][0][i][0] = 0
                    self.quadrants[1][0][i][0] = 0
                    self.quadrants[2][3][i][0] = 1
                    self.quadrants[3][3][i][0] = 1

            case 1:  # congress
                self.quadrants[0][0][1][0] = 0
                self.quadrants[0][0][3][0] = 1
                self.quadrants[0][1][0][0] = 1
                self.quadrants[0][3][0][0] = 0

                self.quadrants[1][0][0][0] = 0
                self.quadrants[1][0][2][0] = 1
                self.quadrants[1][1][3][0] = 0
                self.quadrants[1][3][3][0] = 1

                self.quadrants[2][0][0][0] = 1
                self.quadrants[2][2][0][0] = 0
                self.quadrants[2][3][1][0] = 1
                self.quadrants[2][3][3][0] = 0

                self.quadrants[3][0][3][0] = 0
                self.quadrants[3][2][3][0] = 1
                self.quadrants[3][3][0][0] = 1
                self.quadrants[3][3][2][0] = 0

    def initialize_outer_cells(self):
        """
        Initialise les cases externes du plateau pour Katarenga
        """
        # Création d'une grille 10x10 pour les cases externes (8x8 plateau + 1 case de chaque côté)
        outer_cells = [[None for _ in range(10)] for _ in range(10)]

        # Marquer les cases camps dans les coins (4 pour la couleur grise)
        outer_cells[0][0] = [None, 4]  # Coin supérieur gauche
        outer_cells[0][9] = [None, 4]  # Coin supérieur droit
        outer_cells[9][0] = [None, 4]  # Coin inférieur gauche
        outer_cells[9][9] = [None, 4]  # Coin inférieur droit

        return outer_cells
