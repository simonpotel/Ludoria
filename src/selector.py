import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import os
from src.katerenga.game import Game as Katerenga


class Selector:
    GAMES = ["katerenga", "congress", "isolation"]
    QUADRANTS_COLORS = {
        'Red': 0,
        'Green': 1,
        'Blue': 2,
        'Yellow': 3
    }

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Smart Games: Selector")
        self.setup_initial_ui()
        self.root.mainloop()

    def setup_initial_ui(self):
        tk.Label(self.root, text="Game Name:").pack(pady=10)
        self.entry_game_save = ttk.Combobox(self.root)
        self.entry_game_save['values'] = self.get_saved_games()
        self.entry_game_save.pack(pady=10)
        self.entry_game_save.bind(
            "<<ComboboxSelected>>", self.on_game_save_change)
        self.entry_game_save.bind("<KeyRelease>", self.on_game_save_change)

        tk.Label(self.root, text="Select Game:").pack(pady=10)
        self.game_selection = ttk.Combobox(self.root, state="readonly")
        self.game_selection['values'] = self.GAMES
        self.game_selection.current(0)
        self.game_selection.pack(pady=10)

        tk.Button(self.root, text="Load Game",
                  command=self.load_game).pack(pady=10)

    def get_saved_games(self):
        saves_dir = 'saves'
        if not os.path.exists(saves_dir):
            os.makedirs(saves_dir)
        saved_games = []
        for files in os.listdir(saves_dir):
            if files.endswith('.json'):
                saved_games.append(files.replace('.json', ''))
        return saved_games

    def on_game_save_change(self, event):
        game_save = self.entry_game_save.get()
        if game_save in self.get_saved_games():
            self.game_selection.pack_forget()
        else:
            self.game_selection.pack(pady=10)

    def load_game(self):
        try:
            game_save = self.entry_game_save.get()
            selected_game = self.game_selection.get()
            if not game_save:
                messagebox.showerror("Error", "Please enter a game name.")
                return
            if game_save in self.get_saved_games() or selected_game in self.GAMES:
                self.root.destroy()
                # Red = 0, Green = 1, Blue = 2, Yellow = 3
                quadrant_1 = [[(None, self.QUADRANTS_COLORS['Yellow']), (None, self.QUADRANTS_COLORS['Blue']), (None, self.QUADRANTS_COLORS['Green']), (None, self.QUADRANTS_COLORS['Red'])],
                              [(None, self.QUADRANTS_COLORS['Red']), (None, self.QUADRANTS_COLORS['Green']), (
                                  None, self.QUADRANTS_COLORS['Yellow']), (None, self.QUADRANTS_COLORS['Yellow'])],
                              [(None, self.QUADRANTS_COLORS['Green']), (None, self.QUADRANTS_COLORS['Red']), (
                                  None, self.QUADRANTS_COLORS['Blue']), (None, self.QUADRANTS_COLORS['Blue'])],
                              [(None, self.QUADRANTS_COLORS['Blue']), (None, self.QUADRANTS_COLORS['Yellow']), (None, self.QUADRANTS_COLORS['Red']), (None, self.QUADRANTS_COLORS['Green'])]]

                quadrant_2 = [[(None, self.QUADRANTS_COLORS['Red']), (None, self.QUADRANTS_COLORS['Yellow']), (None, self.QUADRANTS_COLORS['Blue']), (None, self.QUADRANTS_COLORS['Green'])],
                              [(None, self.QUADRANTS_COLORS['Yellow']), (None, self.QUADRANTS_COLORS['Blue']), (
                                  None, self.QUADRANTS_COLORS['Green']), (None, self.QUADRANTS_COLORS['Red'])],
                              [(None, self.QUADRANTS_COLORS['Red']), (None, self.QUADRANTS_COLORS['Green']), (
                                  None, self.QUADRANTS_COLORS['Yellow']), (None, self.QUADRANTS_COLORS['Blue'])],
                              [(None, self.QUADRANTS_COLORS['Blue']), (None, self.QUADRANTS_COLORS['Red']), (None, self.QUADRANTS_COLORS['Yellow']), (None, self.QUADRANTS_COLORS['Green'])]]

                quadrant_3 = [[(None, self.QUADRANTS_COLORS['Green']), (None, self.QUADRANTS_COLORS['Blue']), (None, self.QUADRANTS_COLORS['Yellow']), (None, self.QUADRANTS_COLORS['Red'])],
                              [(None, self.QUADRANTS_COLORS['Yellow']), (None, self.QUADRANTS_COLORS['Red']), (
                                  None, self.QUADRANTS_COLORS['Green']), (None, self.QUADRANTS_COLORS['Blue'])],
                              [(None, self.QUADRANTS_COLORS['Red']), (None, self.QUADRANTS_COLORS['Yellow']), (
                                  None, self.QUADRANTS_COLORS['Blue']), (None, self.QUADRANTS_COLORS['Green'])],
                              [(None, self.QUADRANTS_COLORS['Green']), (None, self.QUADRANTS_COLORS['Blue']), (None, self.QUADRANTS_COLORS['Red']), (None, self.QUADRANTS_COLORS['Yellow'])]]

                quadrant_4 = [[(None, self.QUADRANTS_COLORS['Yellow']), (None, self.QUADRANTS_COLORS['Red']), (None, self.QUADRANTS_COLORS['Blue']), (None, self.QUADRANTS_COLORS['Green'])],
                              [(None, self.QUADRANTS_COLORS['Blue']), (None, self.QUADRANTS_COLORS['Yellow']), (
                                  None, self.QUADRANTS_COLORS['Green']), (None, self.QUADRANTS_COLORS['Red'])],
                              [(None, self.QUADRANTS_COLORS['Green']), (None, self.QUADRANTS_COLORS['Blue']), (
                                  None, self.QUADRANTS_COLORS['Red']), (None, self.QUADRANTS_COLORS['Yellow'])],
                              [(None, self.QUADRANTS_COLORS['Red']), (None, self.QUADRANTS_COLORS['Green']), (None, self.QUADRANTS_COLORS['Yellow']), (None, self.QUADRANTS_COLORS['Blue'])]]

                quadrant_5 = [[(None, self.QUADRANTS_COLORS['Blue']), (None, self.QUADRANTS_COLORS['Green']), (None, self.QUADRANTS_COLORS['Red']), (None, self.QUADRANTS_COLORS['Yellow'])],
                              [(None, self.QUADRANTS_COLORS['Red']), (None, self.QUADRANTS_COLORS['Yellow']), (
                                  None, self.QUADRANTS_COLORS['Blue']), (None, self.QUADRANTS_COLORS['Green'])],
                              [(None, self.QUADRANTS_COLORS['Green']), (None, self.QUADRANTS_COLORS['Red']), (
                                  None, self.QUADRANTS_COLORS['Yellow']), (None, self.QUADRANTS_COLORS['Blue'])],
                              [(None, self.QUADRANTS_COLORS['Yellow']), (None, self.QUADRANTS_COLORS['Blue']), (None, self.QUADRANTS_COLORS['Green']), (None, self.QUADRANTS_COLORS['Red'])]]

                quadrant_6 = [[(None, self.QUADRANTS_COLORS['Green']), (None, self.QUADRANTS_COLORS['Red']), (None, self.QUADRANTS_COLORS['Yellow']), (None, self.QUADRANTS_COLORS['Blue'])],
                              [(None, self.QUADRANTS_COLORS['Yellow']), (None, self.QUADRANTS_COLORS['Blue']), (
                                  None, self.QUADRANTS_COLORS['Red']), (None, self.QUADRANTS_COLORS['Green'])],
                              [(None, self.QUADRANTS_COLORS['Blue']), (None, self.QUADRANTS_COLORS['Green']), (
                                  None, self.QUADRANTS_COLORS['Yellow']), (None, self.QUADRANTS_COLORS['Red'])],
                              [(None, self.QUADRANTS_COLORS['Red']), (None, self.QUADRANTS_COLORS['Yellow']), (None, self.QUADRANTS_COLORS['Blue']), (None, self.QUADRANTS_COLORS['Green'])]]

                match selected_game:
                    case "katerenga":
                        Katerenga(game_save, [quadrant_1, quadrant_2, quadrant_3, quadrant_4])
                    case Else:
                        messagebox.showerror("Error", "Game not defined.")
                        exit()
                self.ask_replay()
            else:
                messagebox.showerror("Error", "Please select a valid game.")
        except ValueError:
            messagebox.showerror("Error", "Please enter a correct value.")

    def ask_replay(self):
        replay = messagebox.askyesno(
            "Smart Games: Selector", "Do you want to replay a new game ?")
        if replay:
            self.__init__()
