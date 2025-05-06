import pygame

class TextInput:
    """
    classe : représente un champ de saisie de texte simple.
    """
    def __init__(self, x, y, width, height, initial_text=""):
        """
        constructeur : initialise le champ de saisie.

        params:
            x, y: coordonnées du coin supérieur gauche.
            width, height: dimensions du champ.
            initial_text: texte initial affiché dans le champ.
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = initial_text
        self.font = pygame.font.SysFont('Arial', 16)
        self.color = (240, 240, 240) # couleur de fond quand inactif
        self.active_color = (255, 255, 255) # couleur de fond quand actif
        self.text_color = (0, 0, 0)
        self.active = False # true si le champ est sélectionné pour la saisie
        self.cursor_visible = True # visibilité du curseur clignotant
        self.cursor_timer = 0 # timer pour le clignotement du curseur
    
    def draw(self, surface):
        """
        procédure : dessine le champ de saisie sur la surface donnée.

        params:
            surface: surface pygame sur laquelle dessiner.
        """
        # choisit la couleur de fond en fonction de l'état actif/inactif
        background_color = self.active_color if self.active else self.color
        pygame.draw.rect(surface, background_color, self.rect)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 1) # bordure
        
        # dessine le texte saisi
        if self.text:
            text_surface = self.font.render(self.text, True, self.text_color)
            # aligne le texte à gauche avec une marge
            text_rect = text_surface.get_rect(midleft=(self.rect.left + 5, self.rect.centery))
            # assure que le texte ne dépasse pas la boîte (simple clipping)
            surface.blit(text_surface, text_rect, area=pygame.Rect(0, 0, self.rect.width - 10, self.rect.height))
        
        # dessine le curseur clignotant si actif
        if self.active and self.cursor_visible:
            # calcule la position x du curseur (après le texte)
            text_width = self.font.size(self.text)[0]
            cursor_x = self.rect.left + 5 + min(text_width, self.rect.width - 10)
            pygame.draw.line(surface, self.text_color, 
                            (cursor_x, self.rect.top + 5), 
                            (cursor_x, self.rect.bottom - 5), 1)
    
    def handle_event(self, event, pos):
        """
        procédure : gère les événements pygame pour le champ de saisie.
        active/désactive le champ au clic, gère la saisie clavier.

        params:
            event: événement pygame.
            pos: tuple (x, y) de la position de la souris (pour les clics).

        retour:
            bool: true si l'événement a été géré par ce champ, false sinon.
        """
        # clic pour activer/désactiver
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            was_active = self.active
            self.active = self.rect.collidepoint(pos)
            if self.active != was_active:
                return self.active # retourne true si le clic l'a activé
        
        # ignore les autres événements si pas actif
        if not self.active:
            return False
            
        # gestion de la saisie clavier
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                self.active = False # désactive à l'appui sur entrée
            elif event.unicode.isprintable():
                # ajoute le caractère si imprimable et si la largeur le permet (simple vérification)
                if self.font.size(self.text + event.unicode)[0] < self.rect.width - 15:
                     self.text += event.unicode
            return True # événement clavier géré
            
        return False # événement non géré
    
    def update(self, dt):
        """
        procédure : met à jour l'état du champ (clignotement du curseur).
        doit être appelée à chaque frame.

        params:
            dt: temps écoulé depuis la dernière frame en millisecondes.
        """
        if self.active:
            self.cursor_timer += dt
            if self.cursor_timer >= 500:  # fréquence de clignotement 500ms
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer %= 500 # reset timer
    
    def get(self):
        """
        fonction : retourne le texte actuellement contenu dans le champ.

        retour:
            str: le texte saisi.
        """
        return self.text 