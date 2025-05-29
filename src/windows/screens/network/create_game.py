import pygame
import os
from src.windows.screens.base_screen import BaseScreen
from src.windows.components.button import Button
from src.windows.components.dropdown import Dropdown
from src.windows.components.text_input import TextInput
from src.windows.components.image_button import ImageButton
from src.utils.logger import Logger
from src.utils.theme_manager import ThemeManager
from src.windows.selector.game_launcher import GameLauncher
from src.windows.selector.config_loader import ConfigLoader
from src.windows.selector.quadrant_handler import QuadrantHandler
from src.network.client.client import NetworkClient

class CreateGameScreen(BaseScreen):
    GAMES = ["katerenga", "isolation", "congress"]
    
    def __init__(self):
        super().__init__(title="Ludoria - Create Network Game")
        self.game_launcher = GameLauncher()
        self.network_client = NetworkClient()
        self.config_loader = ConfigLoader()
        self.quadrant_handler = QuadrantHandler()
        self.theme_manager = ThemeManager()
        
        self.game_name_input = None
        self.player_name_input = None
        self.game_dropdown = None
        self.create_button = None
        self.quadrant_config_button = None
        
        self.quadrants_config = None
        self.quadrant_names = None
        self.selected_quadrants = [None] * 4
        
        self.background_image = None
        try:
            current_theme = self.theme_manager.current_theme
            bg_path = os.path.join("assets", current_theme, "background.png")
            self.background_image = pygame.image.load(bg_path)
            self.background_image = pygame.transform.scale(self.background_image, (self.width, self.height))
            
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            self.background_image.blit(overlay, (0, 0))
            
            Logger.info("CreateGameScreen", f"Background image loaded: {bg_path}")
        except Exception as e:
            Logger.error("CreateGameScreen", f"Failed to load background image: {e}")
        
        # charge les quadrants par défaut
        config_result = self.config_loader.load_quadrants()
        if config_result:
            self.quadrants_config, self.quadrant_names, _ = config_result
            # initialise avec les quadrants par défaut
            for i in range(4):
                if i < len(self.quadrant_names):
                    self.selected_quadrants[i] = self.quadrants_config.get(self.quadrant_names[i % len(self.quadrant_names)])
        else:
            Logger.error("CreateGameScreen", "Failed to load quadrant configurations.")
    
    def setup_ui(self):
        element_spacing = 20
        label_spacing = 10
        current_y = self.navbar_height + 200 
        
        button_font = self.font_manager.get_font(30)
        self.font = self.font_manager.get_font(20)
        
        self.labels = []
        
        button_img_path = "assets/Basic_GUI_Bundle/ButtonsText/ButtonText_Large_GreyOutline_Square.png"
        
        button_width = 280
        button_height = 50
        button_spacing = 30
        element_width = 240
        quadrant_button_width = 420
        
        center_x = self.width // 2
        left_x = center_x - (element_width // 2)
        
        self.labels.append(("GAME NAME:", (left_x, current_y)))
        current_y += self.font.get_height() + label_spacing
        
        self.game_name_input = TextInput(
            left_x, current_y, element_width, 40, "Game Name"
        )
        current_y += 40 + element_spacing * 2
        
        self.labels.append(("YOUR NAME:", (left_x, current_y)))
        current_y += self.font.get_height() + label_spacing
        
        self.player_name_input = TextInput(
            left_x, current_y, element_width, 40, "Your Name"
        )
        current_y += 40 + element_spacing * 2

        self.labels.append(("GAME TYPE:", (left_x, current_y)))
        current_y += self.font.get_height() + label_spacing
        
        self.game_dropdown = Dropdown(
            left_x, current_y, element_width, 40, self.GAMES, 0
        )
        current_y += 40 + element_spacing * 3
        
        self.quadrant_config_button = ImageButton(
            center_x - (quadrant_button_width // 2),
            current_y - 35,
            quadrant_button_width,
            button_height,
            "CONFIGURE QUADRANTS",
            self._open_quadrant_config,
            bg_image_path=button_img_path,
            font=button_font,
            text_color=(255, 255, 255)
        )
        current_y += button_height + button_spacing * 2
        
        self.create_button = ImageButton(
            center_x - (button_width // 2),
            current_y - 80,
            button_width,
            button_height,
            "CREATE GAME",
            self.create_game,
            bg_image_path=button_img_path,
            font=button_font,
            text_color=(255, 255, 255)
        )
        
        self.buttons_left_x = center_x - (quadrant_button_width // 2)
        self.buttons_right_x = self.buttons_left_x + quadrant_button_width
    
    def _open_quadrant_config(self):
        """procédure : ouvre l'écran de configuration des quadrants"""
        from src.windows.screens.game_config.quadrant_config import QuadrantConfigScreen
        self.next_screen = lambda: QuadrantConfigScreen(self)
        self.running = False
        Logger.info("CreateGameScreen", "Opening quadrant configuration screen")
    
    def create_game(self):
        game_name = self.game_name_input.get()
        player_name = self.player_name_input.get()
        selected_index = self.game_dropdown.selected_index
        selected_game = self.GAMES[selected_index]
        
        if not game_name:
            Logger.warning("CreateGameScreen", "Game name cannot be empty")
            return
        
        if not player_name:
            Logger.warning("CreateGameScreen", "Player name cannot be empty")
            return
        
        Logger.info("CreateGameScreen", f"Creating network game '{game_name}' of type '{selected_game}' for player '{player_name}'")
        
        valid_params = self.game_launcher.validate_game_params(
            game_name, "Network", ["Solo", "Bot", "Network"]
        )
        
        if valid_params:
            Logger.info("CreateGameScreen", f"Directly creating and launching game of type '{selected_game}'")
            self.running = False
            
            # retour à l'écran de sélection de mode
            from src.windows.screens.game_selection.mode_selection import ModeSelectionScreen
            self.next_screen = ModeSelectionScreen
            
            # lancer le jeu directement avec les quadrants configurés
            # passer le nom du joueur à start_game au lieu de se connecter séparément
            game_success = self.game_launcher.start_game(
                game_name, selected_game, "Network", self.selected_quadrants, player_name=player_name
            )
            
            if not game_success:
                Logger.warning("CreateGameScreen", "Game exited with errors")
    
    def handle_screen_events(self, event):
        mouse_pos = pygame.mouse.get_pos()
        
        self.game_name_input.handle_event(event, mouse_pos)
        self.player_name_input.handle_event(event, mouse_pos)
        self.game_dropdown.handle_event(event, mouse_pos)
        self.quadrant_config_button.handle_event(event)
        self.create_button.handle_event(event)
    
    def update_screen(self, mouse_pos):
        self.game_name_input.update(16)
        self.player_name_input.update(16)
        self.quadrant_config_button.check_hover(mouse_pos)
        self.create_button.check_hover(mouse_pos)
    
    def draw_screen(self):
        """
        procédure : dessine l'écran.
        """
        if self.background_image:
            self.screen.blit(self.background_image, (0, 0))
        
        title_text = "LUDORIA"
        subtitle_text = "NETWORK MODE"
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
            p2_y = p1_y;
            
            self.screen.blit(player1_img, (p1_x, p1_y))
            self.screen.blit(player2_img, (p2_x, p2_y))
            
        except Exception as e:
            Logger.error("CreateGameScreen", f"Error loading player images: {e}")
        
        for text, pos in self.labels:
            shadow_surface = self.font.render(text, True, (30, 30, 30))
            self.screen.blit(shadow_surface, (pos[0] + 1, pos[1] + 1))
            
            text_surface = self.font.render(text, True, (255, 255, 255))
            self.screen.blit(text_surface, pos)
        
        self.game_name_input.draw(self.screen)
        self.player_name_input.draw(self.screen)
        self.game_dropdown.draw(self.screen)
        self.quadrant_config_button.draw(self.screen)
        self.create_button.draw(self.screen)