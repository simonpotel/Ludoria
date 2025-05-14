import pygame
from src.windows.screens.base_screen import BaseScreen
from src.windows.components.button import Button
from src.windows.components.dropdown import Dropdown
from src.windows.components.text_input import TextInput
from src.utils.logger import Logger
from src.windows.selector.quadrant_handler import QuadrantHandler
from src.windows.selector.config_loader import ConfigLoader
from src.windows.selector.game_launcher import GameLauncher
from src.utils.theme_manager import ThemeManager
from functools import partial
import os

class GameConfigScreen(BaseScreen):
    GAMES = ["katerenga", "isolation", "congress"]
    
    def __init__(self, mode):
        """
        constructeur : initialise l'écran de configuration du jeu.
        
        params:
            mode - mode de jeu (solo, multijoueur, etc.).
        """
        super().__init__(title=f"Ludoria - {mode} Game Configuration")
        self.mode = mode
        self.quadrant_handler = QuadrantHandler()
        self.config_loader = ConfigLoader()
        self.game_launcher = GameLauncher()
        self.theme_manager = ThemeManager()
        
        self.save_name_input = None
        self.game_dropdown = None
        self.quadrant_config_button = None
        self.start_button = None
        
        self.quadrants_config = None
        self.quadrant_names = None
        self.selected_quadrants = [None] * 4
        
        self.background_image = None
        try:
            # chargement de l'image de fond en fonction du thème
            current_theme = self.theme_manager.current_theme
            bg_path = os.path.join("assets", current_theme, "background.png")
            self.background_image = pygame.image.load(bg_path)
            self.background_image = pygame.transform.scale(self.background_image, (self.width, self.height))
            
            # ajouter un effet semi-transparent pour améliorer la lisibilité
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))  # overlay noir semi-transparent
            self.background_image.blit(overlay, (0, 0))
            
            Logger.info("GameConfigScreen", f"Background image loaded: {bg_path}")
        except Exception as e:
            Logger.error("GameConfigScreen", f"Failed to load background image: {e}")
        
        config_result = self.config_loader.load_quadrants()
        if config_result:
            self.quadrants_config, self.quadrant_names, _ = config_result
            # initialisation des quadrants par défaut
            for i in range(4):
                if i < len(self.quadrant_names):
                    self.selected_quadrants[i] = self.quadrants_config.get(self.quadrant_names[i % len(self.quadrant_names)])
        else:
            Logger.error("GameConfigScreen", "Failed to load quadrant configurations.")
    
    def setup_ui(self):
        """
        procédure : configure l'interface utilisateur de l'écran.
        """
        panel_width = 300
        padding = 20
        element_height = 30
        element_spacing = 15
        label_spacing = 5
        current_y = self.navbar_height + 30
        element_width = panel_width - 2 * padding
        
        title_font = pygame.font.SysFont('Arial', 24, bold=True)
        self.font = pygame.font.SysFont('Arial', 24)
        
        self.labels = []
        
        
        self.save_name_input = TextInput(
            padding, current_y + 20, element_width, 80, "Game Name"
        )
        current_y += element_height + element_spacing
        
        self.labels.append(("Game:", (padding, current_y + 100)))
        current_y += self.font.get_height() + label_spacing
        
        self.game_dropdown = Dropdown(
            padding, current_y + 100, element_width, element_height, self.GAMES, 0
        )
        current_y += element_height + element_spacing
        
        self.labels.append(("Quadrant Configuration:", (padding, current_y + 100)))
        current_y += self.font.get_height() + label_spacing
        
        self.quadrant_config_button = Button(
            padding, current_y + 100, element_width, 100, 
            "Change Quadrant", self._open_quadrant_config
        )
        current_y += element_height + element_spacing
        
        current_y += element_spacing
        
        self.start_button = Button(
            padding, current_y + 160, element_width, 100, 
            "Start / Load Game", self.launch_game
        )
        
        # préparation de la zone de prévisualisation
        available_width = self.width - panel_width - (padding * 2)
        available_height = self.height - self.navbar_height - 60
        
        preview_size = min(available_width, available_height)
        
        preview_x = panel_width + ((available_width - preview_size) // 2) + padding
        preview_y = self.navbar_height + ((available_height - preview_size) // 2) + 30
        
        self.preview_rect = pygame.Rect(
            preview_x, 
            preview_y, 
            preview_size, 
            preview_size
        )
        
        Logger.info("GameConfigScreen", f"Preview rectangle: {self.preview_rect}")
        
        self._update_selected_quadrants()
    
    def _update_selected_quadrants(self):
        """
        procédure : met à jour les quadrants sélectionnés selon la configuration.
        """
        if self.quadrants_config and self.quadrant_names:
            for i in range(4):
                if i < len(self.quadrant_names) and not self.selected_quadrants[i]:
                    quadrant_name = self.quadrant_names[i % len(self.quadrant_names)]
                    self.selected_quadrants[i] = self.quadrants_config.get(quadrant_name)
    
    def _open_quadrant_config(self):
        """
        procédure : ouvre l'écran de configuration des quadrants.
        """
        from src.windows.screens.game_config.quadrant_config import QuadrantConfigScreen
        # passage de l'instance actuelle comme écran parent
        self.next_screen = lambda: QuadrantConfigScreen(self)
        self.running = False
        Logger.info("GameConfigScreen", "Opening quadrant configuration screen")
    
    def launch_game(self):
        """
        procédure : lance le jeu avec les paramètres configurés.
        """
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
            
            # navigation vers l'écran de sélection du mode
            from src.windows.screens.game_selection.mode_selection import ModeSelectionScreen
            self.next_screen = ModeSelectionScreen
            
            self.running = False
            
            # démarrage du jeu (bloquant)
            game_success = self.game_launcher.start_game(game_save, selected_game, self.mode, self.selected_quadrants)
            
            if game_success:
                Logger.info("GameConfigScreen", f"Game completed successfully, returning to mode selection")
            else:
                Logger.warning("GameConfigScreen", f"Game exited with errors, returning to mode selection")
    
    def handle_screen_events(self, event):
        """
        procédure : gère les événements pour cet écran.
        
        params:
            event - événement pygame à traiter.
        """
        self.save_name_input.handle_event(event, pygame.mouse.get_pos())
        self.game_dropdown.handle_event(event, pygame.mouse.get_pos())
        
        self.quadrant_config_button.handle_event(event)
        
        self.start_button.handle_event(event)
    
    def update_screen(self, mouse_pos):
        """
        procédure : met à jour l'état des éléments de l'écran.
        
        params:
            mouse_pos - position actuelle de la souris.
        """
        self.save_name_input.update(16)
        
        self.quadrant_config_button.check_hover(mouse_pos)
        
        self.start_button.check_hover(mouse_pos)
    
    def draw_screen(self):
        """
        procédure : dessine les éléments de l'écran.
        """
        if self.background_image:
            self.screen.blit(self.background_image, (0, 0))
        else:
            self.screen.fill((240, 240, 240))
        
        # création du panneau semi-transparent
        panel_surface = pygame.Surface((350, self.height), pygame.SRCALPHA)
        panel_surface.fill((240, 240, 240, 200))
        self.screen.blit(panel_surface, (0, 0))
        
        for text, pos in self.labels:
            text_surface = self.font.render(text, True, (0, 0, 0))
            self.screen.blit(text_surface, pos)
        
        self.save_name_input.draw(self.screen)
        self.game_dropdown.draw(self.screen)
        
        self.quadrant_config_button.draw(self.screen)
        
        self.start_button.draw(self.screen)
        
        preview_label = self.font.render("Preview:", True, (0, 0, 0))
        self.screen.blit(preview_label, (self.preview_rect.left, self.preview_rect.top - 25))
        
        # arrière-plan de la prévisualisation
        preview_bg = pygame.Surface((self.preview_rect.width, self.preview_rect.height), pygame.SRCALPHA)
        preview_bg.fill((255, 255, 255, 150))
        self.screen.blit(preview_bg, self.preview_rect)
        
        pygame.draw.rect(self.screen, (100, 100, 100), self.preview_rect, 2)
        
        if all(self.selected_quadrants):
            self.quadrant_handler.draw_quadrants(
                self.screen, 
                self.selected_quadrants, 
                self.preview_rect
            )