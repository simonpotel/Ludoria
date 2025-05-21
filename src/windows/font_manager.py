import pygame
import os

class FontManager:
    """
    classe : singleton pour gérer les polices utilisées dans le jeu.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FontManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """
        procédure : initialise le gestionnaire de polices.
        """
        pygame.font.init()
        self.default_font_path = os.path.join("assets", "fonts", "BlackHanSans-Regular.ttf")
        self.fonts = {} # cache pour les polices chargées
        
    def get_font(self, size, font_path=None):
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
                print(f"Error loading font: {e}")
                self.fonts[font_key] = pygame.font.SysFont('Arial', size)
                
        return self.fonts[font_key] 