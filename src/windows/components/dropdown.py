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
        self.color = (0, 0, 0) # couleur de fond
        self.text_color = (240, 240, 240)
        self.is_open = False # true si la liste des options est visible
        self.option_height = 30 # hauteur de chaque option dans la liste
        self.option_rects = [] # rectangles pour chaque option (pour la détection de clic)
        self.transparency = 171  # 67%
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
        # Rayon des coins arrondis
        radius = min(int(self.rect.height * 0.2), 10)
        
        # Crée une surface transparente pour la boîte principale
        dropdown_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        
        # Dessine le rectangle avec des coins arrondis et transparence
        pygame.draw.rect(dropdown_surface, self.color + (self.transparency,), dropdown_surface.get_rect(), 0, radius)
        
        # Dessine la bordure avec des coins arrondis (bordure non transparente)
        pygame.draw.rect(dropdown_surface, (240, 240, 240, 255), dropdown_surface.get_rect(), 1, radius)
        
        # dessine l'option actuellement sélectionnée
        if 0 <= self.selected_index < len(self.options):
            text = self.options[self.selected_index]
            text_surface = self.font.render(text, True, self.text_color)
            # aligne le texte à gauche avec une petite marge
            text_rect = text_surface.get_rect(midleft=(5, self.rect.height // 2))
            dropdown_surface.blit(text_surface, text_rect)
        
        # dessine la flèche déroulante
        arrow_points = [
            (self.rect.width - 15, self.rect.height // 2 - 5), # haut gauche
            (self.rect.width - 5, self.rect.height // 2 - 5),  # haut droit
            (self.rect.width - 10, self.rect.height // 2 + 5) # bas milieu
        ]
        pygame.draw.polygon(dropdown_surface, (240, 240, 240, 255), arrow_points)
        
        # Affiche la surface du dropdown sur la surface principale
        surface.blit(dropdown_surface, self.rect)
        
        # dessine les options si la liste est ouverte
        if self.is_open:
            for i, option_rect in enumerate(self.option_rects):
                # Crée une surface transparente pour chaque option
                option_surface = pygame.Surface((option_rect.width, option_rect.height), pygame.SRCALPHA)
                
                # Dessine le rectangle avec des coins arrondis et transparence
                pygame.draw.rect(option_surface, self.color + (self.transparency,), option_surface.get_rect(), 0, radius)
                
                # Dessine la bordure avec des coins arrondis (bordure non transparente)
                pygame.draw.rect(option_surface, (240, 240, 240, 255), option_surface.get_rect(), 1, radius)
                
                text = self.options[i]
                text_surface = self.font.render(text, True, self.text_color)
                text_rect = text_surface.get_rect(midleft=(5, option_rect.height // 2))
                option_surface.blit(text_surface, text_rect)
                
                # Affiche la surface de l'option sur la surface principale
                surface.blit(option_surface, option_rect)
    
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