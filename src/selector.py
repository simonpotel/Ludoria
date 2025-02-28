import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from pathlib import Path
import json
from src.katerenga.game import Game as Katerenga
from src.isolation.game import Game as Isolation
from src.congress.game import Game as Congress
from src.render import Render
from src.saves import load_game
from src.utils.logger import Logger


class Selector:
    """
    class Selector : interface graphique permettant de sélectionner et configurer un jeu
    gère la sélection du jeu, des quadrants et le chargement des sauvegardes
    """
    GAMES = ["katerenga", "isolation", "congress"]  # liste des jeux disponibles
    GAME_MODES = ["Solo", "Bot", "Network"]  # liste des modes de jeu disponibles

    def __init__(self):
        """
        constructeur : initialise l'interface de sélection du jeu et charge la configuration des quadrants
        """
        Logger.initialize()
        Logger.info("Selector", "Initializing game selector")
        self.root = tk.Tk()
        self.root.title("Smart Games: Selector")
        self.quadrants = self.load_quadrants()
        self.selected_quadrants = []
        self.setup_initial_ui()
        Logger.info("Selector", "Game selector initialized successfully")
        self.root.mainloop()

    def load_quadrants(self):
        """
        fonction : charge la configuration des quadrants depuis le fichier JSON
        retourne : liste des quadrants disponibles
        """
        Logger.info("Selector", "Loading quadrants configuration")
        try:
            with open('configs/quadrants.json', 'r') as file:
                self.quadrants_config = json.load(file)
            self.quadrant_names = sorted(self.quadrants_config.keys())
            quadrants = []
            for key in self.quadrant_names:
                quadrants.append(self.quadrants_config[key])
            Logger.success("Selector", f"Successfully loaded {len(quadrants)} quadrants")
            return quadrants
        except FileNotFoundError:
            Logger.error("Selector", "Quadrants configuration file not found")
            messagebox.showerror("Error", "Quadrants configuration file not found.")
            exit(1)
        except json.JSONDecodeError:
            Logger.error("Selector", "Invalid quadrants configuration file format")
            messagebox.showerror("Error", "Invalid quadrants configuration file format.")
            exit(1)

    def setup_initial_ui(self):
        """
        procédure : crée et configure l'interface graphique principale
        """
        # frame principale pour les éléments de configuration
        config_frame = tk.Frame(self.root)
        config_frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")

        # configuration du nom de la partie
        tk.Label(config_frame, text="Game Name:").pack(pady=10)
        self.entry_game_save = ttk.Combobox(config_frame, values=self.get_saved_games())
        self.entry_game_save.pack(pady=10)
        self.entry_game_save.bind("<<ComboboxSelected>>", self.on_game_save_change)
        self.entry_game_save.bind("<KeyRelease>", self.on_game_save_change)

        tk.Label(config_frame, text="Select Game Mode:").pack(pady=10)
        self.mode_selection = ttk.Combobox(config_frame, state="readonly", values=self.GAME_MODES)
        self.mode_selection.current(0)  
        self.mode_selection.pack(pady=10)

        # sélection du type de jeu
        self.label_game_name = tk.Label(config_frame, text="Select Game:").pack(pady=10)
        self.game_selection = ttk.Combobox(config_frame, state="readonly", values=self.GAMES)
        self.game_selection.current(0)
        self.game_selection.pack(pady=10)

        # configuration des quadrants
        self.label_quadrants = tk.Label(config_frame, text="Assign Quadrants:").pack(pady=10)
        self.quadrant_selectors = []
        self.selected_quadrants = []
        
        # création des sélecteurs de quadrants
        for i in range(4):
            frame = tk.Frame(config_frame)
            frame.pack(pady=5)
            selector = self.create_quadrant_selector(frame, i)
            self.quadrant_selectors.append(selector)
            self.selected_quadrants.append([row[:] for row in self.quadrants[i]])
            self.create_rotation_buttons(frame, i)

        # bouton de chargement du jeu
        tk.Button(config_frame, text="Load Game", command=self.load_game).pack(pady=10)

        # canvas pour la prévisualisation des quadrants
        self.canvas = tk.Canvas(self.root, width=400, height=400)
        self.canvas.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.draw_quadrants()

    def create_quadrant_selector(self, parent, index):
        """
        fonction : crée un sélecteur de quadrant avec une combobox
        paramètres :
            parent - widget parent
            index - index du quadrant
        retourne : le widget combobox créé
        """
        selector = ttk.Combobox(parent, state="readonly", values=self.quadrant_names)
        selector.current(index if index < len(self.quadrants) else 0)
        selector.pack(pady=5)
        selector.bind("<<ComboboxSelected>>", self.event_combo)
        return selector

    def create_rotation_buttons(self, parent, index):
        """
        procédure : crée les boutons de rotation pour un quadrant
        paramètres :
            parent - widget parent
            index - index du quadrant
        """
        tk.Button(parent, text="⤴️", command=lambda i=index: self.rotate_left(i)).pack(side="left")
        tk.Button(parent, text="⤵️", command=lambda i=index: self.rotate_right(i)).pack(side="left")

    def get_saved_games(self):
        """
        fonction : récupère la liste des sauvegardes disponibles
        retourne : liste des noms de sauvegardes (sans extension)
        """
        saves_dir = Path('saves')
        if not saves_dir.exists():
            saves_dir.mkdir()
        saved_games = []
        for file in saves_dir.glob('*.json'):
            saved_games.append(file.stem)
        return saved_games

    def on_game_save_change(self, event=None):
        """
        procédure : gère le changement de sauvegarde sélectionnée
        met à jour l'interface en fonction de l'existence ou non de la sauvegarde
        """
        game_save = self.entry_game_save.get()
        if game_save in self.get_saved_games():
            self.game_selection.pack_forget()
            try:
                with open(f"saves/{game_save}.json", 'r') as file:
                    game_state = json.load(file)
                    self.game_selection.current(int(game_state['game_number']))
            except FileNotFoundError:
                messagebox.showerror("Error", "Game save not found in saves/.")
        else:
            self.game_selection.pack(pady=10)

    def load_game(self):
        """
        procédure : charge ou crée une nouvelle partie selon la configuration
        vérifie la validité des paramètres et initialise le jeu approprié
        """
        game_save = self.entry_game_save.get()
        selected_game = self.game_selection.get()
        selected_mode = self.mode_selection.get()
        
        if not game_save:
            Logger.warning("Selector", "No game name provided")
            messagebox.showerror("Error", "Please enter a game name.")
            return
            
        Logger.info("Selector", f"Loading game: {selected_game} (Save: {game_save}, Mode: {selected_mode})")
        
        if game_save in self.get_saved_games() or selected_game in self.GAMES:
            if selected_mode != "Solo":
                Logger.warning("Selector", f"Game mode {selected_mode} not yet implemented")
                messagebox.showerror("Error", f"Game mode {selected_mode} is not yet implemented.")
                return

            self.root.destroy()
            try:
                # création de l'instance du jeu approprié
                match selected_game:
                    case "katerenga":
                        Logger.game("Selector", "Starting Katerenga game")
                        game = Katerenga(game_save, self.selected_quadrants)
                    case "isolation":
                        Logger.game("Selector", "Starting Isolation game")
                        game = Isolation(game_save, self.selected_quadrants)
                    case "congress":
                        Logger.game("Selector", "Starting Congress game")
                        game = Congress(game_save, self.selected_quadrants)
                    case _:
                        Logger.error("Selector", f"Undefined game type: {selected_game}")
                        messagebox.showerror("Error", "Game not defined.")
                        exit()
                
                # charge la sauvegarde si elle existe
                if game_save in self.get_saved_games():
                    Logger.info("Selector", f"Loading saved game state: {game_save}")
                    load_game(game)
                    game.render.render_board()
                game.load_game()
                Logger.success("Selector", f"Successfully loaded game: {selected_game}")
                
            except Exception as e:
                Logger.error("Selector", f"Error loading game: {str(e)}")
                messagebox.showerror("Error", f"Failed to load game: {str(e)}")
                return
                
            self.ask_replay()
        else:
            Logger.warning("Selector", f"Invalid game selection: {selected_game}")
            messagebox.showerror("Error", "Please select a valid game.")

    def ask_replay(self):
        """
        procédure : demande au joueur s'il souhaite démarrer une nouvelle partie
        """
        if messagebox.askyesno("Smart Games: Selector", "Do you want to replay a new game?"):
            self.__init__()

    def draw_quadrants(self):
        """
        procédure : dessine la prévisualisation des quadrants sélectionnés dans le canvas
        """
        self.canvas.delete("all")
        quadrant_size = 200
        cell_size = quadrant_size // 4

        # dessine chaque quadrant
        for i, selector in enumerate(self.quadrant_selectors):
            selected_name = selector.get()
            quadrant_index = self.quadrant_names.index(selected_name)
            quadrant = self.selected_quadrants[i] if self.selected_quadrants else self.quadrants[quadrant_index]
            x_offset = (i % 2) * quadrant_size
            y_offset = (i // 2) * quadrant_size

            # dessine chaque cellule du quadrant
            for row_i, row in enumerate(quadrant):
                for col_i, cell in enumerate(row):
                    color = Render.QUADRANTS_CELLS_COLORS[cell[1]]
                    x1 = x_offset + col_i * cell_size
                    y1 = y_offset + row_i * cell_size
                    x2 = x1 + cell_size
                    y2 = y1 + cell_size
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)

    def event_combo(self, event=None):
        """
        procédure : gère le changement de sélection d'un quadrant
        met à jour l'affichage des quadrants
        """
        self.update_selected_quadrants()
        self.draw_quadrants()

    def update_selected_quadrants(self):
        """
        procédure : met à jour la liste des quadrants sélectionnés
        """
        for i, selector in enumerate(self.quadrant_selectors):
            selected_name = selector.get()
            quadrant_index = self.quadrant_names.index(selected_name)
            self.selected_quadrants[i] = [row[:] for row in self.quadrants[quadrant_index]]

    def rotate_right(self, index):
        """
        procédure : effectue une rotation horaire du quadrant spécifié
        paramètres :
            index - index du quadrant à faire pivoter
        """
        Logger.board("Selector", f"Rotating quadrant {index} right")
        quadrant = self.selected_quadrants[index]
        rotated = list(zip(*quadrant[::-1]))
        self.selected_quadrants[index] = [list(row) for row in rotated]
        self.draw_quadrants()
        Logger.success("Selector", f"Quadrant {index} rotated right successfully")

    def rotate_left(self, index):
        """
        procédure : effectue une rotation antihoraire du quadrant spécifié
        paramètres :
            index - index du quadrant à faire pivoter
        """
        Logger.board("Selector", f"Rotating quadrant {index} left")
        quadrant = self.selected_quadrants[index]
        rotated = list(zip(*quadrant))[::-1]
        self.selected_quadrants[index] = [list(row) for row in rotated]
        self.draw_quadrants()
        Logger.success("Selector", f"Quadrant {index} rotated left successfully")
