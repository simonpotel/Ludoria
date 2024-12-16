import tkinter as tk
from tkinter import messagebox
#from PIL import Image, ImageTk


class Render:
    """
    class Render : gère l'interface graphique du game avec tkinter et les événements de clic sur le canvas
    pour le déplacement des pieces et le déroulement du game.
    """
    def __init__(self, game, quadrants):
        self.game = game 
        self.quadrants = quadrants 
        self.root = tk.Tk() #fenetre principale tkinter 
        self.root.title = ("KATARENGA & Co") #titre de la fenêtre 
        self.root.geometry("800x800") #taille de la fenêtre 
        self.canvas_with = 400 #largeur du canvas
        self.canvas_height = 400 #hauteur du canvas
        self.label_game_name = tk.Label(self.root, text=f'Game :  {self.game_name}', 
            font=("Roboto, 20")) #label que le joueur donnera au lancement
        self.label_game_name.pack(pady=(10,0)) #margin du label de 10 en haut
        self.label_instruction = tk.Label(self.root, text="Au tour du joueur : ", 
            font=("Roboto, 15")) #label qui indique le tour du joueur
        self.label_instruction.pack(pady=(10,0)) #margin du label de 10 en haut
        self.label_round_player = tk.Label(self.root, text="Joueur 1", 
            font=("Roboto, 15")) #label qui indique le joueur 1
        self.label_round_player.pack(pady=(10,0)) #margin du label de 10 en haut
        self.canvas = tk.Canvas(self.root, width=self.canvas_width, height=self.canvas_height) #canvas de la fenêtre
        self.canvas.pack(pady=(10,0)) #margin du canvas de 10 en haut
        self.load_images()
        self.draw_game() #fonction qui dessine le jeu
        self.root.mainloop() #boucle principale de la fenêtre tkinter

    """
    def load_images(self):
    
                #procédure: charge les images des pièces et les redimensionne pour s'adapter aux cellules du board.

        
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
    def draw_game(self):
        """
        procédure: dessine le jeu sur le canvas en fonction des positions des pièces dans le board
        """
        self.label_instruction.config(
            text="Your turn to play:", font=("Helvetica", 15))
        self.label_round_player.config(
            text=f"Player {self.game.round_player[0] + 1}")
        
        size = self.game.board.get_size()
        width_cell = self.canvas_width // size
        height_cell = self.canvas_height // size
        margin = 10
        width_border = 2.5

        #boucles qui dessinnent les cells du board
        for i in range(size):
            for j in range(size):
                _, color = self.quadrants[i // (size // 2)][j // (size // 2)]
                color_map = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00"]  # Red, Green, Blue, Yellow
                fill_color = color_map[color]
                x, y = j * width_cell, i * height_cell
                w, h = (j + 1) * width_cell, (i + 1) * height_cell
                self.canvas.create_rectangle(x, y, w, h, outline="", fill=fill_color)


                piece, player = self.game.board.get_board()[i][j]  # Ajout de cette ligne
                if piece is not None:
                    if piece == 1 or piece == 2:
                        image = self.images[f"tower_player_{player + 1}"]
                        image_id = self.canvas.create_image(
                            x + width_cell // 2, y + height_cell // 2, image=image)
                        self.canvas.tag_bind(image_id, '<Button-1>', lambda _, i=i, j=j: self.game.event_click_piece(i, j))


            for i in range(size + 1):
                # lines horizontales
                self.canvas.create_line(width_border, i * height_cell, self.canvas_width,
                                        i * height_cell)
                # lines verticales
                self.canvas.create_line(
                    i * width_cell, width_border, i * width_cell, self.canvas_height + 0.25)

        # ligne gauche verticale
            self.canvas.create_line(
                width_border, width_border, width_border, self.canvas_height)
        # ligne haute horizontale
            self.canvas.create_line(
                width_border, width_border, self.canvas_width, width_border)
        
    
    def update_tkinter(self):
        self.canvas.delete("all")
        self.draw_game()
        self.canvas.bind("<Button-1>", self.game.event_click_board)
        


        