import pygame
from src.windows.components.navbar.navbar import NavBar
from src.utils.logger import Logger

class BaseScreen:
    def __init__(self, width=1280, height=720, title="Ludoria"):
        self.width = width
        self.height = height
        self.title = title
        self.running = False
        self.screen = None
        self.clock = pygame.time.Clock()
        self.fps = 30
        
        self.navbar = NavBar(self.width)
        self.navbar_height = 50
        self.content_rect = pygame.Rect(0, self.navbar_height, self.width, self.height - self.navbar_height)
        
        self.next_screen = None
    
    def initialize(self):
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(self.title)
        self.running = True
        
        self.setup_navbar()
        self.setup_ui()
    
    def setup_navbar(self):
        self.navbar.set_callbacks(
            home_callback=self.home_action,
            settings_callback=self.settings_action
        )
    
    def setup_ui(self):
        pass
    
    def home_action(self):
        from src.windows.screens.game_selection.mode_selection import ModeSelectionScreen
        self.next_screen = ModeSelectionScreen
        self.running = False
    
    def settings_action(self):
        Logger.info("BaseScreen", "Settings button pressed - not implemented yet")
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                return False
            
            self.navbar.handle_events(event)
            self.handle_screen_events(event)
        
        return True
    
    def handle_screen_events(self, event):
        pass
    
    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        self.navbar.update(mouse_pos)
        self.update_screen(mouse_pos)
    
    def update_screen(self, mouse_pos):
        pass
    
    def draw(self):
        self.screen.fill((240, 240, 240))
        self.draw_screen()
        self.navbar.draw(self.screen)
        pygame.display.flip()
    
    def draw_screen(self):
        pass
    
    def run(self):
        self.initialize()
        
        while self.running:
            #dt = self.clock.tick(self.fps) / 1000.0
            
            if not self.handle_events():
                return None
            
            self.update()
            self.draw()
        
        result = None
        if self.next_screen:
            result = self.next_screen()
        
        return result
    
    def cleanup(self):
        pass 