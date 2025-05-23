import pygame
import os
from src.utils.logger import Logger

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
        self.default_font_path = None # chemin vers la police par défaut
        self.default_font_name = 'Arial' # police par défaut
        self.fonts = {} # cache pour les polices chargées
        
    def get_font(self, size, font_path=None):
        """
        fonction : obtient une police avec la taille et le chemin spécifiés.
        
        params:
            size - taille de la police
            font_path - chemin vers la police (optionnel, utilise la police par défaut si None)
            
        retour : l'objet Font pygame
        """
        if font_path:
            # charger depuis le chemin spécifié
            font_key = f"{font_path}_{size}"
            if font_key not in self.fonts:
                try:
                    self.fonts[font_key] = pygame.font.Font(font_path, size)
                except Exception as e:
                    Logger.error(f"Erreur lors du chargement de la police depuis le chemin '{font_path}' avec la taille {size}: {e}")
                    # retour à la police par défaut si le fichier de police spécifié échoue
                    self.fonts[font_key] = pygame.font.SysFont(self.default_font_name, size)
        else:
            # utiliser la police par défaut
            font_name = self.default_font_name
            font_key = f"{font_name}_{size}"
            if font_key not in self.fonts:
                try:
                    self.fonts[font_key] = pygame.font.SysFont(font_name, size)
                except Exception as e:
                    Logger.error(f"Erreur lors du chargement de la police système '{font_name}' avec la taille {size}: {e}")
                    # retour à une police système générique si la police par défaut échoue
                    self.fonts[font_key] = pygame.font.SysFont('Arial', size) # retour final

        return self.fonts[font_key] 