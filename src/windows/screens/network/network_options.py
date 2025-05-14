import pygame
from src.windows.screens.base_screen import BaseScreen
from src.windows.components.button import Button
from src.utils.logger import Logger

class NetworkOptionsScreen(BaseScreen):
    def __init__(self):
        super().__init__(title="Ludoria - Network Options")
        self.option_buttons = []
        self.options = ["Create Game", "Join Game"]
    
    def setup_ui(self):
        button_width = 200
        button_height = 60
        button_spacing = 30
        
        total_height = (button_height * len(self.options)) + (button_spacing * (len(self.options) - 1))
        start_y = (self.content_rect.height - total_height) // 2 + self.navbar_height
        
        for i, option in enumerate(self.options):
            y_pos = start_y + (button_height + button_spacing) * i
            
            button = Button(
                (self.width - button_width) // 2,
                y_pos,
                button_width,
                button_height,
                option,
                lambda o=option: self.select_option(o)
            )
            self.option_buttons.append(button)
    
    def select_option(self, option):
        Logger.info("NetworkOptionsScreen", f"Selected option: {option}")
        
        if option == "Create Game":
            from src.windows.screens.network.create_game import CreateGameScreen
            self.next_screen = CreateGameScreen
        elif option == "Join Game":
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
        title_font = pygame.font.SysFont('Arial', 32, bold=True)
        title_text = "Network Game Options"
        title_surface = title_font.render(title_text, True, (50, 50, 50))
        title_x = (self.width - title_surface.get_width()) // 2
        title_y = self.navbar_height + 40
        self.screen.blit(title_surface, (title_x, title_y))
        
        for button in self.option_buttons:
            button.draw(self.screen) 