import pygame
from typing import Optional, Callable, Tuple
from src.windows.font_manager import FontManager

class Button:
    """
    classe : représente un bouton cliquable simple dans l'interface.
    """
    def __init__(self, x: int, y: int, width: int, height: int, text: str, action: Optional[Callable] = None, disabled: bool = False, font_size: int = 24) -> None:
        """
        constructeur : initialise un bouton.

        params:
            x, y - coordonnées du coin supérieur gauche.
            width, height - dimensions du bouton.
            text - texte affiché sur le bouton.
            action - fonction à appeler lors du clic (callback).
            disabled - indique si le bouton est désactivé.
            font_size - taille de la police (par défaut 24)
        """
        self.rect: pygame.Rect = pygame.Rect(x, y, width, height)
        self.text: str = text
        self.action: Optional[Callable] = action
        # couleurs pour les états normal et survolé
        self.color: Tuple[int, int, int] = (0, 0, 0)
        self.hover_color: Tuple[int, int, int] = (160, 160, 160)
        self.disabled_color: Tuple[int, int, int] = (70, 70, 70)
        self.text_color: Tuple[int, int, int] = (255, 255, 255)
        self.disabled_text_color: Tuple[int, int, int] = (170, 170, 170)
        self.font_size: int = font_size
        self.font_manager = FontManager()
        self.is_hover: bool = False # true si la souris est sur le bouton
        self.transparency: int = 171  # 67% de 255 (255 * 0.67 ≈ 171)
        self.disabled: bool = disabled
    
    def draw(self, surface: pygame.Surface) -> None:
        """
        procédure : dessine le bouton sur la surface donnée.
        change de couleur si la souris est dessus.

        params:
            surface - surface pygame sur laquelle dessiner.
        """
        # sélection de la couleur selon l'état de survol
        if self.disabled:
            color = self.disabled_color
        else:
            color = self.hover_color if self.is_hover else self.color
        
        # rayon des coins arrondis 
        radius = min(int(self.rect.height * 0.2), 10)
        
        # création de la surface transparente pour le bouton
        button_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        
        # dessin du fond avec coins arrondis
        pygame.draw.rect(button_surface, color + (self.transparency,), button_surface.get_rect(), 0, radius)
        
        # ajout de la bordure
        border_color = (100, 100, 100, self.transparency) if self.disabled else (0, 0, 0, self.transparency)
        pygame.draw.rect(button_surface, border_color, button_surface.get_rect(), 1, radius)
        
        # ajout du texte centré avec la police personnalisée
        text_color = self.disabled_text_color if self.disabled else self.text_color
        font = self.font_manager.get_font(self.font_size)
        text_surface = font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=(self.rect.width // 2, self.rect.height // 2))
        button_surface.blit(text_surface, text_rect)
        
        # affichage final du bouton
        surface.blit(button_surface, self.rect)
    
    def check_hover(self, pos: Tuple[int, int]) -> None:
        """
        procédure : vérifie si la position donnée est sur le bouton.

        params:
            pos - tuple (x, y) de la position de la souris.
        """
        if self.disabled:
            self.is_hover = False
        else:
            self.is_hover = self.rect.collidepoint(pos)
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        fonction : gère les événements pygame pour ce bouton.

        params:
            event - événement pygame.

        retour : True si l'action a été déclenchée, False sinon.
        """
        # détection du clic et déclenchement de l'action associée
        if self.disabled:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hover and self.action:
                self.action()
                return True
        return False