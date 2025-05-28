import pygame
from src.windows.screens.base_screen import BaseScreen
from src.windows.components.button import Button
from src.windows.components.dropdown import Dropdown
from src.windows.components.text_input import TextInput
from src.windows.components.image_button import ImageButton
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
        if mode.upper() == "SOLO":
            mode = "Solo"
        elif mode.upper() == "BOT":
            mode = "Bot"
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
        padding = 20
        element_spacing = 20
        label_spacing = 10
        current_y = self.navbar_height + 200
        
        button_font = self.font_manager.get_font(30)
        title_font = self.font_manager.get_font(24)
        self.font = self.font_manager.get_font(20)
        
        self.labels = []
        
        button_img_path = "assets/Basic_GUI_Bundle/ButtonsText/ButtonText_Large_GreyOutline_Square.png"
        
        initial_game_name = ""
        initial_game_index = 0
        
        if self.existing_game_name:
            initial_game_name = self.existing_game_name
        
        if self.existing_game_type and self.existing_game_type in self.GAMES:
            initial_game_index = self.GAMES.index(self.existing_game_type)
        
        button_width = 280
        button_height = 50
        button_spacing = 30
        element_width = 240
        quadrant_button_width = 420
        
        center_x = self.width // 2
        left_x = center_x - (element_width // 2)
        
        # Nom de la partie
        self.labels.append(("GAME NAME:", (left_x, current_y)))
        current_y += self.font.get_height() + label_spacing
        
        self.save_name_input = TextInput(
            left_x, current_y, element_width, 40, "Game Name", 
            initial_text=initial_game_name,
            disabled=bool(self.existing_game_name)
        )
        current_y += 40 + element_spacing * 2
        
        # Type de jeu
        self.labels.append(("GAME TYPE:", (left_x, current_y)))
        current_y += self.font.get_height() + label_spacing
        
        self.game_dropdown = Dropdown(
            left_x, current_y, element_width, 40, 
            self.GAMES, initial_game_index,
            disabled=bool(self.existing_game_type)
        )
        current_y += 40 + element_spacing * 3

        # si on rejoint une partie réseau, on ne peut pas modifier les quadrants
        quadrant_button_text = "CONFIGURE QUADRANTS"
        if self.mode == "Network" and self.existing_quadrants:
            quadrant_button_text = "QUADRANTS FROM SERVER"
            
        self.quadrant_config_button = ImageButton(
            center_x - (quadrant_button_width // 2),
            current_y,
            quadrant_button_width,
            button_height,
            quadrant_button_text,
            self._open_quadrant_config,
            bg_image_path=button_img_path,
            font=button_font,
            text_color=(255, 255, 255)
        )
        current_y += button_height + button_spacing * 2
        
        start_button_text = "JOIN GAME" if self.mode == "Network" and self.existing_game_name else "START GAME"
        self.start_button = ImageButton(
            center_x - (button_width // 2),
            current_y,
            button_width,
            button_height,
            start_button_text,
            self.launch_game,
            bg_image_path=button_img_path,
            font=button_font,
            text_color=(255, 255, 255)
        )
        
        self.buttons_left_x = center_x - (quadrant_button_width // 2)
        self.buttons_right_x = self.buttons_left_x + quadrant_button_width
        
        self._update_selected_quadrants()
    
    def _update_selected_quadrants(self):
        """
        procédure : met à jour les quadrants sélectionnés selon la configuration.
        """
        if self.existing_quadrants:
            return
        
        if self.quadrants_config and self.quadrant_names:
            for i in range(4):
                if i < len(self.quadrant_names) and not self.selected_quadrants[i]:
                    quadrant_name = self.quadrant_names[i % len(self.quadrant_names)]
                    self.selected_quadrants[i] = self.quadrants_config.get(quadrant_name)
    
    def _open_quadrant_config(self):
        """
        Ouvre l'écran de configuration des quadrants.
        """
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
        
        
        title_text = "LUDORIA"
        subtitle_text = f"{self.mode.upper()} MODE"
        title_font = self.font_manager.get_font(120)
        subtitle_font = self.font_manager.get_font(36)
        
        title_surface = title_font.render(title_text, True, (255, 255, 255))
        subtitle_surface = subtitle_font.render(subtitle_text, True, (255, 255, 255))
        
        title_x = (self.width - title_surface.get_width()) // 2
        subtitle_x = (self.width - subtitle_surface.get_width()) // 2
        
        self.screen.blit(title_surface, (title_x, 40))
        self.screen.blit(subtitle_surface, (subtitle_x, 150))
        
        
        try:
            theme = self.theme_manager.current_theme
            player1_path = f"assets/{theme}/joueur1.png"
            player2_path = f"assets/{theme}/joueur2.png"
            
            
            player1_img = pygame.image.load(player1_path).convert_alpha()
            player2_img = pygame.image.load(player2_path).convert_alpha()
            
            
            character_height = 320  
            
            p1_aspect = player1_img.get_width() / player1_img.get_height()
            p2_aspect = player2_img.get_width() / player2_img.get_height()
            
            p1_width = int(character_height * p1_aspect)
            p2_width = int(character_height * p2_aspect)
            
            player1_img = pygame.transform.smoothscale(player1_img, (p1_width, character_height))
            player2_img = pygame.transform.smoothscale(player2_img, (p2_width, character_height))
            
            
            p1_x = self.buttons_left_x - p1_width - 40 
            p2_x = self.buttons_right_x + 40
            p1_y = self.height // 2 - character_height // 2 - 20  
            p2_y = p1_y
            
            self.screen.blit(player1_img, (p1_x, p1_y))
            self.screen.blit(player2_img, (p2_x, p2_y))
            
        except Exception as e:
            Logger.error("GameConfigScreen", f"Error loading player images: {e}")
        
        
        for text, pos in self.labels:
           
            shadow_surface = self.font.render(text, True, (30, 30, 30))
            self.screen.blit(shadow_surface, (pos[0] + 1, pos[1] + 1))
            
           
            text_surface = self.font.render(text, True, (255, 255, 255))
            self.screen.blit(text_surface, pos)
        
        
        self.save_name_input.draw(self.screen)
        self.game_dropdown.draw(self.screen)
        self.quadrant_config_button.draw(self.screen)
        self.start_button.draw(self.screen)