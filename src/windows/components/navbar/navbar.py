import pygame
import os
from src.windows.components.button import Button
from src.utils.logger import Logger

class NavBar:
    def __init__(self, screen_width, height=50):
        self.width = screen_width
        self.height = height
        self.background_color = (50, 50, 50)
        
        # dimensions des boutons
        home_btn_width = 40
        settings_btn_width = 40
        padding = 10
        
        self.home_button = Button(
            padding, 
            (self.height - 30) // 2, 
            home_btn_width, 
            30, 
            "⌂", 
            self.home_action
        )
        
        self.settings_button = Button(
            self.width - settings_btn_width - padding, 
            (self.height - 30) // 2, 
            settings_btn_width, 
            30, 
            "⚙", 
            self.settings_action
        )
        
        self.title = "Ludoria"
        self.title_font = pygame.font.SysFont('Arial', 22, bold=True)
        
        self.home_callback = None # callback pour le bouton home (sera une fonction qui sera appelée lorsque le bouton home sera cliqué)
        self.settings_callback = None # callback pour le bouton settings (sera une fonction qui sera appelée lorsque le bouton settings sera cliqué)
    
    def set_callbacks(self, home_callback=None, settings_callback=None):
        self.home_callback = home_callback
        self.settings_callback = settings_callback
    
    def home_action(self):
        if self.home_callback:
            self.home_callback()
        else:
            Logger.warning("NavBar", "Home button pressed but no callback set")
    
    def settings_action(self):
        if self.settings_callback:
            self.settings_callback()
        else:
            Logger.warning("NavBar", "Settings button pressed but no callback set")
    
    def handle_events(self, event):
        # gestion des événements pour les boutons home et settings (appel des callbacks)
        self.home_button.handle_event(event)
        self.settings_button.handle_event(event)
    
    def update(self, mouse_pos):
        # mise à jour de la position de la souris pour les boutons home et settings
        self.home_button.check_hover(mouse_pos)
        self.settings_button.check_hover(mouse_pos)
    
    def draw(self, screen):
        # dessin du fond de la navbar
        pygame.draw.rect(screen, self.background_color, (0, 0, self.width, self.height))
        
        # dessin du titre de la navbar
        title_surface = self.title_font.render(self.title, True, (255, 255, 255))
        title_x = (self.width - title_surface.get_width()) // 2
        title_y = (self.height - title_surface.get_height()) // 2
        screen.blit(title_surface, (title_x, title_y))
        
        self.home_button.draw(screen)
        self.settings_button.draw(screen) 