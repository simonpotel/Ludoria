import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from src.utils.logger import Logger


class Render:
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
        Logger.info("Render", "Initializing game renderer")
        self.game = game
        self.canvas_size = canvas_size
        self.board_size = 10  # taille du board
        self.root = tk.Tk()
        self.root.title(f"Smart Games: {game.game_save}")

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
            width=canvas_size,
            height=canvas_size
        )
        self.canvas.pack()

        self.load_images()  # charge les images des pièces
        self.render_board()  # rendu du plateau

        self.canvas.bind("<Button-1>", self.handle_click)

        self.root.update()
        window_width = self.root.winfo_reqwidth()
        window_height = self.root.winfo_reqheight()
        self.root.geometry(f"{window_width}x{window_height}")
        Logger.success("Render", "Game renderer initialized successfully")

    def load_images(self):
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
        Logger.info("Render", f"Updating info label: {text}")
        self.info_label.config(text=text)
        self.root.update()

    def render_board(self):
        Logger.board("Render", "Rendering game board")
        self.canvas.delete("all")  # efface tout ce qui est dans le canvas
        cell_size = self.canvas_size // self.board_size

        for row_i, row in enumerate(self.game.board.board):
            for col_i, cell in enumerate(row):
                color = self.QUADRANTS_CELLS_COLORS[cell[1]]
                x1 = col_i * cell_size
                y1 = row_i * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size

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

                if hasattr(self.game, 'selected_piece') and self.game.selected_piece == (row_i, col_i):
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline='blue', width=3)

        Logger.success("Render", "Game board rendered successfully")

    def handle_click(self, event):
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
