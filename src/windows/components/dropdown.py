import pygame

class Dropdown:
    """
    classe : représente une liste déroulante pour sélectionner une option.
    """
    def __init__(self, x, y, width, height, options, default_index=0):
        """
        constructeur : initialise la liste déroulante.

        params:
            x, y: coordonnées du coin supérieur gauche.
            width, height: dimensions de la boîte principale.
            options: liste des chaînes de caractères à afficher.
            default_index: index de l'option sélectionnée par défaut.
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options
        self.selected_index = default_index
        self.font = pygame.font.SysFont('Arial', 16)
        self.color = (240, 240, 240) # couleur de fond
        self.text_color = (0, 0, 0)
        self.is_open = False # true si la liste des options est visible
        self.option_height = 30 # hauteur de chaque option dans la liste
        self.option_rects = [] # rectangles pour chaque option (pour la détection de clic)
        self.update_option_rects()
        
    def update_option_rects(self):
        """
        procédure : calcule les rectangles pour chaque option de la liste déroulante.
        appelée à l'initialisation et potentiellement si les options changent.
        """
        self.option_rects = []
        for i in range(len(self.options)):
            # positionne chaque option sous la boîte principale
            self.option_rects.append(
                pygame.Rect(self.rect.x, self.rect.y + self.rect.height + i * self.option_height, 
                           self.rect.width, self.option_height)
            )
    
    def draw(self, surface):
        """
        procédure : dessine la liste déroulante sur la surface donnée.

        params:
            surface: surface pygame sur laquelle dessiner.
        """
        # dessine la boîte principale
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 1) # bordure
        
        # dessine l'option actuellement sélectionnée
        if 0 <= self.selected_index < len(self.options):
            text = self.options[self.selected_index]
            text_surface = self.font.render(text, True, self.text_color)
            # aligne le texte à gauche avec une petite marge
            text_rect = text_surface.get_rect(midleft=(self.rect.left + 5, self.rect.centery))
            surface.blit(text_surface, text_rect)
        
        # dessine la flèche déroulante
        arrow_points = [
            (self.rect.right - 15, self.rect.centery - 5), # haut gauche
            (self.rect.right - 5, self.rect.centery - 5),  # haut droit
            (self.rect.right - 10, self.rect.centery + 5) # bas milieu
        ]
        pygame.draw.polygon(surface, (0, 0, 0), arrow_points)
        
        # dessine les options si la liste est ouverte
        if self.is_open:
            for i, option_rect in enumerate(self.option_rects):
                # couleur de fond légèrement différente pour les options
                pygame.draw.rect(surface, (230, 230, 230), option_rect)
                pygame.draw.rect(surface, (0, 0, 0), option_rect, 1) # bordure
                
                text = self.options[i]
                text_surface = self.font.render(text, True, self.text_color)
                text_rect = text_surface.get_rect(midleft=(option_rect.left + 5, option_rect.centery))
                surface.blit(text_surface, text_rect)
    
    def handle_event(self, event, pos):
        """
        procédure : gère les événements pygame pour la liste déroulante.
        ouvre/ferme la liste ou sélectionne une option au clic.

        params:
            event: événement pygame.
            pos: tuple (x, y) de la position de la souris.

        retour:
            bool: true si un clic a été géré par cet élément, false sinon.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # clic gauche
            # clic sur la boîte principale pour ouvrir/fermer
            if self.rect.collidepoint(pos):
                self.is_open = not self.is_open
                return True
            # clic sur une option si la liste est ouverte
            elif self.is_open:
                for i, option_rect in enumerate(self.option_rects):
                    if option_rect.collidepoint(pos):
                        #old_selection = self.get()
                        self.selected_index = i
                        self.is_open = False
                        #new_selection = self.get()
                        return True # clic géré
                # clic en dehors des options ferme la liste
                self.is_open = False
                # ne retourne pas true ici, car le clic n'était pas sur cet élément
        return False # clic non géré par cet élément
    
    def get(self):
        """
        fonction : retourne la valeur de l'option actuellement sélectionnée.

        retour:
            str | none: la chaîne de l'option sélectionnée, ou none si invalide.
        """
        if 0 <= self.selected_index < len(self.options):
            return self.options[self.selected_index]
        return None 