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
    
    def __init__(self, mode, game_name=None, game_type=None, quadrants=None):
        """
        constructeur : initialise l'écran de configuration du jeu.
        
        params:
            mode - mode de jeu (solo, multijoueur, etc.).
            game_name - nom de la partie (optionnel, pour rejoindre une partie réseau).
            game_type - type de jeu (optionnel, pour rejoindre une partie réseau).
            quadrants - quadrants prédéfinis (optionnel, pour rejoindre une partie réseau).
        """
        super().__init__(title=f"Ludoria - {mode} Game Configuration")
        self.mode = mode
        self.existing_game_name = game_name
        self.existing_game_type = game_type
        self.existing_quadrants = quadrants
        
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
        
        # si on rejoint une partie réseau, on utilise les quadrants existants
        if self.mode == "Network" and self.existing_quadrants:
            Logger.info("GameConfigScreen", f"Using existing quadrants for network game")
            self.selected_quadrants = self.existing_quadrants
        else:
            # chargement des quadrants par défaut depuis la configuration
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
        
        # si on rejoint une partie réseau, on ne peut pas modifier le nom de la partie
        initial_game_name = ""
        initial_game_index = 0
        
        if self.existing_game_name:
            initial_game_name = self.existing_game_name
        
        if self.existing_game_type and self.existing_game_type in self.GAMES:
            initial_game_index = self.GAMES.index(self.existing_game_type)
        
        self.save_name_input = TextInput(
            padding, current_y + 20, element_width, 80, "Game Name", 
            initial_text=initial_game_name,
            disabled=bool(self.existing_game_name)
        )
        current_y += element_height + element_spacing
        
        self.labels.append(("Game:", (padding, current_y + 100)))
        current_y += self.font.get_height() + label_spacing
        
        self.game_dropdown = Dropdown(
            padding, current_y + 100, element_width, element_height, 
            self.GAMES, initial_game_index,
            disabled=bool(self.existing_game_type)
        )
        current_y += element_height + element_spacing
        
        self.labels.append(("Quadrant Configuration:", (padding, current_y + 100)))
        current_y += self.font.get_height() + label_spacing
        
        # si on rejoint une partie réseau, on ne peut pas modifier les quadrants
        quadrant_button_text = "Change Quadrant"
        if self.mode == "Network" and self.existing_quadrants:
            quadrant_button_text = "Quadrants from Server"
            
        self.quadrant_config_button = Button(
            padding, current_y + 100, element_width, 100, 
            quadrant_button_text, self._open_quadrant_config,
            disabled=bool(self.existing_quadrants)
        )
        current_y += element_height + element_spacing
        
        current_y += element_spacing
        
        start_button_text = "Join Game" if self.mode == "Network" and self.existing_game_name else "Start / Load Game"
        self.start_button = Button(
            padding, current_y + 160, element_width, 100, 
            start_button_text, self.launch_game
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
        # si on a des quadrants existants depuis le réseau, on ne les met pas à jour
        if self.existing_quadrants:
            return
            
        if self.quadrants_config and self.quadrant_names:
            for i in range(4):
                if i < len(self.quadrant_names) and not self.selected_quadrants[i]:
                    quadrant_name = self.quadrant_names[i % len(self.quadrant_names)]
                    self.selected_quadrants[i] = self.quadrants_config.get(quadrant_name)
    
    def _open_quadrant_config(self):
        """
        procédure : ouvre l'écran de configuration des quadrants.
        """
        # si on rejoint une partie réseau, on ne peut pas modifier les quadrants
        if self.mode == "Network" and self.existing_quadrants:
            return
            
        from src.windows.screens.game_config.quadrant_config import QuadrantConfigScreen
        # passage de l'instance actuelle comme écran parent
        self.next_screen = lambda: QuadrantConfigScreen(self)
        self.running = False
        Logger.info("GameConfigScreen", "Opening quadrant configuration screen")
    
    def launch_game(self):
        """
        procédure : lance le jeu avec les paramètres configurés.
        """
        # si on rejoint une partie réseau, on utilise les informations de la partie existante
        game_save = self.existing_game_name or self.save_name_input.get()
        selected_game = self.existing_game_type or self.GAMES[self.game_dropdown.selected_index]
        
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
            game_success = self.game_launcher.start_game(
                game_save, selected_game, self.mode, 
                self.existing_quadrants or self.selected_quadrants
            )
            
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
        procédure : met à jour l'écran.
        
        params:
            mouse_pos - position de la souris.
        """
        if not self.existing_game_name:
            self.save_name_input.update(16)
        
        self.quadrant_config_button.check_hover(mouse_pos)
        self.start_button.check_hover(mouse_pos)
    
    def draw_screen(self):
        """
        procédure : dessine l'écran.
        """
        if self.background_image:
            self.screen.blit(self.background_image, (0, 0))
        
        for text, pos in self.labels:
            text_surface = self.font.render(text, True, (255, 255, 255))
            self.screen.blit(text_surface, pos)
        
        preview_border_width = 3
        pygame.draw.rect(
            self.screen, 
            (153, 98, 61),  # couleur du cadre (marron)
            self.preview_rect, 
            preview_border_width
        )
        
        quadrant_size = self.preview_rect.width // 2
        
        # dessin des quadrants
        for i in range(4):
            row = i // 2
            col = i % 2
            
            quadrant_rect = pygame.Rect(
                self.preview_rect.x + (col * quadrant_size),
                self.preview_rect.y + (row * quadrant_size),
                quadrant_size,
                quadrant_size
            )
            
            # couleur de fond par défaut pour les quadrants
            fill_color = (200, 200, 200)
            
            # si un quadrant est sélectionné, on utilise sa couleur
            if i < len(self.selected_quadrants) and self.selected_quadrants[i]:
                quadrant_data = self.selected_quadrants[i]
                if quadrant_data and "color" in quadrant_data:
                    color_hex = quadrant_data["color"]
                    fill_color = tuple(int(color_hex[j:j+2], 16) for j in (1, 3, 5))
            
            pygame.draw.rect(self.screen, fill_color, quadrant_rect)
            pygame.draw.rect(self.screen, (0, 0, 0), quadrant_rect, 1)
            
            # afficher le nom du quadrant s'il est disponible
            if i < len(self.selected_quadrants) and self.selected_quadrants[i]:
                quadrant_data = self.selected_quadrants[i]
                if quadrant_data and "name" in quadrant_data:
                    name = quadrant_data["name"]
                    name_font = pygame.font.SysFont('Arial', 12, bold=True)
                    name_surface = name_font.render(name, True, (0, 0, 0))
                    
                    name_rect = name_surface.get_rect(center=quadrant_rect.center)
                    self.screen.blit(name_surface, name_rect)
        
        self.save_name_input.draw(self.screen)
        self.game_dropdown.draw(self.screen)
        self.quadrant_config_button.draw(self.screen)
        self.start_button.draw(self.screen)