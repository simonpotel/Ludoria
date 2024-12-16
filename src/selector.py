import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from pathlib import Path
import json
from src.katerenga.game import Game as Katerenga


class Selector:
    """
    class Selector : permet de choisir un jeu parmi les jeux disponibles et de choisir les quadrants
    parmis ceux de la configuration
    """
    GAMES = ["katerenga", "congress",
             "isolation"]  # liste des jeux disponibles
    # couleurs des cellules à l'intérieur des quadrants en fonction de leur index
    QUADRANTS_CELLS_COLORS = {0: 'red', 1: 'green', 2: 'blue', 3: 'yellow'}

    def __init__(self):
        """
        constructeur qui initialise l'attribut quadrants via le fichier de configuration,
        et charge l'interface graphique de sélection du jeu et des quadrants
        """
        self.root = tk.Tk()
        self.root.title("Smart Games: Selector")
        self.quadrants = self.load_quadrants()
        self.selected_quadrants = []
        self.setup_initial_ui()
        self.root.mainloop()

    def load_quadrants(self):
        """
        fonction qui charge les quadrants à partir du fichier de configuration quadrants.json
        et return un tableau des quadrants
        """
        with open('configs/quadrants.json', 'r') as file:
            quadrants_config = json.load(file)
        quadrants = []
        for key in sorted(quadrants_config.keys(), key=int):
            quadrants.append(quadrants_config[key])
        return quadrants

    def setup_initial_ui(self):
        """
        procédure qui charge l'interface graphique de sélection du jeu et des quadrants
        """
        config_frame = tk.Frame(
            self.root)  # frame pour les éléments de configuration
        # positionnement de la frame dans la grid
        config_frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")

        # nom du jeu (game_save)
        tk.Label(config_frame, text="Game Name:").pack(
            pady=10)  # label pour le nom du jeu
        self.entry_game_save = ttk.Combobox(
            config_frame, values=self.get_saved_games())  # combobox pour le nom du jeu
        self.entry_game_save.pack(pady=10)  # positionnement de la combobox
        # bind de l'événement de sélection de la game_save
        self.entry_game_save.bind(
            "<<ComboboxSelected>>", self.on_game_save_change)
        # bind de l'événement de relâchement de touche de la game_save
        self.entry_game_save.bind("<KeyRelease>", self.on_game_save_change)

        # sélection du jeu (game_selection)
        tk.Label(config_frame, text="Select Game:").pack(
            pady=10)  # label pour la sélection du jeu
        # combobox pour la sélection du jeu
        self.game_selection = ttk.Combobox(
            config_frame, state="readonly", values=self.GAMES)
        # sélection du premier jeu par défaut (katerenga)
        self.game_selection.current(0)
        self.game_selection.pack(pady=10)  # positionnement de la combobox

        # sélection des quadrants (quadrant_selectors)
        tk.Label(config_frame, text="Assign Quadrants:").pack(
            pady=10)  # label pour la sélection des quadrants
        self.quadrant_selectors = []  # liste des combobox pour la sélection des quadrants
        self.selected_quadrants = []  # Initialize selected_quadrants here
        for i in range(4):
            # création de la combobox pour la sélection du quadrant
            selector = self.create_quadrant_selector(config_frame, i)
            # ajout de la combobox à la liste des combobox
            self.quadrant_selectors.append(selector)
            self.selected_quadrants.append(
                [row[:] for row in self.quadrants[i]])
            # création des boutons de rotation pour chaque quadrant
            self.create_rotation_buttons(config_frame, i)

        tk.Button(config_frame, text="Load Game", command=self.load_game).pack(
            pady=10)  # bouton pour charger le jeu

        # canvas pour afficher les quadrants
        self.canvas = tk.Canvas(self.root, width=400, height=400)
        # positionnement du canvas dans la grid
        self.canvas.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.draw_quadrants()

    def create_quadrant_selector(self, parent, index):
        """
        fonction qui crée une combobox pour la sélection d'un quadrant et la retourne
        """
        values = [f"{j+1}" for j in range(len(self.quadrants))
                  ]  # valeurs possibles pour la sélection du quadrant
        # combobox pour la sélection du quadrant
        selector = ttk.Combobox(parent, state="readonly", values=values)
        # sélection du premier quadrant par défaut
        selector.current(index if index < len(self.quadrants) else 0)
        selector.pack(pady=5)  # positionnement de la combobox
        # bind de l'événement de sélection de la combobox
        selector.bind("<<ComboboxSelected>>", self.event_combo)
        return selector  # retourne la combobox

    def create_rotation_buttons(self, parent, index):
        """
        fonction qui crée les boutons de rotation pour un quadrant
        """
        frame = tk.Frame(parent)
        frame.pack(pady=5)
        tk.Button(frame, text="⤴️", command=lambda i=index: self.rotate_left(i)).pack(
            side="left")  # bouton pour rotation à gauche
        tk.Button(frame, text="⤵️", command=lambda i=index: self.rotate_right(i)).pack(
            side="right")  # bouton pour rotation à droite

    def get_saved_games(self):
        """
        fonction qui retourne la liste des jeux sauvegardés dans le dossier saves/
        (tous les fichiers qui ont l'extension .json)
        """
        saves_dir = Path('saves')  # dossier des sauvegardes
        if not saves_dir.exists():
            saves_dir.mkdir()  # création du dossier s'il n'existe pas
        saved_games = []
        for file in saves_dir.glob('*.json'):
            # ajout du nom du fichier sans l'extension à la liste des jeux sauvegardés
            saved_games.append(file.stem)
        return saved_games

    def on_game_save_change(self, event=None):
        """
        procédure qui s'active lorsqu'un changement est détecté dans la combobox de la game_save
        """
        game_save = self.entry_game_save.get()
        if game_save in self.get_saved_games():  # si le nom de la game_save est dans la liste des jeux sauvegardés
            self.game_selection.pack_forget()  # on cache la combobox de sélection du jeu
        else:
            # sinon on affiche la combobox de sélection du jeu car cette save n'existe pas déjà
            self.game_selection.pack(pady=10)

    def load_game(self):
        """
        procédure qui charge le jeu sélectionné avec les quadrants sélectionnés
        """
        game_save = self.entry_game_save.get()  # nom du jeu
        selected_game = self.game_selection.get()  # jeu sélectionné
        if not game_save:
            messagebox.showerror("Error", "Please enter a game name.")
            return
        # si le nom de la game_save est dans la liste des jeux sauvegardés ou si le jeu sélectionné est dans la liste des jeux disponibles
        if game_save in self.get_saved_games() or selected_game in self.GAMES:
            self.selected_quadrants = []
            for selector in self.quadrant_selectors:
                quadrant_index = int(selector.get()) - 1
                # ajout du quadrant sélectionné à la liste des quadrants sélectionnés
                self.selected_quadrants.append(
                    [row[:] for row in self.quadrants[quadrant_index]])
            self.root.destroy()  # fermeture de la fenêtre tkinter
            if selected_game == "katerenga":
                game = Katerenga(game_save, self.selected_quadrants)
                game.load_game()
            else:
                messagebox.showerror("Error", "Game not defined.")
                exit()
            self.ask_replay()
        else:
            messagebox.showerror("Error", "Please select a valid game.")

    def ask_replay(self):
        """
        procédure qui demande à l'utilisateur s'il veut rejouer
        """
        if messagebox.askyesno("Smart Games: Selector", "Do you want to replay a new game?"):
            self.__init__()

    def draw_quadrants(self):
        """
        procédure qui dessine les quadrants dans le canvas en fonction des quadrants sélectionnés
        """
        self.canvas.delete("all")  # efface tout ce qui est dans le canvas
        quadrant_size = 200  # taille d'un quadrant
        cell_size = quadrant_size // 4  # taille d'une cellule dans un quadrant

        # pour chaque combobox de sélection de quadrant
        for i, selector in enumerate(self.quadrant_selectors):
            quadrant_index = int(selector.get()) - 1
            quadrant = self.selected_quadrants[i] if self.selected_quadrants else self.quadrants[quadrant_index]
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

    def event_combo(self, event=None):
        """
        procédure qui s'active lorsqu'un changement est détecté dans une combobox de sélection de quadrant
        """
        self.draw_quadrants()

    def rotate_right(self, index):
        """
        procédure qui fait tourner un quadrant vers la droite
        """
        rotated_quadrant = []
        for row in range(4):
            new_row = []
            for col in range(4):
                new_row.append(self.selected_quadrants[index][3 - col][row])
            rotated_quadrant.append(new_row)
        self.selected_quadrants[index] = rotated_quadrant
        self.draw_quadrants()

    def rotate_left(self, index):
        """
        procédure qui fait tourner un quadrant vers la gauche
        """
        rotated_quadrant = []
        for row in range(4):
            new_row = []
            for col in range(4):
                new_row.append(self.selected_quadrants[index][col][3 - row])
            rotated_quadrant.append(new_row)
        self.selected_quadrants[index] = rotated_quadrant
        self.draw_quadrants()
