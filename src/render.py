import tkinter as tk
from PIL import Image, ImageTk


class Render:
    # couleurs des cellules à l'intérieur des quadrants en fonction de leur index
    QUADRANTS_CELLS_COLORS = {0: 'red', 1: 'green', 2: 'blue',
                              3: 'yellow', 4: 'white', 5: 'black', None: 'grey'}

    def __init__(self, game, canvas_size=600):
        self.game = game
        self.canvas_size = canvas_size
        self.board_size = len(game.board.board)  # taille du board dynamique
        self.root = tk.Tk()
        self.root.title("KATARENGA & Co")
        # taille de la fenêtre
        self.root.geometry(f"{canvas_size}x{canvas_size}")
        # canvas pour dessiner le plateau
        self.canvas = tk.Canvas(
            self.root, width=canvas_size, height=canvas_size)
        self.canvas.pack()  # afficher le canvas

        self.load_images()  # charge les images des pièces
        self.render_board()  # rendu du plateau

    def load_images(self):
        """
        procédure : charge les images des pièces (assets) dans le dictionnaire self.images pour les afficher dans le canvas
        """
        self.images = {}
        cell_size = self.canvas_size // self.board_size  # taille d'une cellule

        for player in [0, 1]:  # joueur 0 ou 1
            # ouvrir l'image
            image = Image.open(f"assets/towns/{player}_tower.png")
            # ratio de l'image (largeur / hauteur)
            aspect_ratio = image.width / image.height
            # trouver le ratio de la taille de cellule par rapport à l'image
            width = int(cell_size * aspect_ratio)
            # hauteur de l'image avec un offset pour ne pas coller l'image aux bordures de la cellule
            height = cell_size - 10
            # redimensionner l'image avec la nouvelle taille
            resized_image = image.resize((width, height), Image.LANCZOS)
            # ajouter l'image redimensionnée dans le dictionnaire self.images
            self.images[f"tower_player_{
                player}"] = ImageTk.PhotoImage(resized_image)

    def render_board(self):
        """
        procédure qui dessine le plateau de jeu dans le canvas
        """
        self.canvas.delete("all")  # efface tout ce qui est dans le canvas
        cell_size = self.canvas_size // self.board_size  # taille d'une cellule

        # pour chaque ligne du plateau de jeu
        for row_i, row in enumerate(self.game.board.board):
            # pour chaque colonne du plateau de jeu
            for col_i, cell in enumerate(row):
                # couleur de la cellule en fonction de son index
                color = self.QUADRANTS_CELLS_COLORS[cell[1]]
                # coordonnées des coins de la cellule
                x1 = col_i * cell_size
                y1 = row_i * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size

                # rectangle de la cellule sur le canvas
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)

                if cell[0] is not None:  # une pièce est présente dans la cellule
                    piece = "tower"
                    player = cell[0]
                    image_key = f"{piece}_player_{player}"
                    self.canvas.create_image(
                        x1 + cell_size // 2,
                        y1 + cell_size // 2,
                        image=self.images[image_key]
                    )
