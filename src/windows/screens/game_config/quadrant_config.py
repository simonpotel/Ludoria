import pygame
from src.windows.screens.base_screen import BaseScreen
from src.windows.components.button import Button
from src.windows.components.dropdown import Dropdown
from src.windows.components.image_button import ImageButton
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
            # utiliser le thème actuel pour charger l'image de fond
            current_theme = self.theme_manager.current_theme
            bg_path = os.path.join("assets", current_theme, "background.png")
            self.background_image = pygame.image.load(bg_path)
            Logger.info("QuadrantConfigScreen", f"Background image loaded: {bg_path}")
        except Exception as e:
            Logger.error("QuadrantConfigScreen", f"Failed to load background image: {e}")
        
        self.quadrant_selectors = []
        self.quadrant_rotation_buttons = []
        self.save_button = None
        self.back_button = None
        
        self.quadrant_display_rects = []
        self.labels = []
        self.previous_indices = [0, 0, 0, 0]
        
        self.quadrants_initialized = [False, False, False, False]
    
    def setup_ui(self):
        """
        procédure : configure l'interface utilisateur de l'écran de configuration des quadrants.
        """
        try:
            self.title_font = pygame.font.SysFont('Arial', 48, bold=True)
            self.label_font = pygame.font.SysFont('Arial', 20, bold=True)
            self.button_font = pygame.font.SysFont('Arial', 24, bold=True)
        except Exception as e:
            Logger.error("QuadrantConfigScreen", f"Font loading error: {str(e)}")
            self.title_font = pygame.font.Font(None, 48)
            self.label_font = pygame.font.Font(None, 20)
            self.button_font = pygame.font.Font(None, 24)
        
        if self.background_image:
            self.background_image = pygame.transform.scale(self.background_image, (self.width, self.height))
            
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            self.background_image.blit(overlay, (0, 0))
        
        padding = 30
        right_panel_width = int(self.width * 0.4)
        left_panel_width = self.width - right_panel_width - (padding * 3)
        
        preview_margin_top = self.navbar_height + 80
        self._setup_quadrant_preview_rects(left_panel_width, preview_margin_top)
        
        button_img_path = 'assets/Basic_GUI_Bundle/ButtonsText/ButtonText_Large_GreyOutline_Square.png'
        button_width = 200
        button_height = 70
        button_spacing = 20
        buttons_y = self.preview_rect.bottom + 30
        
        self.back_button = ImageButton(
            self.preview_rect.left,
            buttons_y,
            button_width,
            button_height,
            "BACK",
            self._back_action,
            bg_image_path=button_img_path,
            font=self.button_font,
            text_color=(255, 255, 255)
        )
        
        self.save_button = ImageButton(
            self.preview_rect.left + button_width + button_spacing,
            buttons_y,
            button_width,
            button_height,
            "SAVE",
            self._save_action,
            bg_image_path=button_img_path,
            font=self.button_font,
            text_color=(255, 255, 255)
        )
        
        right_panel_x = self.width - right_panel_width - padding
        right_panel_y = self.navbar_height + 80
        
        dropdown_width = int(right_panel_width * 0.7)
        dropdown_height = 40
        small_button_width = 40
        small_button_height = 40
        spacing = 30
        
        self.quadrant_selectors = []
        self.quadrant_rotation_buttons = []
        self.labels = []
        
        # création des contrôles pour chaque quadrant
        for i in range(4):
            label_y = right_panel_y + i * (dropdown_height + spacing) * 2
            self.labels.append((f"Quadrant {i+1}:", (right_panel_x, label_y)))
            
            # dropdown pour sélectionner le type de quadrant
            selector = Dropdown(
                right_panel_x, 
                label_y + 30, 
                dropdown_width, 
                dropdown_height, 
                self.quadrant_names, 
                self._get_quadrant_index(i),
                callback=lambda idx=i: self._on_dropdown_change(idx)
            )
            self.quadrant_selectors.append(selector)
            
            # boutons de rotation pour chaque quadrant
            left_button = ImageRotationButton(
                right_panel_x + dropdown_width + 10, 
                label_y + 30, 
                small_button_width, 
                small_button_height, 
                "assets/undo-alt (1).png", 
                lambda idx=i: self._rotate_left_handler(idx)
            )
            right_button = ImageRotationButton(
                right_panel_x + dropdown_width + small_button_width + 15, 
                label_y + 30, 
                small_button_width, 
                small_button_height, 
                "assets/redo-alt (2).png", 
                lambda idx=i: self._rotate_right_handler(idx)
            )
            self.quadrant_rotation_buttons.append((left_button, right_button))
        
        self._update_selected_quadrants()
    
    def _setup_quadrant_preview_rects(self, panel_width, top_margin):
        """
        procédure : configure les rectangles pour l'affichage des quadrants.
        
        params:
            panel_width - largeur du panneau de prévisualisation
            top_margin - marge supérieure pour le panneau
        """
        padding = 30
        
        preview_size = min(panel_width, self.height - top_margin - 100)
        
        preview_x = padding
        preview_y = top_margin
        
        quadrant_size = preview_size // 2
        
        self.preview_rect = pygame.Rect(
            preview_x, 
            preview_y, 
            preview_size, 
            preview_size
        )
        
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
                if self.selected_quadrants[i] is None:
                    self.selected_quadrants[i] = self.quadrants_config.get(quadrant_name)
    
    def _rotate_left_handler(self, index):
        """
        procédure : rotation du quadrant vers la gauche.
        
        params:
            index - index du quadrant à pivoter.
        """
        self.selected_quadrants = self.quadrant_handler.rotate_left(self.selected_quadrants, index)
        Logger.info("QuadrantConfigScreen", f"Rotated quadrant {index+1} left")
        
        self._sync_quadrant_with_dropdown(index)
    
    def _rotate_right_handler(self, index):
        """
        procédure : rotation du quadrant vers la droite.
        
        params:
            index - index du quadrant à pivoter.
        """
        self.selected_quadrants = self.quadrant_handler.rotate_right(self.selected_quadrants, index)
        Logger.info("QuadrantConfigScreen", f"Rotated quadrant {index+1} right")
        
        self._sync_quadrant_with_dropdown(index)
    
    def _sync_quadrant_with_dropdown(self, index):
        """
        procédure : synchronise le dropdown avec l'état actuel du quadrant après rotation.
        
        params:
            index - index du quadrant qui a été pivoté.
        """
        current_quadrant = self.selected_quadrants[index]
        if current_quadrant and self.quadrant_names:
            Logger.info("QuadrantConfigScreen", f"Quadrant {index+1} rotation saved")
    
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
        
        # transmission des quadrants configurés à l'écran parent
        if self.parent_screen:
            self.parent_screen.selected_quadrants = self.selected_quadrants
            self.next_screen = lambda: self.parent_screen
        else:
            from src.windows.screens.game_config.game_config import GameConfigScreen
            self.next_screen = GameConfigScreen
        
        Logger.info("QuadrantConfigScreen", "Quadrants configuration saved")
        self.running = False
    
    def _on_dropdown_change(self, quadrant_index):
        """
        procédure : appelée quand un dropdown change de valeur
        
        params:
            quadrant_index - index du quadrant (0-3) dont le dropdown a changé
        """
        Logger.info("QuadrantConfigScreen", f"Dropdown changed for quadrant {quadrant_index+1}")
        selector = self.quadrant_selectors[quadrant_index]
        
        if 0 <= selector.selected_index < len(self.quadrant_names):
            quadrant_name = self.quadrant_names[selector.selected_index]
            self.selected_quadrants[quadrant_index] = self.quadrants_config.get(quadrant_name)
            Logger.info("QuadrantConfigScreen", f"Selected {quadrant_name} for quadrant {quadrant_index+1}")
    
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
        
        for i, selector in enumerate(self.quadrant_selectors):
            if selector.selected_index != self.previous_indices[i]:
                # correctement le remplacement de quadrant
                self._on_dropdown_change(i)
                
        self.previous_indices = [selector.selected_index for selector in self.quadrant_selectors]
    
    def draw_rounded_rect(self, surface, rect, color, radius=15, alpha=255):
        """
        procédure : dessine un rectangle avec des coins arrondis et une transparence configurable
        
        params:
            surface - surface pygame sur laquelle dessiner
            rect - tuple (x, y, width, height) ou pygame.Rect définissant le rectangle
            color - tuple (r, g, b) définissant la couleur du rectangle
            radius - rayon des coins arrondis en pixels
            alpha - valeur de transparence (0-255)
        """
        rect = pygame.Rect(rect)
        
        panel_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        
        pygame.draw.rect(panel_surface, (*color, alpha), (0, 0, rect.width, rect.height), border_radius=radius)
        
        surface.blit(panel_surface, rect.topleft)
    
    def draw_screen(self):
        """
        procédure : dessine les éléments de l'écran.
        """
        if self.background_image:
            self.screen.blit(self.background_image, (0, 0))
        else:
            self.screen.fill((240, 240, 240))
        
        
        title_text = "QUADRANT CONFIGURATION"
        title_surface = self.title_font.render(title_text, True, (255, 255, 255))
        title_x = (self.width - title_surface.get_width()) // 2
        title_y = self.navbar_height + 20
        self.screen.blit(title_surface, (title_x, title_y))
        
        preview_bg = pygame.Surface((self.preview_rect.width, self.preview_rect.height), pygame.SRCALPHA)
        preview_bg.fill((255, 255, 255, 150))
        self.screen.blit(preview_bg, self.preview_rect)
        
        preview_label = self.label_font.render("Preview:", True, (255, 255, 255))
        self.screen.blit(preview_label, (self.preview_rect.left, self.preview_rect.top - 30))
        
        # dessin des quadrants si tous sont définis
        if all(self.selected_quadrants):
            self.quadrant_handler.draw_quadrants(
                self.screen, 
                self.selected_quadrants, 
                self.preview_rect
            )
        
        # dessin des boutons d'action
        self.back_button.draw(self.screen)
        self.save_button.draw(self.screen)
        
        for text, pos in self.labels:
            text_surface = self.label_font.render(text, True, (255, 255, 255))
            self.screen.blit(text_surface, pos)
        
        for selector in self.quadrant_selectors:
            selector.draw(self.screen)
        
        for left_btn, right_btn in self.quadrant_rotation_buttons:
            left_btn.draw(self.screen)
            right_btn.draw(self.screen)

class ImageRotationButton:
    """
    classe : bouton de rotation utilisant des images PNG
    """
    def __init__(self, x, y, width, height, image_path, action=None):
        """
        constructeur : initialise un bouton avec une image.
        
        params:
            x, y - position du bouton
            width, height - dimensions du bouton
            image_path - chemin vers l'image
            action - fonction à exécuter quand le bouton est cliqué
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.image_path = image_path
        self.action = action
        self.is_hover = False
        
        try:
            self.original_image = pygame.image.load(image_path)
            self.image = pygame.transform.scale(self.original_image, (width, height))
            
            
        except Exception as e:
            print(f"Erreur lors du chargement de l'image: {e}")
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (200, 200, 200), (0, 0, width, height), 1)
    
    def draw(self, surface):
        """
        procédure : dessine le bouton sur la surface donnée.
        
        params:
            surface - surface pygame sur laquelle dessiner
        """
        surface.blit(self.image, self.rect)
    
    def check_hover(self, pos):
        """
        procédure : vérifie si la souris est sur le bouton.
        """
        self.is_hover = self.rect.collidepoint(pos)
    
    def handle_event(self, event):
        """
        fonction : gère les événements pour le bouton.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hover and self.action:
                self.action()
                return True
        return False