import pygame

class Button:
    """
    classe : représente un bouton cliquable simple dans l'interface.
    """
    def __init__(self, x, y, width, height, text, action=None):
        """
        constructeur : initialise un bouton.

        params:
            x, y: coordonnées du coin supérieur gauche.
            width, height: dimensions du bouton.
            text: texte affiché sur le bouton.
            action: fonction à appeler lors du clic (callback).
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        # couleurs pour les états normal et survolé
        self.color = (200, 200, 200)
        self.hover_color = (160, 160, 160)
        self.text_color = (0, 0, 0)
        self.font = pygame.font.SysFont('Arial', 16)
        self.is_hover = False # true si la souris est sur le bouton
    
    def draw(self, surface):
        """
        procédure : dessine le bouton sur la surface donnée.
        change de couleur si la souris est dessus.

        params:
            surface: surface pygame sur laquelle dessiner.
        """
        color = self.hover_color if self.is_hover else self.color
        pygame.draw.rect(surface, color, self.rect) # fond
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 1) # bordure
        
        # dessine le texte centré
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    
    def check_hover(self, pos):
        """
        procédure : vérifie si la position donnée est sur le bouton.

        params:
            pos: tuple (x, y) de la position de la souris.
        """
        self.is_hover = self.rect.collidepoint(pos)
        
    def handle_event(self, event):
        """
        procédure : gère les événements pygame pour ce bouton.
        déclenche l'action si un clic gauche survient pendant le survol.

        params:
            event: événement pygame.

        retour:
            bool: true si l'action a été déclenchée, false sinon.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # clic gauche
            if self.is_hover and self.action:
                self.action()
                return True
        return False 