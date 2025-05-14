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
        self.color = (0, 0, 0)
        self.hover_color = (160, 160, 160)
        self.text_color = (255, 255, 255)
        self.font = pygame.font.SysFont('Arial', 24)
        self.is_hover = False # true si la souris est sur le bouton
        self.transparency = 171  # 67% de 255 (255 * 0.67 ≈ 171)
    
    def draw(self, surface):
        """
        procédure : dessine le bouton sur la surface donnée.
        change de couleur si la souris est dessus.

        params:
            surface: surface pygame sur laquelle dessiner.
        """
        color = self.hover_color if self.is_hover else self.color
        
        # Rayon des coins arrondis (20% de la hauteur, mais pas plus de 10px)
        radius = min(int(self.rect.height * 0.2), 10)
        
        # Crée une surface transparente pour le bouton
        button_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        
        # Dessine le rectangle avec des coins arrondis et transparence
        pygame.draw.rect(button_surface, color + (self.transparency,), button_surface.get_rect(), 0, radius)
        
        # Dessine la bordure (également avec coins arrondis)
        pygame.draw.rect(button_surface, (0, 0, 0, self.transparency), button_surface.get_rect(), 1, radius)
        
        # dessine le texte centré
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=(self.rect.width // 2, self.rect.height // 2))
        button_surface.blit(text_surface, text_rect)
        
        # Affiche la surface du bouton sur la surface principale
        surface.blit(button_surface, self.rect)
    
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