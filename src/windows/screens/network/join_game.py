import pygame
from src.windows.screens.base_screen import BaseScreen
from src.windows.components.button import Button
from src.windows.components.dropdown import Dropdown
from src.windows.components.text_input import TextInput
from src.utils.logger import Logger
from src.windows.selector.game_launcher import GameLauncher

class JoinGameScreen(BaseScreen):
    GAMES = ["katerenga", "isolation", "congress"]
    
    def __init__(self):
        super().__init__(title="Ludoria - Join Network Game")
        self.game_launcher = GameLauncher()
        
        self.game_name_input = None
        self.game_dropdown = None
        self.join_button = None
    
    def setup_ui(self):
        panel_width = 400
        padding = 20
        element_height = 30
        element_spacing = 20
        label_spacing = 5
        current_y = self.navbar_height + 40
        element_width = panel_width - 2 * padding
        
        title_font = pygame.font.SysFont('Arial', 24, bold=True)
        self.font = pygame.font.SysFont('Arial', 16)
        
        self.labels = []
        
        title_text = "Join Network Game"
        title_surface = title_font.render(title_text, True, (50, 50, 50))
        title_x = (self.width - title_surface.get_width()) // 2
        self.labels.append((title_text, (title_x, current_y)))
        current_y += title_font.get_height() + 30
        
        panel_x = (self.width - panel_width) // 2
        
        self.labels.append(("Game Name:", (panel_x, current_y)))
        current_y += self.font.get_height() + label_spacing
        
        self.game_name_input = TextInput(
            panel_x, current_y, element_width, element_height
        )
        current_y += element_height + element_spacing
        
        self.labels.append(("Game Type:", (panel_x, current_y)))
        current_y += self.font.get_height() + label_spacing
        
        self.game_dropdown = Dropdown(
            panel_x, current_y, element_width, element_height, self.GAMES, 0
        )
        current_y += element_height + element_spacing * 2
        
        self.join_button = Button(
            panel_x, current_y, element_width, 40, 
            "Join Game", self.join_game
        )
    
    def join_game(self):
        game_name = self.game_name_input.get()
        selected_game = self.GAMES[self.game_dropdown.selected_index]
        
        if not game_name:
            Logger.warning("JoinGameScreen", "Game name cannot be empty")
            return
        
        Logger.info("JoinGameScreen", f"Joining network game '{game_name}' of type '{selected_game}'")
        
        valid_params = self.game_launcher.validate_game_params(
            game_name, "Network", ["Solo", "Bot", "Network"]
        )
        
        if valid_params:
            Logger.info("JoinGameScreen", "Proceeding to game configuration")
            self.running = False
            
            from src.windows.screens.game_config.game_config import GameConfigScreen
            self.next_screen = lambda: GameConfigScreen("Network")
    
    def handle_screen_events(self, event):
        mouse_pos = pygame.mouse.get_pos()
        
        self.game_name_input.handle_event(event, mouse_pos)
        self.game_dropdown.handle_event(event, mouse_pos)
        self.join_button.handle_event(event)
    
    def update_screen(self, mouse_pos):
        self.game_name_input.update(16)
        self.join_button.check_hover(mouse_pos)
    
    def draw_screen(self):
        for text, pos in self.labels:
            text_surface = self.font.render(text, True, (0, 0, 0))
            self.screen.blit(text_surface, pos)
        
        self.game_name_input.draw(self.screen)
        self.game_dropdown.draw(self.screen)
        self.join_button.draw(self.screen) 