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
        self.text = ""  # Aucun texte par défaut
        self.font = pygame.font.SysFont('Arial', 24)
        self.inactive_color = (30, 30, 30)  # Couleur de fond noire quand inactif
        self.active_color = (50, 50, 50)  # Couleur de fond légèrement plus claire quand actif
        self.text_color = (220, 220, 220)  # Texte clair sur fond sombre
        self.active = False  # true si le champ est sélectionné pour la saisie
        self.cursor_visible = True  # visibilité du curseur clignotant
        self.cursor_timer = 0  # timer pour le clignotement du curseur
        self.transparency = 171  # 67% d'opacité
        self.placeholder = initial_text  # Texte d'indication (placeholder)
        self.placeholder_color = (130, 130, 130)  # Couleur grise pour le placeholder
    
    def draw(self, surface):
        """
        procédure : dessine le champ de saisie sur la surface donnée.

        params:
            surface: surface pygame sur laquelle dessiner.
        """
        # Rayon des coins arrondis (30% de la hauteur)
        radius = int(self.rect.height * 0.3)
        
        # Crée une surface transparente pour le champ de saisie
        input_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        
        # Choisit la couleur de fond en fonction de l'état actif/inactif
        background_color = self.active_color if self.active else self.inactive_color
        
        # Dessine le rectangle principal avec des coins arrondis et transparence
        pygame.draw.rect(input_surface, background_color + (self.transparency,), input_surface.get_rect(), 0, radius)
        
        # Ajoute un effet de focus si actif
        if self.active:
            # Dessine un contour plus brillant quand le champ est actif
            focus_color = (30, 30, 30, 200)  # Bleu subtil
            pygame.draw.rect(input_surface, focus_color, input_surface.get_rect(), 2, radius)
        
        # Calcule la marge pour le texte (proportionnelle à la hauteur)
        left_margin = self.rect.height // 4
        
        # Dessine le texte saisi ou le placeholder
        if self.text:
            # Texte saisi par l'utilisateur
            text_surface = self.font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(midleft=(left_margin, self.rect.height // 2))
            input_surface.blit(text_surface, text_rect, area=pygame.Rect(0, 0, self.rect.width - left_margin * 2, self.rect.height))
        elif self.placeholder and not self.active:
            # Affiche le placeholder si aucun texte et pas actif
            placeholder_surface = self.font.render(self.placeholder, True, self.placeholder_color)
            placeholder_rect = placeholder_surface.get_rect(midleft=(left_margin, self.rect.height // 2))
            input_surface.blit(placeholder_surface, placeholder_rect)
        
        # Dessine le curseur clignotant si actif
        if self.active and self.cursor_visible:
            # Calcule la position x du curseur (après le texte)
            text_width = self.font.size(self.text)[0]
            cursor_x = left_margin + min(text_width, self.rect.width - left_margin * 2)
            
            # Dessine une ligne verticale pour le curseur
            cursor_color = (220, 220, 220, 255)  # Couleur claire pour le curseur
            pygame.draw.line(input_surface, cursor_color, 
                            (cursor_x, self.rect.height // 4), 
                            (cursor_x, self.rect.height * 3 // 4), 2)
        
        # Affiche la surface du champ de saisie sur la surface principale
        surface.blit(input_surface, self.rect)
    
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
        # Clic pour activer/désactiver
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            was_active = self.active
            self.active = self.rect.collidepoint(pos)
            if self.active != was_active:
                # Réinitialiser le timer du curseur pour qu'il soit visible immédiatement
                self.cursor_visible = True
                self.cursor_timer = 0
                return True # Retourne true si le clic a changé l'état
        
        # Ignore les autres événements si pas actif
        if not self.active:
            return False
            
        # Gestion de la saisie clavier
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
                # Réinitialiser le timer du curseur
                self.cursor_visible = True
                self.cursor_timer = 0
            elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                self.active = False # Désactive à l'appui sur entrée
            elif event.unicode.isprintable():
                # Ajoute le caractère si imprimable et si la largeur le permet
                margin = self.rect.height // 4
                if self.font.size(self.text + event.unicode)[0] < self.rect.width - margin * 3:
                    self.text += event.unicode
                    # Réinitialiser le timer du curseur
                    self.cursor_visible = True
                    self.cursor_timer = 0
            return True # Événement clavier géré
            
        return False # Événement non géré
    
    def update(self, dt):
        """
        procédure : met à jour l'état du champ (clignotement du curseur).
        doit être appelée à chaque frame.

        params:
            dt: temps écoulé depuis la dernière frame en millisecondes.
        """
        if self.active:
            self.cursor_timer += dt
            if self.cursor_timer >= 500:  # Fréquence de clignotement 500ms
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer %= 500 # Reset timer
    
    def get(self):
        """
        fonction : retourne le texte actuellement contenu dans le champ.

        retour:
            str: le texte saisi.
        """
        return self.text 