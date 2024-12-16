import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk


class Render:
    """
    class Render : gère l'interface graphique du game avec tkinter et les événements de clic sur le canvas
    pour le déplacement des pieces et le déroulement du game.
    """
    def __init__(self, game):
        self.game = game 
        self.root = tk.Tk() #fenetre principale tkinter 
        self.root.title = ("KATARENGA & Co") #titre de la fenêtre 
        self.root.geometry("800x800") #taille de la fenêtre 
        self.canvas_with = 400 #largeur du canvas
        self.canvas_height = 400 #hauteur du canvas
        self.labal_game_name = tk.label(self.root, text=f'Game :  {self.game_name}', 
            font=("Roboto, 20")) #label que le joueur donnera au lancement
        self.labal_game_name.pack(pady=(10,0)) #margin du label de 10 en haut
        self.label_instruction = tk.label(self.root, text="Au tour du joueur : ", 
            font=("Roboto, 15")) #label qui indique le tour du joueur
        self.label_instruction.pack(pady=(10,0)) #margin du label de 10 en haut
        self.label_round_player = tk.Label(self.root, text="Joueur 1", 
            font=("Roboto, 15")) #label qui indique le joueur 1
        self.label_round_player.pack(pady=(10,0)) #margin du label de 10 en haut
        self.canvas = tk.Canvas(self.root, width=self.canvas_width, height=self.canvas_height) #canvas de la fenêtre
        self.canvas.pack(pady=(10,0)) #margin du canvas de 10 en haut
        self.load_images()
        self.draw_game() #fonction qui dessine le jeu

    """
    def load_images(self):
        """
                procédure: charge les images des pièces et les redimensionne pour s'adapter aux cellules du board.

        """
        self.images = {}
        size = self.game.board.get_size()
        height_cell = self.canvas_height // size

        pieces = ["tower"] #liste des pièces
        max_height = 0
        piece_images = {}

        for piece in pieces: #pour chaque pièce
            for player in [0, 1]: #pour chaque joueur
                #chargement de l'image qu'on utilisera sur le canvas
                image_path = f"assets/{piece}_{player}.png"
                image = Image.open(image_path)
                piece_images[f"{piece}_player_{player + 1}"] = image
                if image.height > max_height: #si la hauteur de l'image est supérieure à la hauteur max trouvée 
                    max_height = image.height # on définit la taille maximale des images 
        
        #ration de redimensionnement pour faire fit les images dans les cellules 
        ratio = height_cell / max_height

        #redimmensionnement des images avec le ratio
        for key, image in piece_images.items():
            width = int(image.width * ratio)
            height = int(image.height * ratio)
            resized_image = image.resize((width, height), Image.LANCZOS)
            self.images[key] = ImageTk.PhotoImage(resized_image)

    """



        