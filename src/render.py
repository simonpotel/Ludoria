import tkinter as tk


class Render:
    def __init__(self, game):
        self.game = game
        self.root = tk.Tk()  # Fenêtre principale tkinter
        self.root.title("KATARENGA & Co")  # Titre de la fenêtre
        self.root.geometry("800x800")  # Taille de la fenêtre
