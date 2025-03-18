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
    classe : interface de sélection et configuration des jeux
    """
    GAMES = ["katerenga", "isolation", "congress"]
    GAME_MODES = ["Solo", "Bot", "Network"]

    def __init__(self):
        """
        procédure : initialise l'interface de sélection
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
        fonction : charge la configuration des quadrants
        retour : liste des quadrants disponibles
        """
        Logger.info("Selector", "Loading quadrants configuration")
        try:
            with open('configs/quadrants.json', 'r') as file:
                self.quadrants_config = json.load(file)
                self.quadrant_names = sorted(self.quadrants_config.keys())
                return [self.quadrants_config[key] for key in self.quadrant_names]
        except FileNotFoundError:
            self._handle_config_error("Quadrants configuration file not found")
        except json.JSONDecodeError:
            self._handle_config_error("Invalid quadrants configuration file format")

    def _handle_config_error(self, message):
        """
        procédure : gère les erreurs de configuration
        params :
            message - message d'erreur à afficher
        """
        Logger.error("Selector", message)
        messagebox.showerror("Error", message)
        exit(1)

    def setup_initial_ui(self):
        """
        procédure : configure l'interface graphique
        """
        config_frame = self._create_config_frame()
        self._setup_game_config(config_frame)
        self._setup_quadrant_config(config_frame)
        tk.Button(config_frame, text="Load Game", command=self.load_game).pack(pady=10)
        self._setup_preview_canvas()
        self.draw_quadrants()

    def _create_config_frame(self):
        """
        fonction : crée le cadre principal de configuration
        retour : frame de configuration
        """
        frame = tk.Frame(self.root)
        frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")
        return frame

    def _setup_game_config(self, parent):
        """
        procédure : configure les éléments de sélection du jeu
        params :
            parent - widget parent
        """
        tk.Label(parent, text="Game Name:").pack(pady=10)
        self.entry_game_save = ttk.Combobox(parent, values=self.get_saved_games())
        self.entry_game_save.pack(pady=10)
        self.entry_game_save.bind("<<ComboboxSelected>>", self.on_game_save_change)
        self.entry_game_save.bind("<KeyRelease>", self.on_game_save_change)

        tk.Label(parent, text="Select Game Mode:").pack(pady=10)
        self.mode_selection = ttk.Combobox(parent, state="readonly", values=self.GAME_MODES)
        self.mode_selection.current(0)
        self.mode_selection.pack(pady=10)

        tk.Label(parent, text="Select Game:").pack(pady=10)
        self.game_selection = ttk.Combobox(parent, state="readonly", values=self.GAMES)
        self.game_selection.current(0)
        self.game_selection.pack(pady=10)

    def _setup_quadrant_config(self, parent):
        """
        procédure : configure les sélecteurs de quadrants
        params :
            parent - widget parent
        """
        tk.Label(parent, text="Assign Quadrants:").pack(pady=10)
        self.quadrant_selectors = []
        self.selected_quadrants = []
        
        for i in range(4):
            frame = tk.Frame(parent)
            frame.pack(pady=5)
            selector = self.create_quadrant_selector(frame, i)
            self.quadrant_selectors.append(selector)
            self.selected_quadrants.append([row[:] for row in self.quadrants[i]])
            self.create_rotation_buttons(frame, i)

    def _setup_preview_canvas(self):
        """
        procédure : configure le canvas de prévisualisation
        """
        self.canvas = tk.Canvas(self.root, width=400, height=400)
        self.canvas.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

    def create_quadrant_selector(self, parent, index):
        """
        fonction : crée un sélecteur de quadrant
        params :
            parent - widget parent
            index - index du quadrant
        retour : widget combobox créé
        """
        selector = ttk.Combobox(parent, state="readonly", values=self.quadrant_names)
        selector.current(index if index < len(self.quadrants) else 0)
        selector.pack(pady=5)
        selector.bind("<<ComboboxSelected>>", self.event_combo)
        return selector

    def create_rotation_buttons(self, parent, index):
        """
        procédure : crée les boutons de rotation d'un quadrant
        params :
            parent - widget parent
            index - index du quadrant
        """
        tk.Button(parent, text="⤴️", command=lambda i=index: self.rotate_left(i)).pack(side="left")
        tk.Button(parent, text="⤵️", command=lambda i=index: self.rotate_right(i)).pack(side="left")

    def get_saved_games(self):
        """
        fonction : récupère la liste des sauvegardes
        retour : liste des noms de sauvegardes
        """
        saves_dir = Path('saves')
        saves_dir.mkdir(exist_ok=True)
        return [file.stem for file in saves_dir.glob('*.json')]

    def on_game_save_change(self, event=None):
        """
        procédure : gère le changement de sauvegarde
        params :
            event - événement déclencheur
        """
        game_save = self.entry_game_save.get()
        if game_save in self.get_saved_games():
            self.game_selection.pack_forget()
            try:
                with open(f"saves/{game_save}.json", 'r') as file:
                    self.game_selection.current(int(json.load(file)['game_number']))
            except FileNotFoundError:
                messagebox.showerror("Error", "Game save not found in saves/.")
        else:
            self.game_selection.pack(pady=10)

    def load_game(self):
        """
        procédure : charge ou crée une nouvelle partie
        """
        game_save = self.entry_game_save.get()
        selected_game = self.game_selection.get()
        selected_mode = self.mode_selection.get()
        
        if not self._validate_game_params(game_save, selected_mode):
            return
            
        Logger.info("Selector", f"Loading game: {selected_game} (Save: {game_save}, Mode: {selected_mode})")
        
        if game_save in self.get_saved_games() or selected_game in self.GAMES:
            self.root.destroy()
            self._start_game(game_save, selected_game, selected_mode)
            self.ask_replay()
        else:
            Logger.warning("Selector", f"Invalid game selection: {selected_game}")
            messagebox.showerror("Error", "Please select a valid game.")

    def _validate_game_params(self, game_save, selected_mode):
        """
        fonction : valide les paramètres du jeu
        params :
            game_save - nom de la sauvegarde
            selected_mode - mode de jeu sélectionné
        retour : bool indiquant si les paramètres sont valides
        """
        if not game_save:
            Logger.warning("Selector", "No game name provided")
            messagebox.showerror("Error", "Please enter a game name.")
            return False
            
        return True

    def _start_game(self, game_save, selected_game, selected_mode):
        """
        procédure : démarre le jeu sélectionné
        params :
            game_save - nom de la sauvegarde
            selected_game - type de jeu
            selected_mode - mode de jeu
        """
        try:
            game = self._create_game_instance(selected_game, game_save, selected_mode)
            if game_save in self.get_saved_games():
                Logger.info("Selector", f"Loading saved game state: {game_save}")
                load_game(game)
                game.render.render_board()
            game.load_game()
            Logger.success("Selector", f"Successfully loaded game: {selected_game}")
        except Exception as e:
            Logger.error("Selector", f"Error loading game: {str(e)}")
            messagebox.showerror("Error", f"Failed to load game: {str(e)}")

    def _create_game_instance(self, game_type, game_save, mode):
        """
        fonction : crée une instance du jeu approprié
        params :
            game_type - type de jeu à créer
            game_save - nom de la sauvegarde
            mode - mode de jeu
        retour : instance du jeu créé
        """
        match game_type:
            case "katerenga":
                Logger.game("Selector", "Starting Katerenga game")
                return Katerenga(game_save, self.selected_quadrants, mode)
            case "isolation":
                Logger.game("Selector", "Starting Isolation game")
                return Isolation(game_save, self.selected_quadrants, mode)
            case "congress":
                Logger.game("Selector", "Starting Congress game")
                return Congress(game_save, self.selected_quadrants, mode)
            case _:
                Logger.error("Selector", f"Undefined game type: {game_type}")
                messagebox.showerror("Error", "Game not defined.")
                exit(1)

    def ask_replay(self):
        """
        procédure : propose de démarrer une nouvelle partie
        """
        if messagebox.askyesno("Smart Games: Selector", "Do you want to replay a new game?"):
            self.__init__()

    def draw_quadrants(self):
        """
        procédure : dessine la prévisualisation des quadrants
        """
        self.canvas.delete("all")
        quadrant_size = 200
        cell_size = quadrant_size // 4

        for i, selector in enumerate(self.quadrant_selectors):
            quadrant = self._get_quadrant_data(selector, i)
            x_offset = (i % 2) * quadrant_size
            y_offset = (i // 2) * quadrant_size
            self._draw_quadrant(quadrant, x_offset, y_offset, cell_size)

    def _get_quadrant_data(self, selector, index):
        """
        fonction : récupère les données d'un quadrant
        params :
            selector - sélecteur de quadrant
            index - index du quadrant
        retour : données du quadrant
        """
        selected_name = selector.get()
        quadrant_index = self.quadrant_names.index(selected_name)
        return self.selected_quadrants[index] if self.selected_quadrants else self.quadrants[quadrant_index]

    def _draw_quadrant(self, quadrant, x_offset, y_offset, cell_size):
        """
        procédure : dessine un quadrant
        params :
            quadrant - données du quadrant
            x_offset - décalage horizontal
            y_offset - décalage vertical
            cell_size - taille d'une cellule
        """
        for row_i, row in enumerate(quadrant):
            for col_i, cell in enumerate(row):
                x1 = x_offset + col_i * cell_size
                y1 = y_offset + row_i * cell_size
                self.canvas.create_rectangle(
                    x1, y1,
                    x1 + cell_size,
                    y1 + cell_size,
                    fill=Render.QUADRANTS_CELLS_COLORS[cell[1]]
                )

    def event_combo(self, event=None):
        """
        procédure : gère le changement de sélection de quadrant
        params :
            event - événement déclencheur
        """
        self.update_selected_quadrants()
        self.draw_quadrants()

    def update_selected_quadrants(self):
        """
        procédure : met à jour les quadrants sélectionnés
        """
        for i, selector in enumerate(self.quadrant_selectors):
            selected_name = selector.get()
            quadrant_index = self.quadrant_names.index(selected_name)
            self.selected_quadrants[i] = [row[:] for row in self.quadrants[quadrant_index]]

    def rotate_right(self, index):
        """
        procédure : fait pivoter un quadrant vers la droite
        params :
            index - index du quadrant à pivoter
        """
        quadrant = self.selected_quadrants[index]
        rotated = [[0 for _ in range(4)] for _ in range(4)]
        for i in range(4):
            for j in range(4):
                rotated[j][3-i] = quadrant[i][j]
        self.selected_quadrants[index] = rotated
        self.draw_quadrants()

    def rotate_left(self, index):
        """
        procédure : fait pivoter un quadrant vers la gauche
        params :
            index - index du quadrant à pivoter
        """
        quadrant = self.selected_quadrants[index]
        rotated = [[0 for _ in range(4)] for _ in range(4)]
        for i in range(4):
            for j in range(4):
                rotated[3-j][i] = quadrant[i][j]
        self.selected_quadrants[index] = rotated
        self.draw_quadrants()
