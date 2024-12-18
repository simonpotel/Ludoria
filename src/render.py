import tkinter as tk
from PIL import Image, ImageTk


class Render:
    # couleurs des cellules à l'intérieur des quadrants en fonction de leur index
    QUADRANTS_CELLS_COLORS = {0: 'red', 1: 'green', 2: 'blue', 3: 'yellow'}

    def __init__(self, game, canvas_size=600):
        self.game = game
        self.canvas_size = canvas_size
        self.root = tk.Tk()
        self.root.title("KATARENGA & Co")
        self.root.geometry(f"{canvas_size}x{canvas_size}") # taille de la fenêtre // on pourra modifier plus tard en fonctions des labels à rajouter
        self.canvas = tk.Canvas(self.root, width=canvas_size, height=canvas_size) # canvas pour dessiner le plateau
        self.canvas.pack() # afficher le canvas

        self.load_images() # charge les images des pièces
        self.render_board() # rendu du plateau // méthode à appeler à chaque fois qu'on veut update l'affichage

    def load_images(self):
        """
        procédure : charge les images des pièces (assets) dans le dictionnaire self.images pour les afficher dans le canvas
        """
        self.images = {}
        cell_size = (self.canvas_size // 2) // 4 # taille d'une cellule dans un quadrant (4 quadrants / 4*4 cellules par quadrant)

        for player in [0, 1]:  # joueur 0 ou 1

            image = Image.open(f"assets/towns/{player}_tower.png") # ouvrir l'image 
            aspect_ratio = image.width / image.height # ratio de l'image (largeur / hauteur)
            width = int(cell_size * aspect_ratio) # trouver le ratio de la taille de cellule par rapport à l'image
            height = cell_size - 10  # hauteur de l'image avec un offset pour ne pas coller l'image aux bordures de la cellule
            resized_image = image.resize((width, height), Image.LANCZOS) # redimensionner l'image avec la nouvelle taille
            self.images[f"tower_player_{player}"] = ImageTk.PhotoImage(resized_image) # ajouter l'image redimensionnée dans le dictionnaire self.images

    def render_board(self):
        """
        procédure qui dessine le plateau de jeu dans le canvas 
        """
        self.canvas.delete("all")  # efface tout ce qui est dans le canvas
        quadrant_size = self.canvas_size // 2  # taille d'un quadrant
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
                    # coordonnées des coins de la cellule
                    x1 = x_offset + col_i * cell_size
                    y1 = y_offset + row_i * cell_size
                    x2 = x1 + cell_size
                    y2 = y1 + cell_size

                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=color) # rectangle de la cellule sur le canvas

                    if cell[0] is not None: # une pièce est présente dans la cellule
                        piece = "tower"
                        player = cell[0]  
                        image_key = f"{piece}_player_{player}"
                        self.canvas.create_image(
                            x1 + cell_size // 2,
                            y1 + cell_size // 2,
                            image=self.images[image_key]
                        )
