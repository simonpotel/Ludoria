import pygame
from src.windows.components.navbar import NavBar
from src.utils.logger import Logger
from src.utils.theme_manager import ThemeManager
from src.windows.font_manager import FontManager
from src.windows.components.dropdown import Dropdown
from src.utils.music_manager import MusicManager

class BaseScreen:
    def __init__(self, width=1280, height=720, title="Ludoria"):
        self.width = width
        self.height = height
        self.title = title
        self.running = False
        self.screen = None
        self.clock = pygame.time.Clock()
        self.fps = 30
        
        self.theme_manager = ThemeManager()
        self.font_manager = FontManager()
        self.music_manager = MusicManager()
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
        self.music_manager.play_music('menu')
    
    def setup_navbar(self):
        theme = self.theme_manager.current_theme
        Logger.info("BaseScreen", f"Initializing navbar with theme: {theme}")
        
        def quadrant_editor_action():
            from src.windows.screens.quadrant_editor_screen import QuadrantEditorScreen
            self.next_screen = QuadrantEditorScreen
            self.running = False
            Logger.info("BaseScreen", "Redirecting to Quadrant Editor Screen")
        
        self.navbar.set_callbacks(
            home_callback=self.home_action,
            settings_callback=self.menu_action,
            quadrant_editor_callback=quadrant_editor_action
        )
    
    def setup_ui(self):
        pass
    
    def home_action(self):
        from src.windows.screens.game_selection.mode_selection import ModeSelectionScreen
        
        if not isinstance(self, ModeSelectionScreen):
            self.next_screen = ModeSelectionScreen
            self.running = False
            Logger.info("BaseScreen", "Redirecting to Mode Selection Screen")
    
    def menu_action(self):
        from src.windows.screens.theme_selection import ThemeSelectionScreen
        self.next_screen = ThemeSelectionScreen
        self.running = False
        Logger.info("BaseScreen", "Redirecting to Theme Settings")
    
    def settings_action(self):
        self.menu_action()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                return False
            
            # vérifier les événements dropdown en premier
            mouse_pos = pygame.mouse.get_pos()
            
            # si un dropdown est actif, il a la priorité pour gérer les clics
            if Dropdown.handle_global_event(event, mouse_pos):
                continue
            
            # gérer les événements de la barre de navigation
            self.navbar.handle_event(event)
            
            # gérer les événements de la fenêtre
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
        theme_colors = {
            "tropique": (0, 150, 136),
            "grec": (156, 136, 255),
            "japon": (255, 138, 174),
            "nordique": (100, 181, 246),
            "sahara": (255, 183, 77),
            "pirate": (255, 183, 77),
            "urbain": (255, 183, 77),
            "montagne": (255, 183, 77)
        }
        
        theme = self.theme_manager.current_theme
        bg_color = theme_colors.get(theme, (240, 240, 240))
        
        bg_color = tuple(min(c + 80, 255) for c in bg_color)
        
        self.screen.fill(bg_color)
        self.draw_screen()
        self.navbar.draw(self.screen)
        
        # render le dropdown actif comme un overlay (après tout le reste)
        Dropdown.render_active_dropdown(self.screen)
        
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