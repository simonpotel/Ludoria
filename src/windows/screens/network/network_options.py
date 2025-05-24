import pygame
import os
from src.windows.screens.base_screen import BaseScreen
from src.windows.components.button import Button
from src.windows.components.image_button import ImageButton
from src.utils.logger import Logger
from src.utils.theme_manager import ThemeManager
from src.network.client.client import NetworkClient

class NetworkOptionsScreen(BaseScreen):
    def __init__(self):
        super().__init__(title="Ludoria - Network Options")
        self.option_buttons = []
        self.options = ["CREATE GAME", "JOIN GAME"]
        self.theme_manager = ThemeManager()
        self.background_image = None
        self.player1_img = None
        self.player2_img = None
        self.network_client = NetworkClient()
        self.server_address = self.network_client.host
        
        try:
            current_theme = self.theme_manager.current_theme
            bg_path = os.path.join("assets", current_theme, "background.png")
            self.background_image = pygame.image.load(bg_path)
            self.background_image = pygame.transform.scale(self.background_image, (self.width, self.height))
            
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            self.background_image.blit(overlay, (0, 0))
            
            Logger.info("NetworkOptionsScreen", f"Background image loaded: {bg_path}")
        except Exception as e:
            Logger.error("NetworkOptionsScreen", f"Failed to load background image: {e}")
    
    def setup_ui(self):
        button_font = self.font_manager.get_font(30)
        
        button_width = 280
        button_height = 50
        button_spacing = 30
        button_img_path = "assets/Basic_GUI_Bundle/ButtonsText/ButtonText_Large_GreyOutline_Square.png"
        
        total_height = (button_height * len(self.options)) + (button_spacing * (len(self.options) - 1))
        
        start_y = (self.height - total_height) // 2 + 70
        
        first_button_y = 0
        last_button_bottom_y = 0
        
        for i, option in enumerate(self.options):
            y_pos = start_y + (button_height + button_spacing) * i
            
            if i == 0:
                first_button_y = y_pos
            if i == len(self.options) - 1:
                last_button_bottom_y = y_pos + button_height
            
            button = ImageButton(
                (self.width - button_width) // 2,
                y_pos,
                button_width,
                button_height,
                option,
                lambda o=option: self.select_option(o),
                bg_image_path=button_img_path,
                font=button_font,
                text_color=(255, 255, 255)
            )
            self.option_buttons.append(button)
        
        self.buttons_center_x = (self.width - button_width) // 2 + button_width // 2
        self.buttons_left_x = (self.width - button_width) // 2
        self.buttons_right_x = self.buttons_left_x + button_width
        
        try:
            theme = self.theme_manager.current_theme
            player1_path = f"assets/{theme}/joueur1.png"
            player2_path = f"assets/{theme}/joueur2.png"
            
            original_p1 = pygame.image.load(player1_path).convert_alpha()
            original_p2 = pygame.image.load(player2_path).convert_alpha()
            
            character_height = int((last_button_bottom_y - first_button_y) * 2)
            
            p1_aspect = original_p1.get_width() / original_p1.get_height()
            p2_aspect = original_p2.get_width() / original_p2.get_height()
            
            p1_width = int(character_height * p1_aspect)
            p2_width = int(character_height * p2_aspect)
            
            self.player1_img = pygame.transform.smoothscale(original_p1, (p1_width, character_height))
            self.player2_img = pygame.transform.smoothscale(original_p2, (p2_width, character_height))
            
            self.p1_y = first_button_y - (character_height - (last_button_bottom_y - first_button_y)) // 2
            self.p2_y = self.p1_y
            
        except Exception as e:
            Logger.error("NetworkOptionsScreen", f"Error loading player images: {e}")
            self.player1_img = None
            self.player2_img = None
    
    def select_option(self, option):
        Logger.info("NetworkOptionsScreen", f"Selected option: {option}")
        
        if option == "CREATE GAME":
            from src.windows.screens.network.create_game import CreateGameScreen
            self.next_screen = CreateGameScreen
        elif option == "JOIN GAME":
            from src.windows.screens.network.join_game import JoinGameScreen
            self.next_screen = JoinGameScreen
        
        self.running = False
    
    def handle_screen_events(self, event):
        for button in self.option_buttons:
            button.handle_event(event)
    
    def update_screen(self, mouse_pos):
        for button in self.option_buttons:
            button.check_hover(mouse_pos)
    
    def draw_screen(self):
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
        
        if self.player1_img and self.player2_img:
            p1_x = self.buttons_left_x - self.player1_img.get_width() - 20
            p2_x = self.buttons_right_x + 20
            
            self.screen.blit(self.player1_img, (p1_x, self.p1_y))
            self.screen.blit(self.player2_img, (p2_x, self.p2_y))
        
        for button in self.option_buttons:
            button.draw(self.screen)
            
        small_font = self.font_manager.get_font(20)
        server_text = f"SERVER: {self.server_address}"
        server_surface = small_font.render(server_text, True, (255, 255, 255))
        server_x = 20
        server_y = self.height - 30
        self.screen.blit(server_surface, (server_x, server_y))