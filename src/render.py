import tkinter as tk


class Render:
    QUADRANTS_CELLS_COLORS = {0: 'red', 1: 'green', 2: 'blue', 3: 'yellow'}

    def __init__(self, game):
        self.game = game
        self.root = tk.Tk()  
        self.root.title("KATARENGA & Co") 
        self.root.geometry("800x800")  
        self.canvas = tk.Canvas(self.root, width=800, height=800)
        self.canvas.pack()
        self.render_board()

    def render_board(self):
        """
        Méthode qui rend le plateau de jeu dans le canvas en fonction des quadrants du plateau de jeu.
        """
        self.canvas.delete("all")  # efface tout ce qui est dans le canvas
        quadrant_size = 200  # taille d'un quadrant
        cell_size = quadrant_size // 4  # taille d'une cellule dans un quadrant

        # pour chaque quadrant du plateau de jeu
        for i, quadrant in enumerate(self.game.board.quadrants):
            x_offset = (i % 2) * quadrant_size  # décalage en x
            y_offset = (i // 2) * quadrant_size  # décalage en y

            # pour chaque ligne du quadrant
            for row_i, row in enumerate(quadrant):
                # pour chaque colonne du quadrant
                for col_i, cell in enumerate(row):
                    # couleur de la cellule en fonction de son index
                    color = self.QUADRANTS_CELLS_COLORS[cell[1]]
                    # coordonnée x du coin supérieur gauche de la cellule
                    x1 = x_offset + col_i * cell_size
                    # coordonnée y du coin supérieur gauche de la cellule
                    y1 = y_offset + row_i * cell_size
                    x2 = x1 + cell_size  # coordonnée x du coin inférieur droit de la cellule
                    y2 = y1 + cell_size  # coordonnée y du coin inférieur droit de la cellule
                    # dessine la cellule dans le canvas
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)