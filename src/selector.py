import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from pathlib import Path
import json
from src.katerenga.game import Game as Katerenga


class Selector:
    GAMES = ["katerenga", "congress", "isolation"]
    QUADRANTS_COLORS = {
        'Red': 0,
        'Green': 1,
        'Blue': 2,
        'Yellow': 3
    }
    COLOR_MAP = {0: 'red', 1: 'green', 2: 'blue', 3: 'yellow'}

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Smart Games: Selector")
        self.quadrants = self.load_quadrants()
        self.setup_initial_ui()
        self.root.mainloop()

    def load_quadrants(self):
        with open('configs/quadrants.json', 'r') as file:
            quadrants_config = json.load(file)
        quadrants = []
        for key in sorted(quadrants_config.keys(), key=int):
            quadrants.append(quadrants_config[key])
        return quadrants

    def setup_initial_ui(self):
        config_frame = tk.Frame(self.root)
        config_frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")

        tk.Label(config_frame, text="Game Name:").pack(pady=10)
        self.entry_game_save = ttk.Combobox(
            config_frame, values=self.get_saved_games())
        self.entry_game_save.pack(pady=10)
        self.entry_game_save.bind(
            "<<ComboboxSelected>>", self.on_game_save_change)
        self.entry_game_save.bind("<KeyRelease>", self.on_game_save_change)

        tk.Label(config_frame, text="Select Game:").pack(pady=10)
        self.game_selection = ttk.Combobox(
            config_frame, state="readonly", values=self.GAMES)
        self.game_selection.current(0)
        self.game_selection.pack(pady=10)

        tk.Label(config_frame, text="Assign Quadrants:").pack(pady=10)
        self.quadrant_selectors = []
        for i in range(4):
            selector = self.create_quadrant_selector(config_frame, i)
            self.quadrant_selectors.append(selector)

        tk.Button(config_frame, text="Load Game",
                  command=self.load_game).pack(pady=10)

        self.canvas = tk.Canvas(self.root, width=400, height=400)
        self.canvas.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        self.draw_quadrants()

    def create_quadrant_selector(self, parent, index):
        values = [f"{j+1}" for j in range(len(self.quadrants))]
        selector = ttk.Combobox(parent, state="readonly", values=values)
        selector.current(index if index < len(self.quadrants) else 0)
        selector.pack(pady=5)
        selector.bind("<<ComboboxSelected>>", self.event_combo)
        return selector

    def get_saved_games(self):
        saves_dir = Path('saves')
        if not saves_dir.exists():
            saves_dir.mkdir()
        saved_games = []
        for file in saves_dir.glob('*.json'):
            saved_games.append(file.stem)
        return saved_games

    def on_game_save_change(self, event=None):
        game_save = self.entry_game_save.get()
        if game_save in self.get_saved_games():
            self.game_selection.pack_forget()
        else:
            self.game_selection.pack(pady=10)

    def load_game(self):
        game_save = self.entry_game_save.get()
        selected_game = self.game_selection.get()
        if not game_save:
            messagebox.showerror("Error", "Please enter a game name.")
            return
        if game_save in self.get_saved_games() or selected_game in self.GAMES:
            selected_quadrants = []
            for selector in self.quadrant_selectors:
                quadrant_index = int(selector.get()) - 1
                selected_quadrants.append(self.quadrants[quadrant_index])
            self.root.destroy()
            if selected_game == "katerenga":
                Katerenga(game_save, selected_quadrants)
            else:
                messagebox.showerror("Error", "Game not defined.")
                exit()
            self.ask_replay()
        else:
            messagebox.showerror("Error", "Please select a valid game.")

    def ask_replay(self):
        if messagebox.askyesno("Smart Games: Selector", "Do you want to replay a new game?"):
            self.__init__()

    def draw_quadrants(self):
        self.canvas.delete("all")
        quadrant_size = 200
        cell_size = quadrant_size // 4

        for i, selector in enumerate(self.quadrant_selectors):
            quadrant_index = int(selector.get()) - 1
            quadrant = self.quadrants[quadrant_index]
            x_offset = (i % 2) * quadrant_size
            y_offset = (i // 2) * quadrant_size

            for row_i, row in enumerate(quadrant):
                for col_i, cell in enumerate(row):
                    color = self.COLOR_MAP[cell[1]]
                    x1 = x_offset + col_i * cell_size
                    y1 = y_offset + row_i * cell_size
                    x2 = x1 + cell_size
                    y2 = y1 + cell_size
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)

    def event_combo(self, event=None):
        self.draw_quadrants()
