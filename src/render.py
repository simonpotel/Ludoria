import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from src.utils.logger import Logger


class Render:
    """
    classe : gère l'affichage graphique du jeu
    """
    # couleurs des cellules à l'intérieur des quadrants en fonction de leur index
    QUADRANTS_CELLS_COLORS = {
        0: 'red',
        1: 'green', 
        2: 'blue',
        3: 'yellow', 
        4: 'white', 
        5: 'black', 
        None: 'grey'
    }

    def __init__(self, game, canvas_size=600):
        """
        procédure : initialise l'interface graphique
        params :
            game - instance du jeu
            canvas_size - taille du canvas en pixels
        """
        Logger.info("Render", "Initializing game renderer")
        self.game = game
        self.canvas_size = canvas_size
        self.board_size = 10  # taille du board
        self._setup_window()
        self._setup_interface()
        self.load_images()  # charge les images des pièces
        self.render_board()  # rendu du plateau
        self._setup_events()
        self._center_window()
        Logger.success("Render", "Game renderer initialized successfully")

    def _setup_window(self):
        """
        procédure : configure la fenêtre principale
        """
        self.root = tk.Tk()
        self.root.title(f"Smart Games: {self.game.game_save}")

    def _setup_interface(self):
        """
        procédure : configure les éléments de l'interface
        """
        main_frame = tk.Frame(self.root)
        main_frame.pack(padx=10, pady=10)

        self.info_label = tk.Label(
            main_frame,
            text="",
            font=('Arial', 12),
            pady=10
        )
        self.info_label.pack()

        if self.game.is_network_game:
            self.game.setup_status_display(main_frame)

        self.canvas = tk.Canvas(
            main_frame,
            width=self.canvas_size,
            height=self.canvas_size
        )
        self.canvas.pack()

    def _setup_events(self):
        """
        procédure : configure les événements
        """
        self.canvas.bind("<Button-1>", self.handle_click)

    def _center_window(self):
        """
        procédure : centre la fenêtre à l'écran
        """
        self.root.update()
        window_width = self.root.winfo_reqwidth()
        window_height = self.root.winfo_reqheight()
        self.root.geometry(f"{window_width}x{window_height}")

    def load_images(self):
        """
        procédure : charge les images des pièces
        """
        Logger.info("Render", "Loading game piece images")
        self.images = {}
        cell_size = self.canvas_size // self.board_size

        try:
            for player in [0, 1]:
                image = Image.open(f"assets/towns/{player}_tower.png")
                aspect_ratio = image.width / image.height
                width = int(cell_size * aspect_ratio)
                height = cell_size - 10
                resized_image = image.resize((width, height), Image.LANCZOS)
                self.images[f"tower_player_{player}"] = ImageTk.PhotoImage(resized_image)
                Logger.success("Render", f"Successfully loaded tower image for player {player}")
        except Exception as e:
            Logger.error("Render", f"Failed to load game piece images: {str(e)}")
            raise

    def edit_info_label(self, text):
        """
        procédure : met à jour le texte d'information
        params :
            text - nouveau texte à afficher
        """
        Logger.info("Render", f"Updating info label: {text}")
        self.info_label.config(text=text)
        self.root.update()

    def render_board(self):
        """
        procédure : dessine le plateau de jeu
        """
        Logger.board("Render", "Rendering game board")
        self.canvas.delete("all")  # efface tout ce qui est dans le canvas
        cell_size = self.canvas_size // self.board_size

        for row_i, row in enumerate(self.game.board.board):
            for col_i, cell in enumerate(row):
                self._draw_cell(row_i, col_i, cell, cell_size)

        Logger.success("Render", "Game board rendered successfully")

    def _draw_cell(self, row, col, cell, cell_size):
        """
        procédure : dessine une cellule du plateau
        params :
            row - numéro de ligne
            col - numéro de colonne
            cell - contenu de la cellule
            cell_size - taille d'une cellule
        """
        x1, y1 = col * cell_size, row * cell_size
        x2, y2 = x1 + cell_size, y1 + cell_size

        self.canvas.create_rectangle(x1, y1, x2, y2, fill=self.QUADRANTS_CELLS_COLORS[cell[1]])

        if cell[0] is not None:
            piece = "tower"
            player = cell[0]
            image_key = f"{piece}_player_{player}"
            self.canvas.create_image(
                x1 + cell_size // 2,
                y1 + cell_size // 2,
                image=self.images[image_key]
            )

        if hasattr(self.game, 'selected_piece') and self.game.selected_piece == (row, col):
            self.canvas.create_rectangle(x1, y1, x2, y2, outline='blue', width=3)

    def handle_click(self, event):
        """
        procédure : gère les clics sur le plateau
        params :
            event - événement de clic
        """
        cell_size = self.canvas_size // self.board_size
        row = event.y // cell_size
        col = event.x // cell_size

        Logger.game("Render", f"Handling click at position ({row},{col})")

        if 0 <= row < self.board_size and 0 <= col < self.board_size:
            if self.game.can_play():
                if not self.game.on_click(row, col):
                    Logger.warning("Render", f"Invalid click at position ({row},{col})")
                    return
                self.render_board()
                Logger.success("Render", f"Successfully processed click at ({row},{col})")
        else:
            Logger.warning("Render", f"Click outside board boundaries at ({row},{col})")
