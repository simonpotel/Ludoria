import pygame
import os
from typing import Dict, Optional
from src.utils.logger import Logger

class FontManager:
    """
    classe : singleton pour gérer les polices utilisées dans le jeu.
    """
    _instance: Optional['FontManager'] = None
    
    def __new__(cls) -> 'FontManager':
        if cls._instance is None:
            cls._instance = super(FontManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self) -> None:
        """
        procédure : initialise le gestionnaire de polices.
        """
        pygame.font.init()
        self.default_font_path: str = os.path.join("assets", "fonts", "BlackHanSans-Regular.ttf")
        self.fonts: Dict[str, pygame.font.Font] = {} # cache pour les polices chargées
        
    def get_font(self, size: int, font_path: Optional[str] = None) -> pygame.font.Font:
        """
        fonction : obtient une police avec la taille et le chemin spécifiés.
        
        params:
            size - taille de la police
            font_path - chemin vers la police (optional, uses default if None)
            
        retour : l'objet Font pygame
        """
        path = font_path if font_path else self.default_font_path
        font_key = f"{path}_{size}"
        
        if font_key not in self.fonts:
            try:
                self.fonts[font_key] = pygame.font.Font(path, size)
            except Exception as e:
                Logger.error(f"Error loading font from path '{path}' with size {size}: {e}")
                self.fonts[font_key] = pygame.font.SysFont('Arial', size)
                
        return self.fonts[font_key] 