import pygame
import os
from src.windows.screens.base_screen import BaseScreen
from src.windows.components.image_button import ImageButton
from src.utils.logger import Logger
from src.utils.theme_manager import ThemeManager
from src.network.client.client import NetworkClient


class ModeSelectionScreen(BaseScreen):
    def __init__(self):
        super().__init__(title="Ludoria - Mode Selection")
        self.mode_buttons = []
        self.modes = ["SOLO", "BOT", "NETWORK"]
        self.theme_manager = ThemeManager()
        self.background = None
        self.player1_img = None
        self.player2_img = None
        self.version = "v1"
        self.server_address = NetworkClient().host

    def setup_ui(self):
        button_font = self.font_manager.get_font(40)
        
        try:
            theme = self.theme_manager.current_theme
            bg_path = f"assets/{theme}/background.png"
            original_bg = pygame.image.load(bg_path).convert_alpha()
            self.background = pygame.transform.scale(original_bg, (self.width, self.height))
            
            blur_effect = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            blur_effect.fill((0, 0, 0, 180))
            self.background.blit(blur_effect, (0, 0))
        except Exception as e:
            Logger.error("ModeSelectionScreen", f"Error loading background image: {e}")
            self.background = None

        button_width = 280  
        button_height = 60  
        button_spacing = 10  
        button_img_path = "assets/Basic_GUI_Bundle/ButtonsText/ButtonText_Large_GreyOutline_Square.png"

        total_height = (button_height * len(self.modes)) + (button_spacing * (len(self.modes) - 1))
        start_y = (self.height - total_height) // 2 + 30  

        first_button_y = 0
        last_button_bottom_y = 0
        
        for i, mode in enumerate(self.modes):
            y_pos = start_y + (button_height + button_spacing) * i
            
            if i == 0:
                first_button_y = y_pos
            if i == len(self.modes) - 1:
                last_button_bottom_y = y_pos + button_height
                
            button = ImageButton(
                (self.width - button_width) // 2,
                y_pos,
                button_width,
                button_height,
                mode,
                lambda m=mode: self.select_mode(m),
                bg_image_path=button_img_path,
                font=button_font
            )
            self.mode_buttons.append(button)
            
        self.buttons_center_x = (self.width - button_width) // 2 + button_width // 2
        self.buttons_left_x = (self.width - button_width) // 2
        self.buttons_right_x = self.buttons_left_x + button_width

        try:
            theme = self.theme_manager.current_theme
            player1_path = f"assets/{theme}/joueur1.png"
            player2_path = f"assets/{theme}/joueur2.png"
            
            original_p1 = pygame.image.load(player1_path).convert_alpha()
            original_p2 = pygame.image.load(player2_path).convert_alpha()
            
            character_height = last_button_bottom_y - first_button_y
            
            p1_aspect = original_p1.get_width() / original_p1.get_height()
            p2_aspect = original_p2.get_width() / original_p2.get_height()
            
            p1_width = int(character_height * p1_aspect)
            p2_width = int(character_height * p2_aspect)
            
            self.player1_img = pygame.transform.smoothscale(original_p1, (p1_width, character_height))
            self.player2_img = pygame.transform.smoothscale(original_p2, (p2_width, character_height))
            
            self.p1_y = first_button_y
            self.p2_y = first_button_y
            
        except Exception as e:
            Logger.error("ModeSelectionScreen", f"Error loading player images: {e}")
            self.player1_img = None
            self.player2_img = None

    def select_mode(self, mode):
        Logger.info("ModeSelectionScreen", f"Selected mode: {mode}")
        if mode == "SOLO" or mode == "BOT":
            from src.windows.screens.game_config.game_config import GameConfigScreen
            self.next_screen = lambda: GameConfigScreen(mode)
        elif mode == "NETWORK":
            from src.windows.screens.network.network_options import NetworkOptionsScreen
            self.next_screen = NetworkOptionsScreen

        self.running = False
        
    def handle_screen_events(self, event):
        for button in self.mode_buttons:
            button.handle_event(event)

    def update_screen(self, mouse_pos):
        for button in self.mode_buttons:
            button.check_hover(mouse_pos)

    def draw_screen(self):
        if self.background:
            self.screen.blit(self.background, (0, 0))
        
        title_text = "LUDORIA"
        title_font = self.font_manager.get_font(150)
        title_surface = title_font.render(title_text, True, (255, 255, 255))
        title_x = (self.width - title_surface.get_width()) // 2
        title_y = 100  
        self.screen.blit(title_surface, (title_x, title_y))

        if self.player1_img and self.player2_img:
            p1_x = self.buttons_left_x - self.player1_img.get_width() - 5  
            p2_x = self.buttons_right_x + 5  
            
            self.screen.blit(self.player1_img, (p1_x, self.p1_y))
            self.screen.blit(self.player2_img, (p2_x, self.p2_y))

        for button in self.mode_buttons:
            button.draw(self.screen)
        
        small_font = self.font_manager.get_font(20)
        
        server_text = f"SERVER: {self.server_address}"
        server_surface = small_font.render(server_text, True, (255, 255, 255))
        self.screen.blit(server_surface, (20, self.height - 30))
        
        version_surface = small_font.render(self.version, True, (255, 255, 255))
        version_x = self.width - version_surface.get_width() - 20
        version_y = self.height - 30
        self.screen.blit(version_surface, (version_x, version_y))
        
