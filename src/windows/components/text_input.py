import pygame

class TextInput:
    """
    classe : représente un champ de saisie de texte simple.
    """
    def __init__(self, x, y, width, height, placeholder="", initial_text="", disabled=False):
        """
        constructeur : initialise le champ de saisie.

        params:
            x, y - coordonnées du coin supérieur gauche.
            width, height - dimensions du champ.
            placeholder - texte affiché lorsque le champ est vide.
            initial_text - texte initial dans le champ.
            disabled - indique si le champ est désactivé.
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = initial_text
        self.font = pygame.font.SysFont('Arial', 24)
        self.inactive_color = (30, 30, 30)
        self.active_color = (50, 50, 50)
        self.disabled_color = (70, 70, 70)
        self.text_color = (220, 220, 220)
        self.disabled_text_color = (170, 170, 170)
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0
        self.transparency = 171
        self.placeholder = placeholder
        self.placeholder_color = (130, 130, 130)
        self.disabled = disabled
    
    def draw(self, surface):
        """
        procédure : dessine le champ de saisie sur la surface donnée.

        params:
            surface - surface pygame sur laquelle dessiner.
        """
        radius = int(self.rect.height * 0.3)
        
        input_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        
        if self.disabled:
            background_color = self.disabled_color
        else:
            background_color = self.active_color if self.active else self.inactive_color
        
        pygame.draw.rect(input_surface, background_color + (self.transparency,), input_surface.get_rect(), 0, radius)
        
        if self.active and not self.disabled:
            focus_color = (30, 30, 30, 200)
            pygame.draw.rect(input_surface, focus_color, input_surface.get_rect(), 2, radius)
        
        left_margin = self.rect.height // 4
        
        if self.text:
            text_color = self.disabled_text_color if self.disabled else self.text_color
            text_surface = self.font.render(self.text, True, text_color)
            text_rect = text_surface.get_rect(midleft=(left_margin, self.rect.height // 2))
            input_surface.blit(text_surface, text_rect, area=pygame.Rect(0, 0, self.rect.width - left_margin * 2, self.rect.height))
        elif self.placeholder and not self.active:
            placeholder_surface = self.font.render(self.placeholder, True, self.placeholder_color)
            placeholder_rect = placeholder_surface.get_rect(midleft=(left_margin, self.rect.height // 2))
            input_surface.blit(placeholder_surface, placeholder_rect)
        
        if self.active and self.cursor_visible and not self.disabled:
            text_width = self.font.size(self.text)[0]
            cursor_x = left_margin + min(text_width, self.rect.width - left_margin * 2)
            
            cursor_color = (220, 220, 220, 255)
            pygame.draw.line(input_surface, cursor_color, 
                            (cursor_x, self.rect.height // 4), 
                            (cursor_x, self.rect.height * 3 // 4), 2)
        
        surface.blit(input_surface, self.rect)
    
    def handle_event(self, event, pos):
        """
        fonction : gère les événements pygame pour le champ de saisie.

        params:
            event - événement pygame.
            pos - tuple (x, y) de la position de la souris.

        retour : True si l'événement a été géré par ce champ, False sinon.
        """
        if self.disabled:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            was_active = self.active
            self.active = self.rect.collidepoint(pos)
            if self.active != was_active:
                self.cursor_visible = True
                self.cursor_timer = 0
                return True
        
        if not self.active:
            return False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
                self.cursor_visible = True
                self.cursor_timer = 0
            elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                self.active = False
            elif event.unicode.isprintable():
                margin = self.rect.height // 4
                if self.font.size(self.text + event.unicode)[0] < self.rect.width - margin * 3:
                    self.text += event.unicode
                    self.cursor_visible = True
                    self.cursor_timer = 0
            return True
            
        return False
    
    def update(self, dt):
        """
        procédure : met à jour l'état du champ (clignotement du curseur).

        params:
            dt - temps écoulé depuis la dernière frame en millisecondes.
        """
        if self.active and not self.disabled:
            self.cursor_timer += dt
            if self.cursor_timer >= 500:
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer %= 500
    
    def get(self):
        """
        fonction : retourne le texte actuellement contenu dans le champ.

        retour : le texte saisi.
        """
        return self.text 