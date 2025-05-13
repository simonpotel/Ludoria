import pygame
from src.windows.screens.base_screen import BaseScreen
from src.windows.components.button import Button
from src.windows.components.dropdown import Dropdown
from src.windows.components.text_input import TextInput
from src.utils.logger import Logger
from src.windows.selector.quadrant_handler import QuadrantHandler
from src.windows.selector.config_loader import ConfigLoader
from src.windows.selector.game_launcher import GameLauncher
from functools import partial

class GameConfigScreen(BaseScreen):
    GAMES = ["katerenga", "isolation", "congress"]
    
    def __init__(self, mode):
        super().__init__(title=f"Ludoria - {mode} Game Configuration")
        self.mode = mode
        self.quadrant_handler = QuadrantHandler()
        self.config_loader = ConfigLoader()
        self.game_launcher = GameLauncher()
        
        self.save_name_input = None
        self.game_dropdown = None
        self.quadrant_selectors = []
        self.quadrant_rotation_buttons = []
        self.start_button = None
        
        self.quadrants_config = None
        self.quadrant_names = None
        self.selected_quadrants = [None] * 4
        
        config_result = self.config_loader.load_quadrants()
        if config_result:
            self.quadrants_config, self.quadrant_names, _ = config_result
        else:
            Logger.error("GameConfigScreen", "Failed to load quadrant configurations.")
    
    def setup_ui(self):
        panel_width = 300
        padding = 20
        element_height = 30
        element_spacing = 15
        label_spacing = 5
        current_y = self.navbar_height + 30
        element_width = panel_width - 2 * padding
        
        title_font = pygame.font.SysFont('Arial', 24, bold=True)
        self.font = pygame.font.SysFont('Arial', 16)
        
        self.labels = []
        
        self.labels.append(("Game Save Name:", (padding, current_y)))
        current_y += self.font.get_height() + label_spacing
        
        self.save_name_input = TextInput(
            padding, current_y, element_width, element_height
        )
        current_y += element_height + element_spacing
        
        self.labels.append(("Game:", (padding, current_y)))
        current_y += self.font.get_height() + label_spacing
        
        self.game_dropdown = Dropdown(
            padding, current_y, element_width, element_height, self.GAMES, 0
        )
        current_y += element_height + element_spacing
        
        self.labels.append(("Quadrant Configuration:", (padding, current_y)))
        current_y += self.font.get_height() + label_spacing
        
        self.quadrant_selectors = []
        self.quadrant_rotation_buttons = []
        button_width = 30
        selector_width = element_width - 2 * button_width - 10
        
        for i in range(4):
            selector = Dropdown(
                padding, current_y, selector_width, element_height, 
                self.quadrant_names, i % len(self.quadrant_names)
            )
            self.quadrant_selectors.append(selector)
            
            left_button = Button(
                padding + selector_width + 5, current_y, 
                button_width, element_height, "< -", 
                partial(self._rotate_left_handler, i)
            )
            right_button = Button(
                padding + selector_width + 10 + button_width, current_y, 
                button_width, element_height, "->", 
                partial(self._rotate_right_handler, i)
            )
            self.quadrant_rotation_buttons.append((left_button, right_button))
            
            current_y += element_height + 5
        
        current_y += element_spacing
        
        self.start_button = Button(
            padding, current_y, element_width, 40, 
            "Start / Load Game", self.launch_game
        )
        
        # Calculer la taille optimale pour la prévisualisation
        available_width = self.width - panel_width - (padding * 2)
        available_height = self.height - self.navbar_height - 60
        
        # Déterminer la taille carrée qui est optimale pour la prévisualisation du plateau
        preview_size = min(available_width, available_height)
        
        # Centrer le rectangle de prévisualisation dans l'espace disponible
        preview_x = panel_width + ((available_width - preview_size) // 2) + padding
        preview_y = self.navbar_height + ((available_height - preview_size) // 2) + 30
        
        self.preview_rect = pygame.Rect(
            preview_x, 
            preview_y, 
            preview_size, 
            preview_size
        )
        
        # Log pour le debug
        Logger.info("GameConfigScreen", f"Preview rectangle: {self.preview_rect}")
        
        self._update_selected_quadrants()
    
    def _update_selected_quadrants(self):
        self.selected_quadrants = self.quadrant_handler.update_selected_quadrants(
            self.quadrant_selectors, 
            self.selected_quadrants, 
            self.quadrants_config, 
            self.quadrant_names
        )
    
    def _rotate_left_handler(self, index):
        self.selected_quadrants = self.quadrant_handler.rotate_left(self.selected_quadrants, index)
    
    def _rotate_right_handler(self, index):
        self.selected_quadrants = self.quadrant_handler.rotate_right(self.selected_quadrants, index)
    
    def launch_game(self):
        game_save = self.save_name_input.get()
        selected_game = self.GAMES[self.game_dropdown.selected_index]
        
        if not game_save:
            Logger.warning("GameConfigScreen", "Game save name cannot be empty")
            return
        
        valid_params = self.game_launcher.validate_game_params(
            game_save, self.mode, ["Solo", "Bot", "Network"]
        )
        
        if valid_params:
            Logger.info("GameConfigScreen", f"Launching {selected_game} in {self.mode} mode with save '{game_save}'")
            
            # configure l'écran suivant avant de lancer le jeu
            from src.windows.screens.game_selection.mode_selection import ModeSelectionScreen
            self.next_screen = ModeSelectionScreen
            
            # arrête l'écran courant pour retourner au launcher
            self.running = False
            
            # démarre le jeu - bloque jusqu'à la fin du jeu
            game_success = self.game_launcher.start_game(game_save, selected_game, self.mode, self.selected_quadrants)
            
            if game_success:
                Logger.info("GameConfigScreen", f"Game completed successfully, returning to mode selection")
            else:
                Logger.warning("GameConfigScreen", f"Game exited with errors, returning to mode selection")
    
    def handle_screen_events(self, event):
        self.save_name_input.handle_event(event, pygame.mouse.get_pos())
        self.game_dropdown.handle_event(event, pygame.mouse.get_pos())
        
        for selector in self.quadrant_selectors:
            if selector.handle_event(event, pygame.mouse.get_pos()):
                if not selector.is_open:
                    self._update_selected_quadrants()
        
        for left_btn, right_btn in self.quadrant_rotation_buttons:
            left_btn.handle_event(event)
            right_btn.handle_event(event)
        
        self.start_button.handle_event(event)
    
    def update_screen(self, mouse_pos):
        self.save_name_input.update(16)
        
        for left_btn, right_btn in self.quadrant_rotation_buttons:
            left_btn.check_hover(mouse_pos)
            right_btn.check_hover(mouse_pos)
        
        self.start_button.check_hover(mouse_pos)
    
    def draw_screen(self):
        for text, pos in self.labels:
            text_surface = self.font.render(text, True, (0, 0, 0))
            self.screen.blit(text_surface, pos)
        
        self.save_name_input.draw(self.screen)
        self.game_dropdown.draw(self.screen)
        
        for selector in self.quadrant_selectors:
            selector.draw(self.screen)
        
        for left_btn, right_btn in self.quadrant_rotation_buttons:
            left_btn.draw(self.screen)
            right_btn.draw(self.screen)
        
        self.start_button.draw(self.screen)
        
        preview_label = self.font.render("Preview:", True, (0, 0, 0))
        self.screen.blit(preview_label, (self.preview_rect.left, self.preview_rect.top - 25))
        
        pygame.draw.rect(self.screen, (200, 200, 200), self.preview_rect, 2)
        
        if all(self.selected_quadrants):
            self.quadrant_handler.draw_quadrants(
                self.screen, 
                self.selected_quadrants, 
                self.preview_rect
            )