import pygame
import json
from typing import List, Tuple, Optional, Dict, Any
from src.windows.screens.base_screen import BaseScreen
from src.windows.components.image_button import ImageButton
from src.utils.logger import Logger

class QuadrantEditorScreen(BaseScreen):
    """
    classe : gestion de l'éditeur de quadrants du jeu
    """
    
    COLORS: List[str] = ['red', 'green', 'blue', 'yellow']
    GRID_SIZE: int = 4
    CELL_SIZE: int = 70
    COLOR_MAP: Dict[int, str] = {0: 'red', 1: 'green', 2: 'blue', 3: 'yellow'}
    REVERSE_COLOR_MAP: Dict[str, int] = {'red': 0, 'green': 1, 'blue': 2, 'yellow': 3}
    FEEDBACK_MESSAGE_DURATION: int = 180
    
    UI_CONFIG = {
        'button': {
            'width': 200,
            'height': 35,
            'spacing': 5,
            'text_color': (255, 255, 255),
            'nav_width': 35,
            'image_path': "assets/Basic_GUI_Bundle/ButtonsText/ButtonText_Large_GreyOutline_Square.png"
        },
        'panel': {
            'left_margin': 50,
            'spacing': 10,
            'grid_offset': 70
        },
        'colors': {
            'background': (30, 30, 30),
            'text': (255, 255, 255),
            'grid_border': (100, 100, 120),
            'instruction': (200, 200, 200),
            'error': (255, 100, 100),
            'success': (100, 255, 100),
            'input_inactive': (200, 200, 200)
        }
    }

    def __init__(self, width: int = 1280, height: int = 720, title: str = "Ludoria - Quadrant Editor"):
        """
        fonction : initialise l'éditeur de quadrants
        params :
            width - largeur de la fenêtre en pixels
            height - hauteur de la fenêtre en pixels
            title - titre de la fenêtre
        """
        super().__init__(width, height, title)
        
        self.current_color: str = self.COLORS[0]
        self.grid: List[List[Optional[str]]] = [[None for _ in range(self.GRID_SIZE)] for _ in range(self.GRID_SIZE)]
        self.quadrants_config: Dict[str, Any] = {}
        self.quadrant_names: List[str] = []
        self.selected_quadrant_index: int = 0
        self.save_name: str = ""
        
        self.color_buttons: List[ImageButton] = []
        self.grid_rects: List[List[pygame.Rect]] = []
        self.load_button: Optional[ImageButton] = None
        self.save_button: Optional[ImageButton] = None
        self.clear_button: Optional[ImageButton] = None
        self.back_button: Optional[ImageButton] = None
        self.prev_quadrant_button: Optional[ImageButton] = None
        self.next_quadrant_button: Optional[ImageButton] = None
        
        self.name_input_rect: Optional[pygame.Rect] = None
        self.name_input_active: bool = False

        self.title_font: Optional[pygame.font.Font] = None
        self.label_font: Optional[pygame.font.Font] = None
        self.button_font: Optional[pygame.font.Font] = None
        self.input_text_font: Optional[pygame.font.Font] = None
        self.info_font: Optional[pygame.font.Font] = None
        self.feedback_font: Optional[pygame.font.Font] = None

        self.instruction_text_content: str = "Each color must appear exactly 4 times."
        self.instruction_text_surface: Optional[pygame.Surface] = None
        self.instruction_text_pos: Tuple[int, int] = (0, 0)

        self.feedback_message: Optional[str] = None
        self.feedback_message_surface: Optional[pygame.Surface] = None
        self.feedback_message_pos: Tuple[int, int] = (0, 0)
        self.feedback_message_timer: int = 0
        self.feedback_message_color: Tuple[int, int, int] = (255, 255, 255)
        self.feedback_message_base_y: int = 0
        
        self.background_image: Optional[pygame.Surface] = None
        
        self.setup_fonts()
        self.setup_ui_elements()
        self.load_quadrants_config()
        
    def setup_fonts(self):
        """
        fonction : initialise les polices de caractères
        """
        self.title_font = self.font_manager.get_font(72)
        self.label_font = self.font_manager.get_font(24)
        self.button_font = self.font_manager.get_font(20)
        self.input_text_font = self.font_manager.get_font(22)
        self.info_font = self.font_manager.get_font(18)
        self.feedback_font = self.font_manager.get_font(22)

    def setup_ui_elements(self):
        """
        fonction : initialise les éléments de l'interface utilisateur
        """
        self.setup_background()
        self.setup_color_buttons()
        self.setup_grid()
        self.setup_navigation()
        self.setup_input_area()
        self.setup_action_buttons()
        self.setup_instruction_text()
        
    def setup_background(self):
        try:
            theme = self.theme_manager.current_theme
            bg_path = f"assets/{theme}/background.png"
            self.background_image = pygame.image.load(bg_path).convert_alpha()
            self.background_image = pygame.transform.scale(self.background_image, (self.width, self.height))
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            self.background_image.blit(overlay, (0, 0))
        except Exception as e:
            Logger.error("QuadrantEditorScreen", f"Failed to load background: {e}")
            self.background_image = None

    def setup_color_buttons(self):
        btn_config = self.UI_CONFIG['button']
        panel_config = self.UI_CONFIG['panel']
        
        current_y = self.navbar_height + 120
        self.colors_label_text = "COLORS:"
        self.colors_label_pos = (panel_config['left_margin'], current_y)
        current_y += self.label_font.get_height() + panel_config['spacing']

        self.color_buttons = []
        for i, color_name in enumerate(self.COLORS):
            btn = self.create_button(
                panel_config['left_margin'],
                current_y + i * (btn_config['height'] + btn_config['spacing']),
                color_name.upper(),
                lambda c=color_name: self.set_current_color(c)
            )
            self.color_buttons.append(btn)

    def setup_grid(self):
        panel_config = self.UI_CONFIG['panel']
        grid_start_x = panel_config['left_margin'] + self.UI_CONFIG['button']['width'] + panel_config['grid_offset']
        
        self.grid_label_text = "GRID:"
        self.grid_label_pos = (grid_start_x, self.colors_label_pos[1])
        grid_start_y = self.grid_label_pos[1] + self.label_font.get_height() + panel_config['spacing']

        self.grid_rects = []
        for r in range(self.GRID_SIZE):
            row_rects = []
            for c in range(self.GRID_SIZE):
                rect = pygame.Rect(
                    grid_start_x + c * self.CELL_SIZE,
                    grid_start_y + r * self.CELL_SIZE,
                    self.CELL_SIZE,
                    self.CELL_SIZE
                )
                row_rects.append(rect)
            self.grid_rects.append(row_rects)

    def setup_navigation(self):
        """
        fonction : configure la navigation des quadrants
        """
        btn_config = self.UI_CONFIG['button']
        panel_config = self.UI_CONFIG['panel']
        grid_width = self.GRID_SIZE * self.CELL_SIZE
        right_panel_x = panel_config['left_margin'] + self.UI_CONFIG['button']['width'] + panel_config['grid_offset'] + grid_width + panel_config['grid_offset']

        self.quadrant_label_text = "QUADRANT:"
        self.quadrant_label_pos = (right_panel_x, self.grid_label_pos[1])
        nav_y = self.quadrant_label_pos[1] + self.label_font.get_height() + panel_config['spacing']

        self.prev_quadrant_button = self.create_button(right_panel_x, nav_y, "<", self.prev_quadrant, btn_config['nav_width'])
        
        num_display_x = right_panel_x + btn_config['nav_width'] + panel_config['spacing']
        self.quadrant_num_display_pos = (num_display_x, nav_y + (btn_config['height'] - self.label_font.get_height()) // 2)
        
        name_display_width = btn_config['width'] - (2 * btn_config['nav_width'] + 2 * panel_config['spacing'])
        next_button_x = num_display_x + name_display_width + panel_config['spacing']
        self.next_quadrant_button = self.create_button(next_button_x, nav_y, ">", self.next_quadrant, btn_config['nav_width'])

        load_button_y = nav_y + btn_config['height'] + btn_config['spacing']
        self.load_button = self.create_button(right_panel_x, load_button_y, "LOAD QUADRANT", self.load_selected_quadrant)

    def setup_input_area(self):
        btn_config = self.UI_CONFIG['button']
        panel_config = self.UI_CONFIG['panel']
        
        name_y = self.load_button.rect.bottom + panel_config['spacing'] * 2
        self.name_label_text = "NAME:"
        self.name_label_pos = (self.load_button.rect.x, name_y)
        
        name_label_width = self.label_font.size(self.name_label_text)[0]
        input_x = self.name_label_pos[0] + name_label_width + panel_config['spacing']
        input_width = max(50, btn_config['width'] - name_label_width - panel_config['spacing'])
        
        self.name_input_rect = pygame.Rect(input_x, name_y, input_width, btn_config['height'])
        self.name_input_active = False

    def setup_action_buttons(self):
        btn_config = self.UI_CONFIG['button']
        panel_config = self.UI_CONFIG['panel']
        
        save_y = self.name_input_rect.bottom + btn_config['spacing']
        self.save_button = self.create_button(self.load_button.rect.x, save_y, "SAVE", self.save_quadrant)
        
        clear_y = self.height - btn_config['height'] * 2 - btn_config['spacing'] * 2
        self.clear_button = self.create_button(panel_config['left_margin'], clear_y, "CLEAR", self.clear_grid)
        
        back_y = clear_y + btn_config['height'] + btn_config['spacing']
        self.back_button = self.create_button(panel_config['left_margin'], back_y, "BACK", self.go_back)

    def setup_instruction_text(self):
        self.instruction_text_content = "Each color must appear exactly 4 times."
        if self.info_font:
            self.instruction_text_surface = self.info_font.render(
                self.instruction_text_content,
                True,
                self.UI_CONFIG['colors']['instruction']
            )
            instruction_x = (self.width - self.instruction_text_surface.get_width()) // 2
            instruction_y = self.height - self.instruction_text_surface.get_height() - 15
            self.instruction_text_pos = (instruction_x, instruction_y)

        title_height = self.title_font.get_height() if self.title_font else 72
        self.feedback_message_base_y = self.navbar_height + 20 + title_height + 15

    def create_button(self, x: int, y: int, text: str, callback, width: Optional[int] = None) -> ImageButton:
        """
        fonction : crée un bouton avec les paramètres spécifiés
        """
        btn_config = self.UI_CONFIG['button']
        return ImageButton(
            x, y,
            width or btn_config['width'],
            btn_config['height'],
            text,
            callback,
            bg_image_path=btn_config['image_path'],
            font=self.button_font,
            text_color=btn_config['text_color']
        )

    def load_quadrants_config(self):
        """
        fonction : charge la configuration des quadrants depuis le fichier JSON
        """
        try:
            with open('configs/quadrants.json', 'r') as f:
                self.quadrants_config = json.load(f)
            self.update_quadrant_list()
            Logger.info("QuadrantEditorScreen", f"Loaded {len(self.quadrant_names)} quadrants")
        except FileNotFoundError:
            Logger.warning("QuadrantEditorScreen", "quadrants.json not found. A new file will be created on save.")
            self.quadrants_config = {}
            self.quadrant_names = []
            self.show_feedback_message("Warning: quadrants.json not found. Will be created on save.", is_error=False)
        except json.JSONDecodeError as e:
            Logger.error("QuadrantEditorScreen", f"Failed to parse quadrants.json: {str(e)}")
            self.quadrants_config = {}
            self.quadrant_names = []
            self.show_feedback_message("Error: Could not parse quadrants_config.json. Check format.", is_error=True)
        except Exception as e:
            Logger.error("QuadrantEditorScreen", f"Failed to load quadrants config: {str(e)}")
            self.quadrants_config = {}
            self.quadrant_names = []
            self.show_feedback_message("Error: Could not load quadrants_config.json", is_error=True)
            
    def save_quadrants_config(self) -> bool:
        """
        fonction : sauvegarde la configuration des quadrants dans le fichier JSON
        retour : True si la sauvegarde a réussi, False sinon
        """
        try:
            with open('configs/quadrants.json', 'w') as f:
                json.dump(self.quadrants_config, f, indent=2)
            Logger.info("QuadrantEditorScreen", "Quadrants configuration saved successfully")
            return True
        except Exception as e:
            Logger.error("QuadrantEditorScreen", f"Failed to save quadrants config: {str(e)}")
            return False
            
    def convert_from_storage_format(self, stored_grid: List[List[List[Optional[Any]]]]) -> List[List[Optional[str]]]:
        """
        fonction : convertit une grille du format de stockage vers le format d'édition
        params :
            stored_grid - grille au format de stockage
        retour : grille au format d'édition
        """
        converted_grid: List[List[Optional[str]]] = []
        for row in stored_grid:
            converted_row: List[Optional[str]] = []
            for cell in row:
                if isinstance(cell, list) and len(cell) == 2 and isinstance(cell[1], int) and cell[1] in self.COLOR_MAP:
                    converted_row.append(self.COLOR_MAP[cell[1]])
                else:
                    converted_row.append(None)
            converted_grid.append(converted_row)
        return converted_grid
        
    def convert_to_storage_format(self, editor_grid: List[List[Optional[str]]]) -> List[List[List[Optional[Any]]]]:
        """
        fonction : convertit une grille du format d'édition vers le format de stockage
        params :
            editor_grid - grille au format d'édition
        retour : grille au format de stockage
        """
        converted_grid: List[List[List[Optional[Any]]]] = []
        for row in editor_grid:
            converted_row: List[List[Optional[Any]]] = []
            for cell_color_name in row:
                if cell_color_name in self.REVERSE_COLOR_MAP:
                    converted_row.append([None, self.REVERSE_COLOR_MAP[cell_color_name]])
                else:
                    converted_row.append([None, 0])
            converted_grid.append(converted_row)
        return converted_grid
        
    def is_valid_quadrant(self, grid: List[List[Optional[str]]]) -> bool:
        """
        fonction : vérifie si la configuration de la grille est valide
        params :
            grid - grille à vérifier
        retour : True si la grille est valide, False sinon
        """
        for row in grid:
            for cell in row:
                if cell is None:
                    return False
        return True
        
    def set_current_color(self, color: str):
        """
        fonction : définit la couleur active pour la grille
        params :
            color - nom de la couleur à utiliser
        """
        self.current_color = color
        Logger.info("QuadrantEditorScreen", f"Color set to {color}")
        
    def prev_quadrant(self):
        """
        fonction : sélectionne le quadrant précédent
        """
        if not self.quadrant_names:
            return
            
        self.selected_quadrant_index = (self.selected_quadrant_index - 1) % len(self.quadrant_names)
        Logger.info("QuadrantEditorScreen", f"Moved to previous quadrant, index: {self.selected_quadrant_index}")
            
    def next_quadrant(self):
        """
        fonction : sélectionne le quadrant suivant
        """
        if not self.quadrant_names:
            return
            
        self.selected_quadrant_index = (self.selected_quadrant_index + 1) % len(self.quadrant_names)
        Logger.info("QuadrantEditorScreen", f"Moved to next quadrant, index: {self.selected_quadrant_index}")
            
    def load_selected_quadrant(self):
        """
        fonction : charge le quadrant sélectionné dans la grille
        """
        if not self.quadrant_names:
            self.show_feedback_message("Info: No quadrants available to load.", is_error=False)
            Logger.info("QuadrantEditorScreen", "Load attempt with no quadrant names available.")
            return

        if 0 <= self.selected_quadrant_index < len(self.quadrant_names):
            quadrant_name_to_load = self.quadrant_names[self.selected_quadrant_index]
            if quadrant_name_to_load in self.quadrants_config:
                self.grid = self.convert_from_storage_format(self.quadrants_config[quadrant_name_to_load])
                self.save_name = quadrant_name_to_load
                Logger.info("QuadrantEditorScreen", f"Loaded quadrant: {quadrant_name_to_load}")
                self.show_feedback_message(f"Quadrant '{quadrant_name_to_load}' loaded.", is_error=False)
            else:
                Logger.error("QuadrantEditorScreen", f"Attempted to load non-existent quadrant '{quadrant_name_to_load}' from config.")
                self.show_feedback_message(f"Error: Quadrant '{quadrant_name_to_load}' not found in config.", is_error=True)
        else:
            Logger.warning("QuadrantEditorScreen", f"Load attempt with invalid index: {self.selected_quadrant_index}. Clamping.")
            self.selected_quadrant_index = 0
            self.show_feedback_message("Error: Invalid quadrant selection index.", is_error=True)
            
    def update_quadrant_list(self, new_quadrant_name: Optional[str] = None):
        """
        fonction : met à jour la liste des quadrants
        params :
            new_quadrant_name - nom du nouveau quadrant à sélectionner (optionnel)
        """
        self.quadrant_names = sorted(self.quadrants_config.keys())
        if new_quadrant_name is not None and new_quadrant_name in self.quadrant_names:
            self.selected_quadrant_index = self.quadrant_names.index(new_quadrant_name)
        elif self.quadrant_names:
            self.selected_quadrant_index = min(self.selected_quadrant_index, len(self.quadrant_names) - 1)
        else:
            self.selected_quadrant_index = 0
            
    def save_quadrant(self):
        """
        fonction : sauvegarde la configuration actuelle de la grille
        """
        if not self.is_valid_quadrant(self.grid):
            Logger.warning("QuadrantEditorScreen", "Save attempt failed: invalid quadrant configuration.")
            self.show_feedback_message("Error: All grid cells must be filled to save.", is_error=True)
            return
            
        current_save_name = self.save_name.strip()
        if not current_save_name:
            Logger.warning("QuadrantEditorScreen", "Save attempt failed: no name provided.")
            self.show_feedback_message("Error: Quadrant name cannot be empty.", is_error=True)
            return
            
        self.quadrants_config[current_save_name] = self.convert_to_storage_format(self.grid)
        if self.save_quadrants_config():
            self.update_quadrant_list(current_save_name)
            Logger.info("QuadrantEditorScreen", f"Quadrant saved as: {current_save_name}")
            self.show_feedback_message(f"Quadrant '{current_save_name}' saved successfully!", is_error=False)
        else:
            self.show_feedback_message(f"Error: Failed to save quadrant '{current_save_name}' to file.", is_error=True)
            
    def clear_grid(self):
        """
        fonction : réinitialise la grille d'édition
        """
        self.grid = [[None for _ in range(self.GRID_SIZE)] for _ in range(self.GRID_SIZE)]
        self.save_name = ""
        Logger.info("QuadrantEditorScreen", "Grid cleared")
        self.show_feedback_message("Grid cleared.", is_error=False)
        
    def go_back(self):
        """
        fonction : retourne à l'écran de sélection du mode
        """
        from src.windows.screens.game_selection.mode_selection import ModeSelectionScreen
        self.next_screen = ModeSelectionScreen
        self.running = False
        Logger.info("QuadrantEditorScreen", "Returning to ModeSelectionScreen.")
        
    def handle_screen_events(self, event: pygame.event.Event):
        """
        fonction : gère les événements de l'écran
        params :
            event - événement Pygame à traiter
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.handle_mouse_click(event.pos)
        elif event.type == pygame.KEYDOWN and self.name_input_active:
            self.handle_keyboard_input(event)
            
        self.handle_button_events(event)
            
    def handle_mouse_click(self, pos: Tuple[int, int]):
        """
        fonction : gère les clics de souris
        params :
            pos - position du clic
        """
        if self.handle_grid_click(pos):
            return
            
        if self.name_input_rect and self.name_input_rect.collidepoint(pos):
            self.name_input_active = True
            Logger.debug("QuadrantEditorScreen", "Name input field activated.")
        else:
            if self.name_input_active:
                Logger.debug("QuadrantEditorScreen", "Name input field deactivated.")
            self.name_input_active = False
            
    def handle_grid_click(self, pos: Tuple[int, int]) -> bool:
        """
        fonction : gère les clics sur la grille
        params :
            pos - position du clic
        retour : True si un clic sur la grille a été traité
        """
        for r, row_of_rects in enumerate(self.grid_rects):
            for c, cell_rect in enumerate(row_of_rects):
                if cell_rect.collidepoint(pos):
                    self.grid[r][c] = self.current_color
                    return True
        return False
        
    def handle_keyboard_input(self, event: pygame.event.Event):
        """
        fonction : gère les entrées clavier
        params :
            event - événement clavier à traiter
        """
        if event.key == pygame.K_BACKSPACE:
            self.save_name = self.save_name[:-1]
        elif event.key == pygame.K_RETURN:
            self.name_input_active = False
            Logger.debug("QuadrantEditorScreen", "Name input field deactivated by Enter key.")
        elif event.unicode.isprintable():
            if self.input_text_font and self.input_text_font.size(self.save_name + event.unicode)[0] < self.name_input_rect.width - 10:
                self.save_name += event.unicode
                
    def handle_button_events(self, event: pygame.event.Event):
        """
        fonction : gère les événements des boutons
        params :
            event - événement à traiter
        """
        buttons = [
            *self.color_buttons,
            self.prev_quadrant_button,
            self.next_quadrant_button,
            self.load_button,
            self.save_button,
            self.clear_button,
            self.back_button
        ]
        
        for button in buttons:
            if button:
                button.handle_event(event)
                
    def update_screen(self, mouse_pos: Tuple[int, int]):
        """
        fonction : met à jour l'état des éléments de l'écran
        params :
            mouse_pos - position actuelle de la souris
        """
        self.update_feedback_message()
        self.update_buttons(mouse_pos)
            
    def update_feedback_message(self):
        """
        fonction : met à jour l'état du message de feedback
        """
        if self.feedback_message_timer > 0:
            self.feedback_message_timer -= 1
            if self.feedback_message_timer == 0:
                self.feedback_message_surface = None
                self.feedback_message = None
                
    def update_buttons(self, mouse_pos: Tuple[int, int]):
        """
        fonction : met à jour l'état des boutons
        params :
            mouse_pos - position actuelle de la souris
        """
        buttons = [
            *self.color_buttons,
            self.prev_quadrant_button,
            self.next_quadrant_button,
            self.load_button,
            self.save_button,
            self.clear_button,
            self.back_button
        ]
        
        for button in buttons:
            if button:
                button.check_hover(mouse_pos)
                
    def draw_screen(self):
        """
        fonction : dessine les éléments de l'écran
        """
        self.draw_background()
        self.draw_title()
        self.draw_labels()
        self.draw_buttons()
        self.draw_grid()
        self.draw_quadrant_navigation()
        self.draw_name_input()
        self.draw_instruction()
        self.draw_feedback()
            
    def draw_background(self):
        """
        fonction : dessine l'arrière-plan
        """
        if self.background_image:
            self.screen.blit(self.background_image, (0, 0))
        else:
            self.screen.fill(self.UI_CONFIG['colors']['background'])
            
    def draw_title(self):
        """
        fonction : dessine le titre
        """
        if self.title_font:
            title_text_surface = self.title_font.render("QUADRANT EDITOR", True, self.UI_CONFIG['colors']['text'])
            title_x: int = (self.width - title_text_surface.get_width()) // 2
            title_y: int = self.navbar_height + 20 
            self.screen.blit(title_text_surface, (title_x, title_y))
            
    def draw_labels(self):
        """
        fonction : dessine les étiquettes
        """
        if not self.label_font:
            return
            
        labels = [
            (self.colors_label_text, self.colors_label_pos),
            (self.grid_label_text, self.grid_label_pos),
            (self.quadrant_label_text, self.quadrant_label_pos)
        ]
        
        for text, pos in labels:
            label_surface = self.label_font.render(text, True, self.UI_CONFIG['colors']['text'])
            self.screen.blit(label_surface, pos)
            
        if self.name_input_rect:
            name_label_surface = self.label_font.render(self.name_label_text, True, self.UI_CONFIG['colors']['text'])
            name_label_y = self.name_input_rect.y + (self.name_input_rect.height - name_label_surface.get_height()) // 2
            self.screen.blit(name_label_surface, (self.name_label_pos[0], name_label_y))
            
    def draw_buttons(self):
        """
        fonction : dessine les boutons
        """
        for i, button in enumerate(self.color_buttons):
            button.draw(self.screen)
            if self.COLORS[i] == self.current_color:
                pygame.draw.rect(self.screen, self.UI_CONFIG['colors']['text'], button.rect, 3)
                
        buttons = [
            self.prev_quadrant_button,
            self.next_quadrant_button,
            self.load_button,
            self.save_button,
            self.clear_button,
            self.back_button
        ]
        
        for button in buttons:
            if button:
                button.draw(self.screen)
                
    def draw_grid(self):
        """
        fonction : dessine la grille
        """
        for row_idx in range(self.GRID_SIZE):
            for col_idx in range(self.GRID_SIZE):
                cell_rect = self.grid_rects[row_idx][col_idx]
                cell_color_name = self.grid[row_idx][col_idx]
                
                fill_color = self.get_pygame_color(cell_color_name)
                pygame.draw.rect(self.screen, fill_color, cell_rect)
                pygame.draw.rect(self.screen, self.UI_CONFIG['colors']['grid_border'], cell_rect, 2)
                
    def draw_quadrant_navigation(self):
        """
        fonction : dessine la navigation des quadrants
        """
        if self.quadrant_names and self.label_font:
            current_name = self.quadrant_names[self.selected_quadrant_index] if self.quadrant_names else ""
            quadrant_surface = self.label_font.render(current_name, True, self.UI_CONFIG['colors']['text'])
            
            available_width = self.next_quadrant_button.rect.x - self.quadrant_num_display_pos[0]
            if quadrant_surface.get_width() > available_width:
                quadrant_surface = self.label_font.render(current_name[:8] + "...", True, self.UI_CONFIG['colors']['text'])
            
            self.screen.blit(quadrant_surface, self.quadrant_num_display_pos)
            
    def draw_name_input(self):
        """
        fonction : dessine le champ de saisie du nom
        """
        if not self.name_input_rect:
            return
            
        border_color = self.UI_CONFIG['colors']['text'] if self.name_input_active else self.UI_CONFIG['colors']['input_inactive']
        pygame.draw.rect(self.screen, (0, 0, 0, 100), self.name_input_rect)
        pygame.draw.rect(self.screen, border_color, self.name_input_rect, 2)
        
        if not self.save_name or not self.input_text_font:
            return
            
        name_surface = self.input_text_font.render(self.save_name, True, self.UI_CONFIG['colors']['text'])
        text_x = self.name_input_rect.x + 5
        text_y = self.name_input_rect.y + (self.name_input_rect.height - name_surface.get_height()) // 2
        
        available_width = self.name_input_rect.width - 10
        if name_surface.get_width() > available_width:
            area = pygame.Rect(0, 0, available_width, name_surface.get_height())
            self.screen.blit(name_surface, (text_x, text_y), area=area)
        else:
            self.screen.blit(name_surface, (text_x, text_y))
            
    def draw_instruction(self):
        """
        fonction : dessine le texte d'instruction
        """
        if self.instruction_text_surface:
            self.screen.blit(self.instruction_text_surface, self.instruction_text_pos)
            
    def draw_feedback(self):
        """
        fonction : dessine le message de feedback
        """
        if self.feedback_message_surface and self.feedback_message_timer > 0 and self.feedback_font:
            self.screen.blit(self.feedback_message_surface, self.feedback_message_pos)

    def show_feedback_message(self, text: str, is_error: bool = True, duration_frames: Optional[int] = None):
        """
        fonction : affiche un message de feedback temporaire
        params :
            text - contenu du message
            is_error - True si erreur, False si succès
            duration_frames - durée en frames du message
        """
        self.feedback_message = text
        self.feedback_message_color = (255, 100, 100) if is_error else (100, 255, 100)
        
        if not self.feedback_font:
             Logger.warning("QuadrantEditorScreen", "Feedback font not initialized, using fallback.")
             self.feedback_font = pygame.font.Font(None, 28)

        self.feedback_message_surface = self.feedback_font.render(self.feedback_message, True, self.feedback_message_color)
        
        msg_x: int = (self.width - self.feedback_message_surface.get_width()) // 2
        msg_y: int = self.feedback_message_base_y 
        self.feedback_message_pos = (msg_x, msg_y)
        
        self.feedback_message_timer = duration_frames if duration_frames is not None else self.FEEDBACK_MESSAGE_DURATION
        Logger.info("FeedbackMessage", f"Displaying: '{text}' (Error: {is_error})")

    def get_pygame_color(self, color_name: Optional[str]) -> Tuple[int, int, int]:
        """
        fonction : obtient la couleur RGB correspondant au nom de couleur
        params :
            color_name - nom de la couleur
        retour : tuple RGB de la couleur
        """
        color_map: Dict[str, Tuple[int, int, int]] = {
            'red': (220, 20, 20),
            'green': (20, 220, 20),
            'blue': (20, 20, 220),
            'yellow': (220, 220, 20)
        }
        return color_map.get(color_name, (128, 128, 128)) if color_name else (128, 128, 128)
