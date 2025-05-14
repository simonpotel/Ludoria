import pygame
from src.windows.screens.base_screen import BaseScreen
from src.windows.components.button import Button
from src.windows.components.dropdown import Dropdown
from src.utils.logger import Logger
from src.windows.selector.quadrant_handler import QuadrantHandler
from src.windows.selector.config_loader import ConfigLoader
from src.utils.theme_manager import ThemeManager
import os

class QuadrantConfigScreen(BaseScreen):
    """
    classe : écran de configuration des quadrants qui permet de sélectionner
    et configurer les quadrants pour chaque zone du plateau de jeu.
    """
    
    def __init__(self, parent_screen=None):
        """
        constructeur : initialise l'écran de configuration des quadrants.
        
        params:
            parent_screen - écran parent qui a appelé cet écran.
        """
        super().__init__(title="Ludoria - Quadrant Configuration")
        self.parent_screen = parent_screen
        self.quadrant_handler = QuadrantHandler()
        self.config_loader = ConfigLoader()
        self.theme_manager = ThemeManager()
        
        # récupération des configurations depuis l'écran parent
        if parent_screen:
            self.selected_quadrants = parent_screen.selected_quadrants
            self.quadrants_config = parent_screen.quadrants_config
            self.quadrant_names = parent_screen.quadrant_names
        else:
            self.selected_quadrants = [None] * 4
            self.quadrants_config = None
            self.quadrant_names = None
            
            # chargement depuis les fichiers si pas d'écran parent
            config_result = self.config_loader.load_quadrants()
            if config_result:
                self.quadrants_config, self.quadrant_names, _ = config_result
            else:
                Logger.error("QuadrantConfigScreen", "Failed to load quadrant configurations.")
        
        self.background_image = None
        try:
            # Utiliser le thème actuel pour charger l'image de fond
            current_theme = self.theme_manager.current_theme
            bg_path = os.path.join("assets", current_theme, "background.png")
            self.background_image = pygame.image.load(bg_path)
            self.background_image = pygame.transform.scale(self.background_image, (self.width, self.height))
            
            # Ajouter un effet semi-transparent pour améliorer la lisibilité
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))  # Overlay noir semi-transparent
            self.background_image.blit(overlay, (0, 0))
            
            Logger.info("QuadrantConfigScreen", f"Background image loaded: {bg_path}")
        except Exception as e:
            Logger.error("QuadrantConfigScreen", f"Failed to load background image: {e}")
        
        self.quadrant_selectors = []
        self.quadrant_rotation_buttons = []
        self.save_button = None
        self.back_button = None
        
        self.quadrant_display_rects = []
        self.labels = []
    
    def setup_ui(self):
        """
        procédure : configure l'interface utilisateur de l'écran de configuration des quadrants.
        """
        padding = 20
        left_panel_width = 280
        button_height = 40
        button_width = 200
        dropdown_height = 40
        dropdown_width = 180
        spacing = 20
        small_button_width = 40
        
        self.font = pygame.font.SysFont('Arial', 20)
        
        self._setup_quadrant_preview_rects()
        
        self.quadrant_selectors = []
        self.quadrant_rotation_buttons = []
        
        left_margin = padding
        top_margin = self.navbar_height + 80
        
        # création des contrôles pour chaque quadrant
        for i in range(4):
            self.labels.append((f"Quadrant {i+1}:", (left_margin, top_margin + i * (dropdown_height + spacing) * 2)))
            
            # dropdown pour sélectionner le type de quadrant
            selector = Dropdown(
                left_margin, top_margin + i * (dropdown_height + spacing) * 2 + 30, 
                dropdown_width, dropdown_height, 
                self.quadrant_names, 
                self._get_quadrant_index(i)
            )
            self.quadrant_selectors.append(selector)
            
            # boutons de rotation pour chaque quadrant
            left_button = Button(
                left_margin + dropdown_width + 10, top_margin + i * (dropdown_height + spacing) * 2 + 30, 
                small_button_width, dropdown_height, 
                "←", 
                lambda idx=i: self._rotate_left_handler(idx)
            )
            right_button = Button(
                left_margin + dropdown_width + small_button_width + 15, top_margin + i * (dropdown_height + spacing) * 2 + 30, 
                small_button_width, dropdown_height, 
                "→", 
                lambda idx=i: self._rotate_right_handler(idx)
            )
            self.quadrant_rotation_buttons.append((left_button, right_button))
        
        # boutons de navigation en bas de l'écran
        button_y = self.height - padding - button_height * 2 - spacing
        
        self.save_button = Button(
            left_margin, button_y, button_width, button_height,
            "Enregistrer", self._save_action
        )
        
        self.back_button = Button(
            left_margin, button_y + button_height + spacing, button_width, button_height,
            "Retour", self._back_action
        )
        
        self._update_selected_quadrants()
    
    def _setup_quadrant_preview_rects(self):
        """
        procédure : configure les rectangles pour l'affichage des quadrants.
        """
        left_panel_width = 300
        padding = 20
        
        available_width = self.width - left_panel_width - (padding * 2)
        available_height = self.height - self.navbar_height - 60
        
        # calcul de la taille optimale du plateau
        preview_size = min(available_width, available_height)
        
        preview_x = left_panel_width + ((available_width - preview_size) // 2) + padding
        preview_y = self.navbar_height + ((available_height - preview_size) // 2) + 30
        
        quadrant_size = preview_size // 2
        
        # définition des rectangles pour chacun des quatre quadrants
        self.quadrant_display_rects = [
            pygame.Rect(
                preview_x, 
                preview_y,
                quadrant_size, quadrant_size
            ),
            pygame.Rect(
                preview_x + quadrant_size, 
                preview_y,
                quadrant_size, quadrant_size
            ),
            pygame.Rect(
                preview_x, 
                preview_y + quadrant_size,
                quadrant_size, quadrant_size
            ),
            pygame.Rect(
                preview_x + quadrant_size, 
                preview_y + quadrant_size,
                quadrant_size, quadrant_size
            )
        ]
        
        # rectangle global contenant tous les quadrants
        self.preview_rect = pygame.Rect(
            preview_x, 
            preview_y, 
            preview_size, 
            preview_size
        )
    
    def _get_quadrant_index(self, quadrant_position):
        """
        fonction : retrouve l'index du quadrant dans la liste des noms de quadrants.
        
        params:
            quadrant_position - position du quadrant (0-3).
            
        retour : l'index dans la liste des noms de quadrants.
        """
        if not self.selected_quadrants[quadrant_position] or not self.quadrant_names:
            return 0
            
        for name in self.quadrant_names:
            if self.quadrants_config.get(name) == self.selected_quadrants[quadrant_position]:
                return self.quadrant_names.index(name)
        
        return 0
    
    def _update_selected_quadrants(self):
        """
        procédure : met à jour les quadrants sélectionnés en fonction des sélecteurs.
        """
        if not self.quadrant_selectors or not self.quadrants_config or not self.quadrant_names:
            return
            
        for i, selector in enumerate(self.quadrant_selectors):
            if 0 <= selector.selected_index < len(self.quadrant_names):
                quadrant_name = self.quadrant_names[selector.selected_index]
                self.selected_quadrants[i] = self.quadrants_config.get(quadrant_name)
    
    def _rotate_left_handler(self, index):
        """
        procédure : rotation du quadrant vers la gauche.
        
        params:
            index - index du quadrant à pivoter.
        """
        self.selected_quadrants = self.quadrant_handler.rotate_left(self.selected_quadrants, index)
    
    def _rotate_right_handler(self, index):
        """
        procédure : rotation du quadrant vers la droite.
        
        params:
            index - index du quadrant à pivoter.
        """
        self.selected_quadrants = self.quadrant_handler.rotate_right(self.selected_quadrants, index)
    
    def _back_action(self):
        """
        procédure : action du bouton Retour - revient à l'écran parent sans sauvegarder.
        """
        if self.parent_screen:
            self.next_screen = lambda: self.parent_screen
        else:
            from src.windows.screens.game_config.game_config import GameConfigScreen
            self.next_screen = GameConfigScreen
        
        self.running = False
    
    def _save_action(self):
        """
        procédure : action du bouton Enregistrer - sauvegarde les quadrants et revient à l'écran parent.
        """
        self._update_selected_quadrants()
        
        # transmission des quadrants configurés à l'écran parent
        if self.parent_screen:
            self.parent_screen.selected_quadrants = self.selected_quadrants
            self.next_screen = lambda: self.parent_screen
        else:
            from src.windows.screens.game_config.game_config import GameConfigScreen
            self.next_screen = GameConfigScreen
        
        Logger.info("QuadrantConfigScreen", "Quadrants configuration saved")
        self.running = False
    
    def handle_screen_events(self, event):
        """
        procédure : gère les événements spécifiques à cet écran.
        
        params:
            event - événement pygame à traiter.
        """
        # gestion de la fermeture des dropdowns ouverts
        clicked_dropdown = None
        for i, selector in enumerate(self.quadrant_selectors):
            if selector.rect.collidepoint(pygame.mouse.get_pos()) and event.type == pygame.MOUSEBUTTONDOWN:
                clicked_dropdown = i
        
        if clicked_dropdown is not None:
            for i, selector in enumerate(self.quadrant_selectors):
                if i != clicked_dropdown and selector.is_open:
                    selector.is_open = False
        
        # traitement des événements pour les sélecteurs
        for i, selector in enumerate(self.quadrant_selectors):
            if selector.handle_event(event, pygame.mouse.get_pos()):
                if not selector.is_open:
                    self._update_selected_quadrants()
        
        # traitement des événements pour les boutons de rotation
        for left_btn, right_btn in self.quadrant_rotation_buttons:
            left_btn.handle_event(event)
            right_btn.handle_event(event)
        
        self.back_button.handle_event(event)
        self.save_button.handle_event(event)
    
    def update_screen(self, mouse_pos):
        """
        procédure : met à jour l'état des éléments de l'écran.
        
        params:
            mouse_pos - position actuelle de la souris.
        """
        for left_btn, right_btn in self.quadrant_rotation_buttons:
            left_btn.check_hover(mouse_pos)
            right_btn.check_hover(mouse_pos)
        
        self.back_button.check_hover(mouse_pos)
        self.save_button.check_hover(mouse_pos)
    
    def draw_screen(self):
        """
        procédure : dessine les éléments de l'écran.
        """
        if self.background_image:
            self.screen.blit(self.background_image, (0, 0))
        else:
            self.screen.fill((240, 240, 240))
        
        # panneau de contrôle semi-transparent
        left_panel_width = 300
        panel_surface = pygame.Surface((left_panel_width, self.height), pygame.SRCALPHA)
        panel_surface.fill((240, 240, 240, 200))
        self.screen.blit(panel_surface, (0, 0))
        
        for text, pos in self.labels:
            text_surface = self.font.render(text, True, (0, 0, 0))
            self.screen.blit(text_surface, pos)
        
        # zone de prévisualisation semi-transparente
        preview_bg = pygame.Surface((self.preview_rect.width, self.preview_rect.height), pygame.SRCALPHA)
        preview_bg.fill((255, 255, 255, 150))
        self.screen.blit(preview_bg, self.preview_rect)
        
        preview_label = self.font.render("Preview:", True, (0, 0, 0))
        self.screen.blit(preview_label, (self.preview_rect.left, self.preview_rect.top - 25))
        
        # dessin des quadrants si tous sont définis
        if all(self.selected_quadrants):
            self.quadrant_handler.draw_quadrants(
                self.screen, 
                self.selected_quadrants, 
                self.preview_rect
            )
        
        # dessin des contrôles d'interface
        for selector in self.quadrant_selectors:
            selector.draw(self.screen)
        
        for left_btn, right_btn in self.quadrant_rotation_buttons:
            left_btn.draw(self.screen)
            right_btn.draw(self.screen)
        
        self.back_button.draw(self.screen)
        self.save_button.draw(self.screen) 