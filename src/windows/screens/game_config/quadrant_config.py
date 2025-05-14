import pygame
from src.windows.screens.base_screen import BaseScreen
from src.windows.components.button import Button
from src.windows.components.dropdown import Dropdown
from src.utils.logger import Logger
from src.windows.selector.quadrant_handler import QuadrantHandler
from src.windows.selector.config_loader import ConfigLoader

class QuadrantConfigScreen(BaseScreen):
    """
    Écran de configuration des quadrants qui permet de sélectionner
    et configurer les quadrants pour chaque zone du plateau de jeu.
    """
    
    def __init__(self, parent_screen=None):
        super().__init__(title="Ludoria - Quadrant Configuration")
        self.parent_screen = parent_screen
        self.quadrant_handler = QuadrantHandler()
        self.config_loader = ConfigLoader()
        
        # Récupération des quadrants depuis le parent si disponible
        if parent_screen:
            self.selected_quadrants = parent_screen.selected_quadrants
            self.quadrants_config = parent_screen.quadrants_config
            self.quadrant_names = parent_screen.quadrant_names
        else:
            self.selected_quadrants = [None] * 4
            self.quadrants_config = None
            self.quadrant_names = None
            
            # Chargement des configurations depuis les fichiers
            config_result = self.config_loader.load_quadrants()
            if config_result:
                self.quadrants_config, self.quadrant_names, _ = config_result
            else:
                Logger.error("QuadrantConfigScreen", "Failed to load quadrant configurations.")
        
        # Interface elements
        self.quadrant_selectors = []
        self.quadrant_rotation_buttons = []
        self.save_button = None
        self.back_button = None
        
        # Variables de disposition
        self.quadrant_display_rects = []
        self.labels = []
    
    def setup_ui(self):
        """Configure l'interface utilisateur de l'écran de configuration des quadrants."""
        # Dimensions et positionnement
        padding = 20
        left_panel_width = 280
        button_height = 40
        button_width = 200
        dropdown_height = 40
        dropdown_width = 180
        spacing = 20
        small_button_width = 40
        
        # Police et titre
        title_font = pygame.font.SysFont('Arial', 28, bold=True)
        self.title_text = title_font.render("Configuration des Quadrants", True, (0, 0, 0))
        self.title_rect = self.title_text.get_rect(midtop=(self.width // 2, self.navbar_height + 20))
        
        # Configurer le titre de la section
        self.font = pygame.font.SysFont('Arial', 20)
        
        # Créer les rectangles de prévisualisation des quadrants
        self._setup_quadrant_preview_rects()
        
        # Sélecteurs de quadrants et boutons de rotation
        self.quadrant_selectors = []
        self.quadrant_rotation_buttons = []
        
        # Position initiale pour les contrôles
        left_margin = padding
        top_margin = self.navbar_height + 80
        
        # Configurer un sélecteur et des boutons de rotation pour chaque quadrant
        for i in range(4):
            # Label du quadrant
            self.labels.append((f"Quadrant {i+1}:", (left_margin, top_margin + i * (dropdown_height + spacing) * 2)))
            
            # Sélecteur de quadrant (dropdown)
            selector = Dropdown(
                left_margin, top_margin + i * (dropdown_height + spacing) * 2 + 30, 
                dropdown_width, dropdown_height, 
                self.quadrant_names, 
                self._get_quadrant_index(i)
            )
            self.quadrant_selectors.append(selector)
            
            # Boutons de rotation (à droite du dropdown)
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
        
        # Boutons de navigation (l'un au-dessus de l'autre à gauche)
        button_y = self.height - padding - button_height * 2 - spacing
        
        self.save_button = Button(
            left_margin, button_y, button_width, button_height,
            "Enregistrer", self._save_action
        )
        
        self.back_button = Button(
            left_margin, button_y + button_height + spacing, button_width, button_height,
            "Retour", self._back_action
        )
        
        # Mettre à jour les quadrants sélectionnés
        self._update_selected_quadrants()
    
    def _setup_quadrant_preview_rects(self):
        """Configure les rectangles pour l'affichage des quadrants."""
        # Zone centrale de l'écran pour le plateau
        left_panel_width = 300
        content_width = self.width - left_panel_width - 80
        content_height = self.height - self.navbar_height - 200
        
        # Taille d'un quadrant (carré)
        quadrant_size = min(content_width // 2, content_height // 2) - 20
        
        # Position centrale 
        center_x = (self.width + left_panel_width) // 2
        center_y = self.navbar_height + 80 + content_height // 2
        
        # Liste des rectangles pour chaque quadrant
        self.quadrant_display_rects = [
            # Quadrant supérieur gauche (0)
            pygame.Rect(
                center_x - quadrant_size - 10, 
                center_y - quadrant_size - 10,
                quadrant_size, quadrant_size
            ),
            # Quadrant supérieur droit (1)
            pygame.Rect(
                center_x + 10, 
                center_y - quadrant_size - 10,
                quadrant_size, quadrant_size
            ),
            # Quadrant inférieur gauche (2)
            pygame.Rect(
                center_x - quadrant_size - 10, 
                center_y + 10,
                quadrant_size, quadrant_size
            ),
            # Quadrant inférieur droit (3)
            pygame.Rect(
                center_x + 10, 
                center_y + 10,
                quadrant_size, quadrant_size
            )
        ]
    
    def _get_quadrant_index(self, quadrant_position):
        """Retrouve l'index du quadrant dans la liste des noms de quadrants."""
        if not self.selected_quadrants[quadrant_position] or not self.quadrant_names:
            return 0
            
        # Recherche le nom du quadrant
        for name in self.quadrant_names:
            if self.quadrants_config.get(name) == self.selected_quadrants[quadrant_position]:
                return self.quadrant_names.index(name)
        
        return 0
    
    def _update_selected_quadrants(self):
        """Met à jour les quadrants sélectionnés en fonction des sélecteurs."""
        if not self.quadrant_selectors or not self.quadrants_config or not self.quadrant_names:
            return
            
        for i, selector in enumerate(self.quadrant_selectors):
            if 0 <= selector.selected_index < len(self.quadrant_names):
                quadrant_name = self.quadrant_names[selector.selected_index]
                self.selected_quadrants[i] = self.quadrants_config.get(quadrant_name)
    
    def _rotate_left_handler(self, index):
        """Rotation du quadrant vers la gauche."""
        self.selected_quadrants = self.quadrant_handler.rotate_left(self.selected_quadrants, index)
    
    def _rotate_right_handler(self, index):
        """Rotation du quadrant vers la droite."""
        self.selected_quadrants = self.quadrant_handler.rotate_right(self.selected_quadrants, index)
    
    def _back_action(self):
        """Action du bouton Retour - revient à l'écran parent sans sauvegarder."""
        if self.parent_screen:
            self.next_screen = lambda: self.parent_screen
        else:
            from src.windows.screens.game_config.game_config import GameConfigScreen
            self.next_screen = GameConfigScreen
        
        self.running = False
    
    def _save_action(self):
        """Action du bouton Enregistrer - sauvegarde les quadrants et revient à l'écran parent."""
        self._update_selected_quadrants()
        
        if self.parent_screen:
            # Mise à jour des quadrants dans l'écran parent
            self.parent_screen.selected_quadrants = self.selected_quadrants
            self.next_screen = lambda: self.parent_screen
        else:
            from src.windows.screens.game_config.game_config import GameConfigScreen
            self.next_screen = GameConfigScreen
        
        Logger.info("QuadrantConfigScreen", "Quadrants configuration saved")
        self.running = False
    
    def handle_screen_events(self, event):
        """Gère les événements spécifiques à cet écran."""
        # Fermer tous les autres dropdowns avant de gérer un nouveau dropdown
        clicked_dropdown = None
        for i, selector in enumerate(self.quadrant_selectors):
            if selector.rect.collidepoint(pygame.mouse.get_pos()) and event.type == pygame.MOUSEBUTTONDOWN:
                clicked_dropdown = i
        
        # Si un dropdown a été cliqué, fermez tous les autres
        if clicked_dropdown is not None:
            for i, selector in enumerate(self.quadrant_selectors):
                if i != clicked_dropdown and selector.is_open:
                    selector.is_open = False
        
        # Gérer les événements normalement
        for i, selector in enumerate(self.quadrant_selectors):
            if selector.handle_event(event, pygame.mouse.get_pos()):
                if not selector.is_open:
                    self._update_selected_quadrants()
        
        for left_btn, right_btn in self.quadrant_rotation_buttons:
            left_btn.handle_event(event)
            right_btn.handle_event(event)
        
        self.back_button.handle_event(event)
        self.save_button.handle_event(event)
    
    def update_screen(self, mouse_pos):
        """Met à jour l'état des éléments de l'écran."""
        for left_btn, right_btn in self.quadrant_rotation_buttons:
            left_btn.check_hover(mouse_pos)
            right_btn.check_hover(mouse_pos)
        
        self.back_button.check_hover(mouse_pos)
        self.save_button.check_hover(mouse_pos)
    
    def draw_screen(self):
        """Dessine les éléments de l'écran."""
        # Dessine le titre
        self.screen.blit(self.title_text, self.title_rect)
        
        # Dessine les labels pour les quadrants
        for text, pos in self.labels:
            text_surface = self.font.render(text, True, (0, 0, 0))
            self.screen.blit(text_surface, pos)
        
        # Dessine les prévisualisations des quadrants
        if all(self.selected_quadrants):
            self.quadrant_handler.draw_quadrants(
                self.screen, 
                self.selected_quadrants, 
                pygame.Rect(
                    self.quadrant_display_rects[0].left,
                    self.quadrant_display_rects[0].top,
                    self.quadrant_display_rects[1].right - self.quadrant_display_rects[0].left,
                    self.quadrant_display_rects[3].bottom - self.quadrant_display_rects[0].top
                )
            )
        else:
            # Dessine des cadres vides si aucun quadrant n'est sélectionné
            for rect in self.quadrant_display_rects:
                pygame.draw.rect(self.screen, (200, 200, 200), rect, 2)
        
        # Dessine les sélecteurs
        for selector in self.quadrant_selectors:
            selector.draw(self.screen)
        
        # Dessine les boutons de rotation
        for left_btn, right_btn in self.quadrant_rotation_buttons:
            left_btn.draw(self.screen)
            right_btn.draw(self.screen)
        
        # Dessine les boutons de navigation
        self.back_button.draw(self.screen)
        self.save_button.draw(self.screen) 