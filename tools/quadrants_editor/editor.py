import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import json
import os
from src.utils.logger import Logger
from tools.quadrants_editor.validator import QuadrantValidator

class QuadrantEditor:
    COLORS = ['red', 'green', 'blue', 'yellow']
    GRID_SIZE = 4
    CELL_SIZE = 80
    COLOR_MAP = {0: 'red', 1: 'green', 2: 'blue', 3: 'yellow'}
    REVERSE_COLOR_MAP = {'red': 0, 'green': 1, 'blue': 2, 'yellow': 3}
    BUTTON_STYLE = {'font': ('Helvetica', 10), 'borderwidth': 2, 'relief': 'raised', 'cursor': 'hand2'}

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Quadrant Editor")
        self.root.configure(bg='#f0f0f0')
        
        self.style = ttk.Style()
        self.style.configure('TLabelframe', background='#f0f0f0')
        self.style.configure('TLabelframe.Label', background='#f0f0f0', font=('Helvetica', 10, 'bold'))
        self.style.configure('TCombobox', background='white', font=('Helvetica', 10))
        
        self.current_color = tk.StringVar(value=self.COLORS[0])
        self.grid = [[None for _ in range(self.GRID_SIZE)] for _ in range(self.GRID_SIZE)]
        self.validator = QuadrantValidator()
        self.load_quadrants_config()
        self.setup_ui()

    def load_quadrants_config(self):
        try:
            with open('configs/quadrants.json', 'r') as f:
                self.quadrants_config = json.load(f)
        except:
            self.quadrants_config = {}

    def save_quadrants_config(self):
        try:
            with open('configs/quadrants.json', 'w') as f:
                json.dump(self.quadrants_config, f, indent=2)
            return True
        except Exception as e:
            Logger.error("QuadrantEditor", f"Failed to save quadrants config: {str(e)}")
            return False

    def convert_from_storage_format(self, stored_grid):
        # convertit le format de stockage en format d'édition
        converted_grid = []
        for row in stored_grid:
            converted_row = []
            for cell in row:
                if isinstance(cell, list) and len(cell) == 2 and cell[1] in self.COLOR_MAP:
                    converted_row.append(self.COLOR_MAP[cell[1]])
                else:
                    converted_row.append(None)
            converted_grid.append(converted_row)
        return converted_grid

    def convert_to_storage_format(self, editor_grid):
        # convertit le format d'édition en format de stockage
        converted_grid = []
        for row in editor_grid:
            converted_row = []
            for cell in row:
                if cell in self.REVERSE_COLOR_MAP:
                    converted_row.append([None, self.REVERSE_COLOR_MAP[cell]])
                else:
                    converted_row.append([None, 0])
            converted_grid.append(converted_row)
        return converted_grid

    def setup_ui(self):
        # initialise l'interface utilisateur
        main_frame = tk.Frame(self.root, bg='#f0f0f0', padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')

        left_panel = tk.Frame(main_frame, bg='#f0f0f0')
        left_panel.pack(side=tk.LEFT, padx=(0, 20))

        title_label = tk.Label(left_panel, text="QUADRANT EDITOR", font=('Helvetica', 16, 'bold'),
                             bg='#f0f0f0', fg='#333333')
        title_label.pack(pady=(0, 20))

        self.create_color_selector(left_panel)
        self.create_quadrant_selector(left_panel)

        grid_frame = tk.Frame(main_frame, bg='#f0f0f0')
        grid_frame.pack(side=tk.LEFT)
        
        grid_title = tk.Label(grid_frame, text="QUADRANT GRID", font=('Helvetica', 12, 'bold'),
                            bg='#f0f0f0', fg='#333333')
        grid_title.pack(pady=(0, 10))
        
        self.create_grid(grid_frame)
        self.create_buttons(left_panel)

    def create_color_selector(self, parent):
        # crée le sélecteur de couleurs
        color_frame = ttk.LabelFrame(parent, text="Colors", padding=(10, 5))
        color_frame.pack(fill='x', pady=(0, 10))
        
        for color in self.COLORS:
            frame = tk.Frame(color_frame, bg='#f0f0f0')
            frame.pack(fill='x', pady=2)
            
            rb = tk.Radiobutton(frame, text=color, variable=self.current_color, value=color,
                              bg='#f0f0f0', font=('Helvetica', 10), cursor='hand2')
            rb.pack(side=tk.LEFT)
            
            color_preview = tk.Frame(frame, width=20, height=20, bg=color,
                                   relief='solid', borderwidth=1)
            color_preview.pack(side=tk.RIGHT, padx=5)

    def create_quadrant_selector(self, parent):
        selector_frame = ttk.LabelFrame(parent, text="Load Quadrant", padding=(10, 5))
        selector_frame.pack(fill='x', pady=(0, 10))

        self.quadrant_combo = ttk.Combobox(selector_frame, values=sorted(self.quadrants_config.keys()),
                                         state="readonly", width=30, font=('Helvetica', 10))
        self.quadrant_combo.pack(fill='x', pady=5)
        self.quadrant_combo.bind('<<ComboboxSelected>>', self.on_quadrant_selected)

    def create_grid(self, parent):
        canvas_frame = tk.Frame(parent, bg='white', bd=2, relief='solid', padx=2, pady=2)
        canvas_frame.pack()

        canvas_size = self.GRID_SIZE * self.CELL_SIZE
        self.canvas = tk.Canvas(canvas_frame, width=canvas_size, height=canvas_size,
                              bg='white', bd=0, highlightthickness=0)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.handle_click)
        self.draw_grid()

    def create_buttons(self, parent):
        button_frame = ttk.LabelFrame(parent, text="Actions", padding=(10, 5))
        button_frame.pack(fill='x', pady=(0, 10))
        
        save_frame = tk.Frame(button_frame, bg='#f0f0f0')
        save_frame.pack(fill='x', pady=5)
        
        tk.Label(save_frame, text="Quadrant name:", font=('Helvetica', 10),
                bg='#f0f0f0').pack(anchor='w')
        
        self.save_name = ttk.Entry(save_frame, font=('Helvetica', 10))
        self.save_name.pack(fill='x', pady=(2, 5))
        
        tk.Button(button_frame, text="Save", command=self.save_quadrant,
                 bg='#4CAF50', fg='white', activebackground='#45a049',
                 activeforeground='white', **self.BUTTON_STYLE).pack(fill='x', pady=2)

        tk.Button(button_frame, text="Clear Grid", command=self.clear_grid,
                 bg='#f44336', fg='white', activebackground='#da190b',
                 activeforeground='white', **self.BUTTON_STYLE).pack(fill='x', pady=2)

    def draw_grid(self):
        # dessine la grille avec les couleurs
        self.canvas.delete("all")
        for row in range(self.GRID_SIZE):
            for col in range(self.GRID_SIZE):
                x1, y1 = col * self.CELL_SIZE, row * self.CELL_SIZE
                x2, y2 = x1 + self.CELL_SIZE, y1 + self.CELL_SIZE
                color = self.grid[row][col] or "white"
                
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='#666666', width=1)
                if color != "white":
                    self.canvas.create_line(x1, y1, x2, y1, fill='white', width=1)
                    self.canvas.create_line(x1, y1, x1, y2, fill='white', width=1)

    def handle_click(self, event):
        # gère les clics sur la grille
        col, row = event.x // self.CELL_SIZE, event.y // self.CELL_SIZE
        if 0 <= row < self.GRID_SIZE and 0 <= col < self.GRID_SIZE:
            self.grid[row][col] = self.current_color.get()
            self.draw_grid()

    def on_quadrant_selected(self, event=None):
        selected = self.quadrant_combo.get()
        if selected in self.quadrants_config:
            self.grid = self.convert_from_storage_format(self.quadrants_config[selected])
            self.draw_grid()
            self.save_name.delete(0, tk.END)
            self.save_name.insert(0, selected)

    def save_quadrant(self):
        if not self.validator.is_valid_quadrant(self.grid):
            messagebox.showerror("Error", "Invalid quadrant configuration")
            return

        name = self.save_name.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a name for the quadrant")
            return

        self.quadrants_config[name] = self.convert_to_storage_format(self.grid)
        if self.save_quadrants_config():
            self.quadrant_combo['values'] = sorted(self.quadrants_config.keys())
            messagebox.showinfo("Success", f"Quadrant saved as '{name}'")
        else:
            messagebox.showerror("Error", "Failed to save quadrant")

    def clear_grid(self):
        self.grid = [[None for _ in range(self.GRID_SIZE)] for _ in range(self.GRID_SIZE)]
        self.draw_grid()

    def run(self):
        # centre la fenêtre sur l'écran
        self.root.update_idletasks()
        width, height = self.root.winfo_width(), self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'+{x}+{y}')
        self.root.mainloop() 