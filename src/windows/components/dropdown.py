import pygame
from typing import Optional, Callable, List, Tuple

class Dropdown:
    """
    classe : représente une liste déroulante pour sélectionner une option.
    """
    # variable statique pour suivre toutes les dropdowns ouvertes
    active_dropdown: Optional['Dropdown'] = None
    
    def __init__(self, x: int, y: int, width: int, height: int, options: List[str], default_index: int = 0, disabled: bool = False, callback: Optional[Callable] = None) -> None:
        """
        constructeur : initialise la liste déroulante.

        params:
            x, y - coordonnées du coin supérieur gauche.
            width, height - dimensions de la boîte principale.
            options - liste des chaînes de caractères à afficher.
            default_index - index de l'option sélectionnée par défaut.
            disabled - indique si la liste déroulante est désactivée.
            callback - fonction à appeler lorsque la sélection change.
        """
        self.rect: pygame.Rect = pygame.Rect(x, y, width, height)
        self.options: List[str] = options
        self.selected_index: int = default_index
        self.font: pygame.font.Font = pygame.font.SysFont('Arial', 16)
        self.color: Tuple[int, int, int] = (0, 0, 0)
        self.disabled_color: Tuple[int, int, int] = (70, 70, 70)
        self.text_color: Tuple[int, int, int] = (240, 240, 240)
        self.disabled_text_color: Tuple[int, int, int] = (170, 170, 170)
        self.is_open: bool = False
        self.option_height: int = 30
        self.option_rects: List[pygame.Rect] = []
        self.transparency: int = 171
        self.disabled: bool = disabled
        self.callback: Optional[Callable] = callback
        self.update_option_rects()
        
    def update_option_rects(self) -> None:
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
    
    def draw(self, surface: pygame.Surface) -> None:
        """
        procédure : dessine la liste déroulante sur la surface donnée.

        params:
            surface - surface pygame sur laquelle dessiner.
        """
        radius = min(int(self.rect.height * 0.2), 10)
        
        # dessin du container principal
        dropdown_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        
        if self.disabled:
            bg_color = self.disabled_color
        else:
            bg_color = self.color
            
        pygame.draw.rect(dropdown_surface, bg_color + (self.transparency,), dropdown_surface.get_rect(), 0, radius)
        
        border_color = (170, 170, 170, 255) if self.disabled else (240, 240, 240, 255)
        pygame.draw.rect(dropdown_surface, border_color, dropdown_surface.get_rect(), 1, radius)
        
        # affichage de l'élément sélectionné
        if 0 <= self.selected_index < len(self.options):
            text = self.options[self.selected_index]
            text_color = self.disabled_text_color if self.disabled else self.text_color
            text_surface = self.font.render(text, True, text_color)
            text_rect = text_surface.get_rect(midleft=(5, self.rect.height // 2))
            dropdown_surface.blit(text_surface, text_rect)
        
        # indicateur visuel (flèche)
        arrow_color = (170, 170, 170, 255) if self.disabled else (240, 240, 240, 255)
        arrow_points = [
            (self.rect.width - 15, self.rect.height // 2 - 5),
            (self.rect.width - 5, self.rect.height // 2 - 5),
            (self.rect.width - 10, self.rect.height // 2 + 5)
        ]
        pygame.draw.polygon(dropdown_surface, arrow_color, arrow_points)
        
        surface.blit(dropdown_surface, self.rect)
        
        # si ce dropdown est l'actif et ouvert, le menu sera dessiné à la fin du cycle de rendu
        if self.is_open and Dropdown.active_dropdown == self:
            self._prepare_overlay_options(surface)
    
    def _prepare_overlay_options(self, surface: pygame.Surface) -> None:
        """
        procédure : prépare le rendu des options du dropdown pour être dessinées comme overlay.
        
        params:
            surface - surface pygame principale sur laquelle dessiner.
        """
        # calcul de la position verticale pour éviter de sortir de l'écran
        screen_height = surface.get_height()
        dropdown_height = len(self.options) * self.option_height
        
        # détermine si le dropdown doit s'afficher au-dessus ou en-dessous
        if self.rect.bottom + dropdown_height > screen_height:
            # s'affiche au-dessus si pas assez de place en-dessous
            start_y = self.rect.top - dropdown_height
        else:
            # s'affiche en-dessous normalement
            start_y = self.rect.bottom
        
        # mise à jour des rectangles d'options
        self.option_rects = []
        for i in range(len(self.options)):
            self.option_rects.append(
                pygame.Rect(self.rect.x, start_y + i * self.option_height, 
                           self.rect.width, self.option_height)
            )
    
    @classmethod
    def render_active_dropdown(cls, surface: pygame.Surface) -> None:
        """
        procédure : dessine le dropdown actif comme un overlay sur toute la surface.
        
        params:
            surface - surface pygame sur laquelle dessiner.
        """
        if cls.active_dropdown is None or not cls.active_dropdown.is_open:
            return
        
        dropdown = cls.active_dropdown
        radius = min(int(dropdown.rect.height * 0.2), 10)
        
        # créer une surface overlay de la taille de l'écran
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        
        # dessiner un arrière-plan semi-transparent pour mettre en évidence le dropdown
        overlay.fill((30, 30, 30, 180)) 
        # dessiner chaque option
        for i, option_rect in enumerate(dropdown.option_rects):
            option_surface = pygame.Surface((option_rect.width, dropdown.option_height), pygame.SRCALPHA)
            
            # fond semi-transparent pour chaque option
            pygame.draw.rect(option_surface, (20, 20, 20, 255), option_surface.get_rect(), 0, radius) 
            
            # bordure claire
            pygame.draw.rect(option_surface, (240, 240, 240, 255), option_surface.get_rect(), 1, radius)
            
            # texte de l'option
            text = dropdown.options[i]
            text_surface = dropdown.font.render(text, True, dropdown.text_color)
            text_rect = text_surface.get_rect(midleft=(5, dropdown.option_height // 2))
            option_surface.blit(text_surface, text_rect)
            
            overlay.blit(option_surface, option_rect)
        
        # dessiner l'overlay sur la surface principale à la FIN du cycle de rendu
        surface.blit(overlay, (0, 0))
    
    @classmethod
    def check_dropdown_click(cls, event: pygame.event.Event) -> bool:
        if cls.active_dropdown is not None and cls.active_dropdown.is_open:
            return True
        return False
    
    @classmethod
    def handle_global_event(cls, event: pygame.event.Event, pos: Tuple[int, int]) -> bool:
        if cls.active_dropdown is not None and cls.active_dropdown.is_open:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                dropdown = cls.active_dropdown
                option_clicked = False
                
                for i, option_rect in enumerate(dropdown.option_rects):
                    if option_rect.collidepoint(pos):
                        previous_index = dropdown.selected_index
                        dropdown.selected_index = i
                        dropdown.is_open = False
                        cls.active_dropdown = None
                        option_clicked = True
                        
                        if dropdown.callback is not None and previous_index != i:
                            dropdown.callback()
                        break
                
                if not option_clicked:
                    dropdown.is_open = False
                    cls.active_dropdown = None
                
                return True
        return False
    
    def handle_event(self, event: pygame.event.Event, pos: Tuple[int, int]) -> bool:
        """
        fonction : gère les événements pygame pour la liste déroulante.

        params:
            event - événement pygame.
            pos - tuple (x, y) de la position de la souris.

        retour : True si un clic a été géré par cet élément, False sinon.
        """
        if self.disabled:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(pos):
                if not self.is_open:
                    if Dropdown.active_dropdown is not None:
                        Dropdown.active_dropdown.is_open = False
                    Dropdown.active_dropdown = self
                    self.is_open = True
                else:
                    self.is_open = False
                    Dropdown.active_dropdown = None
                return True
        return False
    
    def get(self) -> Optional[str]:
        """
        fonction : retourne la valeur de l'option actuellement sélectionnée.

        retour : la chaîne de l'option sélectionnée, ou None si invalide.
        """
        if 0 <= self.selected_index < len(self.options):
            return self.options[self.selected_index]
        return None