import pygame
import os
from typing import Optional, Callable, Tuple
from src.windows.components.button import Button
from src.windows.components.image_button import ImageButton
from src.utils.logger import Logger
from src.windows.font_manager import FontManager
from src.utils.music_manager import MusicManager

class NavBar:
    def __init__(self, screen_width: int, height: int = 50) -> None:
        self.width: int = screen_width
        self.height: int = height
        self.background_color: Tuple[int, int, int, int] = (0, 0, 0, 0)
        
        self.font_manager = FontManager()
        self.music_manager = MusicManager()
        
        btn_size = 40
        padding = 5
        
        star_icon_path = "assets/Basic_GUI_Bundle/Icons/Icon_Small_Star.png"
        menu_icon_path = "assets/Basic_GUI_Bundle/Icons/Icon_Small_WhiteOutline_Menu.png"
        music_on_icon_path = "assets/Basic_GUI_Bundle/Icons/Icon_Small_WhiteOutline_Music.png"
        music_off_icon_path = "assets/Basic_GUI_Bundle/Icons/Icon_Small_WhiteOutline_MusicOff.png"
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
        
        self.music_button = ImageButton(
            self.width - (btn_size * 2) - (padding * 2),
            (self.height - btn_size) // 2,
            btn_size,
            btn_size,
            "",
            self.toggle_music,
            bg_image_path=button_bg_path,
            icon_path=music_on_icon_path
        )
        self.music_on_icon = pygame.image.load(music_on_icon_path)
        self.music_off_icon = pygame.image.load(music_off_icon_path)
        
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
        
        self.home_callback: Optional[Callable] = None 
        self.settings_callback: Optional[Callable] = None 
    
    def toggle_music(self) -> None:
        """
        procédure : active/désactive la musique et met à jour l'icône du bouton
        """
        self.music_manager.toggle_mute()
        if self.music_manager.is_muted:
            self.music_button.icon_path = "assets/Basic_GUI_Bundle/Icons/Icon_Small_WhiteOutline_MusicOff.png"
        else:
            self.music_button.icon_path = "assets/Basic_GUI_Bundle/Icons/Icon_Small_WhiteOutline_Music.png"
        self.music_button.load_icon()
        Logger.info("NavBar", f"Music {'muted' if self.music_manager.is_muted else 'unmuted'}")
    
    def set_callbacks(self, home_callback: Optional[Callable] = None, settings_callback: Optional[Callable] = None) -> None:
        self.home_callback = home_callback
        self.settings_callback = settings_callback
    
    def home_action(self) -> None:
        if self.home_callback:
            self.home_callback()
        else:
            Logger.warning("NavBar", "Home button pressed but no callback set")
    
    def settings_action(self) -> None:
        if self.settings_callback:
            self.settings_callback()
        else:
            Logger.warning("NavBar", "Settings button pressed but no callback set")
    
    def handle_events(self, event: pygame.event.Event) -> None:
        self.home_button.handle_event(event)
        self.music_button.handle_event(event)
        self.settings_button.handle_event(event)
    
    def update(self, mouse_pos: Tuple[int, int]) -> None:
        self.home_button.check_hover(mouse_pos)
        self.music_button.check_hover(mouse_pos)
        self.settings_button.check_hover(mouse_pos)
    
    def draw(self, screen: pygame.Surface) -> None:
        navbar_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        navbar_surface.fill(self.background_color)
        screen.blit(navbar_surface, (0,0))
        
        self.home_button.draw(screen)
        self.music_button.draw(screen)
        self.settings_button.draw(screen) 