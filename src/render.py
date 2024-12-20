import tkinter as tk
from PIL import Image, ImageTk


class Render:
    # couleurs des cellules à l'intérieur des quadrants en fonction de leur index
    QUADRANTS_CELLS_COLORS = {0: 'red', 1: 'green', 2: 'blue', 3: 'yellow', 4: 'grey'}

    def __init__(self, game, canvas_size=800):
        self.game = game
        self.canvas_size = canvas_size
        self.root = tk.Tk()
        self.root.title("KATARENGA & Co")
        self.root.geometry(f"{canvas_size}x{canvas_size}")
        self.canvas = tk.Canvas(self.root, width=canvas_size, height=canvas_size)
        self.canvas.pack()

        # Calculer la taille des cellules basée sur un plateau 10x10
        self.cell_size = canvas_size // 10
        self.board_offset = self.cell_size  # Décalage d'une cellule pour la bordure

        self.load_images()
        self.render_board()

    def load_images(self):
        """
        procédure : charge les images des pièces (assets) dans le dictionnaire self.images
        """
        self.images = {}
        cell_size = self.cell_size  # Utiliser la nouvelle taille de cellule

        for player in [0, 1]:
            image = Image.open(f"assets/towns/{player}_tower.png")
            aspect_ratio = image.width / image.height
            width = int(cell_size * aspect_ratio)
            height = cell_size - 10
            resized_image = image.resize((width, height), Image.LANCZOS)
            self.images[f"tower_player_{player}"] = ImageTk.PhotoImage(resized_image)

    def render_board(self):
        """
        procédure qui dessine le plateau de jeu dans le canvas avec les cases supplémentaires
        """
        self.canvas.delete("all")
        cell_size = self.cell_size

        # Dessiner toutes les cases blanches externes
        for i in range(10):
            for j in range(10):
                # Si c'est une case de bordure (première/dernière ligne ou colonne)
                if i == 0 or i == 9 or j == 0 or j == 9:
                    x1 = j * cell_size
                    y1 = i * cell_size
                    x2 = x1 + cell_size
                    y2 = y1 + cell_size
                    
                    # Cases grises dans les coins
                    if (i == 0 and j == 0) or (i == 0 and j == 9) or \
                       (i == 9 and j == 0) or (i == 9 and j == 9):
                        color = 'grey'
                    else:
                        color = 'white'
                        
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)

        # Dessiner le plateau principal (8x8)
        for i, quadrant in enumerate(self.game.board.quadrants):
            # Calculer le décalage pour chaque quadrant
            quad_x = (i % 2) * 4 + 1  # +1 pour le décalage de la bordure
            quad_y = (i // 2) * 4 + 1  # +1 pour le décalage de la bordure

            for row_i, row in enumerate(quadrant):
                for col_i, cell in enumerate(row):
                    x1 = (quad_x + col_i) * cell_size
                    y1 = (quad_y + row_i) * cell_size
                    x2 = x1 + cell_size
                    y2 = y1 + cell_size

                    color = self.QUADRANTS_CELLS_COLORS[cell[1]]
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)

                    if cell[0] is not None:
                        piece = "tower"
                        player = cell[0]
                        image_key = f"{piece}_player_{player}"
                        self.canvas.create_image(
                            x1 + cell_size // 2,
                            y1 + cell_size // 2,
                            image=self.images[image_key]
                        )
