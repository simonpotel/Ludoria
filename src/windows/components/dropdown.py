import pygame

class Dropdown:
    """
    classe : représente une liste déroulante pour sélectionner une option.
    """
    def __init__(self, x, y, width, height, options, default_index=0):
        """
        constructeur : initialise la liste déroulante.

        params:
            x, y - coordonnées du coin supérieur gauche.
            width, height - dimensions de la boîte principale.
            options - liste des chaînes de caractères à afficher.
            default_index - index de l'option sélectionnée par défaut.
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options
        self.selected_index = default_index
        self.font = pygame.font.SysFont('Arial', 16)
        self.color = (0, 0, 0)
        self.text_color = (240, 240, 240)
        self.is_open = False
        self.option_height = 30
        self.option_rects = []
        self.transparency = 171
        self.update_option_rects()
        
    def update_option_rects(self):
        """
        procédure : calcule les rectangles pour chaque option de la liste déroulante.
        """
        self.option_rects = []
        for i in range(len(self.options)):
            # position de chaque option sous le dropdown principal
            self.option_rects.append(
                pygame.Rect(self.rect.x, self.rect.y + self.rect.height + i * self.option_height, 
                           self.rect.width, self.option_height)
            )
    
    def draw(self, surface):
        """
        procédure : dessine la liste déroulante sur la surface donnée.

        params:
            surface - surface pygame sur laquelle dessiner.
        """
        radius = min(int(self.rect.height * 0.2), 10)
        
        # dessin du container principal
        dropdown_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        
        pygame.draw.rect(dropdown_surface, self.color + (self.transparency,), dropdown_surface.get_rect(), 0, radius)
        
        pygame.draw.rect(dropdown_surface, (240, 240, 240, 255), dropdown_surface.get_rect(), 1, radius)
        
        # affichage de l'élément sélectionné
        if 0 <= self.selected_index < len(self.options):
            text = self.options[self.selected_index]
            text_surface = self.font.render(text, True, self.text_color)
            text_rect = text_surface.get_rect(midleft=(5, self.rect.height // 2))
            dropdown_surface.blit(text_surface, text_rect)
        
        # indicateur visuel (flèche)
        arrow_points = [
            (self.rect.width - 15, self.rect.height // 2 - 5),
            (self.rect.width - 5, self.rect.height // 2 - 5),
            (self.rect.width - 10, self.rect.height // 2 + 5)
        ]
        pygame.draw.polygon(dropdown_surface, (240, 240, 240, 255), arrow_points)
        
        surface.blit(dropdown_surface, self.rect)
        
        # affichage du menu déroulant si ouvert
        if self.is_open:
            for i, option_rect in enumerate(self.option_rects):
                option_surface = pygame.Surface((option_rect.width, option_rect.height), pygame.SRCALPHA)
                
                pygame.draw.rect(option_surface, self.color + (self.transparency,), option_surface.get_rect(), 0, radius)
                
                pygame.draw.rect(option_surface, (240, 240, 240, 255), option_surface.get_rect(), 1, radius)
                
                text = self.options[i]
                text_surface = self.font.render(text, True, self.text_color)
                text_rect = text_surface.get_rect(midleft=(5, option_rect.height // 2))
                option_surface.blit(text_surface, text_rect)
                
                surface.blit(option_surface, option_rect)
    
    def handle_event(self, event, pos):
        """
        fonction : gère les événements pygame pour la liste déroulante.

        params:
            event - événement pygame.
            pos - tuple (x, y) de la position de la souris.

        retour : True si un clic a été géré par cet élément, False sinon.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # gestion du clic sur le dropdown principal
            if self.rect.collidepoint(pos):
                self.is_open = not self.is_open
                return True
            # gestion du clic sur une option quand le menu est ouvert
            elif self.is_open:
                for i, option_rect in enumerate(self.option_rects):
                    if option_rect.collidepoint(pos):
                        self.selected_index = i
                        self.is_open = False
                        return True
                # fermeture du menu si clic en dehors des options
                self.is_open = False
        return False
    
    def get(self):
        """
        fonction : retourne la valeur de l'option actuellement sélectionnée.

        retour : la chaîne de l'option sélectionnée, ou None si invalide.
        """
        if 0 <= self.selected_index < len(self.options):
            return self.options[self.selected_index]
        return None 