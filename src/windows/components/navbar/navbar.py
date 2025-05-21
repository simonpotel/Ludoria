import pygame
import os
from src.windows.components.button import Button
from src.windows.components.image_button import ImageButton
from src.utils.logger import Logger
from src.windows.font_manager import FontManager

class NavBar:
    def __init__(self, screen_width, height=50):
        self.width = screen_width
        self.height = height
        self.background_color = (0, 0, 0, 0) 
        
        self.font_manager = FontManager()
        
        btn_size = 40
        padding = 5
        
        star_icon_path = "assets/Basic_GUI_Bundle/Icons/Icon_Small_Star.png"
        menu_icon_path = "assets/Basic_GUI_Bundle/Icons/Icon_Small_WhiteOutline_Menu.png"
        button_bg_path = "assets/Basic_GUI_Bundle/ButtonsIcons/IconButton_Small_Blank_Rounded.png"
        
        self.home_button = ImageButton(
            padding, 
            (self.height - btn_size) // 2, 
            btn_size, 
            btn_size, 
            "", 
            self.home_action,
            bg_image_path=button_bg_path,
            icon_path=star_icon_path
        )
        
        self.settings_button = ImageButton(
            self.width - btn_size - padding, 
            (self.height - btn_size) // 2, 
            btn_size, 
            btn_size, 
            "", 
            self.settings_action,
            bg_image_path=button_bg_path,
            icon_path=menu_icon_path
        )
        
        self.home_callback = None 
        self.settings_callback = None 
    
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
        self.home_button.handle_event(event)
        self.settings_button.handle_event(event)
    
    def update(self, mouse_pos):
        self.home_button.check_hover(mouse_pos)
        self.settings_button.check_hover(mouse_pos)
    
    def draw(self, screen):
        navbar_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        navbar_surface.fill(self.background_color)
        screen.blit(navbar_surface, (0,0))
        
        self.home_button.draw(screen)
        self.settings_button.draw(screen) 