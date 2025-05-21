import pygame

class ImageButton:
    """
    classe : représente un bouton avec une image de fond.
    """
    def __init__(self, x, y, width, height, text, action=None, bg_image_path="assets/cta_background.png", 
                 font=None, icon_path=None, text_color=(255, 255, 255)):
        """
        constructeur : initialise un bouton avec image.

        params:
            x, y - coordonnées du coin supérieur gauche.
            width, height - dimensions du bouton.
            text - texte affiché sur le bouton.
            action - fonction à appeler lors du clic.
            bg_image_path - chemin vers l'image de fond.
            font - police à utiliser (optional)
            icon_path - chemin vers une icône à afficher (optional)
            text_color - couleur du texte
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.x = x  
        self.y = y
        self.width = width
        self.height = height
        self.text = text.upper()
        self.action = action
        self.text_color = text_color
        self.font = font if font else pygame.font.SysFont('Arial', 20, bold=True)
        self.is_hover = False
        self.bg_image_path = bg_image_path
        self.bg_image = None
        self.icon_path = icon_path
        self.icon_image = None
        
        self.load_image()
        if self.icon_path:
            self.load_icon()
        
    def load_image(self):
        """
        procédure : charge l'image de fond du bouton.
        """
        try:
            self.original_image = pygame.image.load(self.bg_image_path).convert_alpha()
            
            self.bg_image = pygame.transform.smoothscale(
                self.original_image, (self.width, self.height)
            )
        except pygame.error:
            self.bg_image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            self.bg_image.fill((60, 60, 60, 230))
    
    def load_icon(self):
        """
        procédure : charge l'icône du bouton.
        """
        try:
            original_icon = pygame.image.load(self.icon_path).convert_alpha()
            icon_size = min(self.rect.width, self.rect.height) * 0.6
            self.icon_image = pygame.transform.smoothscale(
                original_icon, (int(icon_size), int(icon_size))
            )
        except pygame.error as e:
            print(f"Error loading icon: {e}")
            self.icon_image = None
    
    def scale_image_preserve_ratio(self, image, target_width, target_height):
        """
        fonction : redimensionne l'image en préservant son ratio.

        params:
            image - image à redimensionner.
            target_width - largeur cible.
            target_height - hauteur cible.

        retour : l'image redimensionnée.
        """
        img_width, img_height = image.get_size()
        scale_ratio = max(target_width / img_width, target_height / img_height)
        new_width = int(img_width * scale_ratio)
        new_height = int(img_height * scale_ratio)
        scaled_image = pygame.transform.smoothscale(image, (new_width, new_height))
        
        final_image = pygame.Surface((target_width, target_height), pygame.SRCALPHA)
        x_offset = (target_width - new_width) // 2
        y_offset = (target_height - new_height) // 2
        final_image.blit(scaled_image, (x_offset, y_offset))
        
        return final_image
    
    def draw(self, surface):
        """
        procédure : dessine le bouton sur la surface donnée.

        params:
            surface - surface pygame sur laquelle dessiner.
        """
        surface.blit(self.bg_image, self.rect.topleft)
        
        if self.is_hover:
            hover_effect = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            hover_effect.fill((255, 255, 255, 30))
            surface.blit(hover_effect, self.rect.topleft)
        
        if self.icon_image:
            icon_rect = self.icon_image.get_rect(
                center=(self.rect.x + self.rect.width // 2, 
                        self.rect.y + self.rect.height // 2)
            )
            surface.blit(self.icon_image, icon_rect)
        elif self.text:
            text_surface = self.font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(
                center=(self.rect.x + self.rect.width // 2, 
                        self.rect.y + self.rect.height // 2)
            )
            surface.blit(text_surface, text_rect)
    
    def check_hover(self, pos):
        """
        procédure : vérifie si la position donnée est sur le bouton.

        params:
            pos - tuple (x, y) de la position de la souris.
        """
        self.is_hover = self.rect.collidepoint(pos)
        
    def handle_event(self, event):
        """
        fonction : gère les événements pygame pour ce bouton.

        params:
            event - événement pygame.

        retour : True si l'action a été déclenchée, False sinon.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hover and self.action:
                self.action()
                return True
        return False 