import pygame
from functools import partial

from src.utils.logger import Logger
from src.windows.components import Button, Dropdown


class QuadrantConfigScreen:
    """
    Classe : interface graphique pour la configuration des quadrants.
    Permet à l'utilisateur de sélectionner et d'orienter les quadrants pour le plateau de jeu.
    """
    
    def __init__(self, selector, initial_quadrants=None):
        """
        Constructeur : initialise l'écran de configuration des quadrants.
        
        Params:
            selector (Selector): référence à l'instance de la classe Selector principale
            initial_quadrants (list): configuration initiale des quadrants (si disponible)
        """
        self.selector = selector 
        self.quadrant_handler = selector.quadrant_handler
        self.quadrants_config = selector.quadrants_config
        self.quadrant_names = selector.quadrant_names
        
        # Interface graphique
        self.width = selector.width
        self.height = selector.height
        self.screen = selector.screen
        self.clock = selector.clock
        
        # Fond d'écran
        self.background = selector.background
        
        # Paramètres de mise en page
        self.left_panel_width = 350
        self.rect_width = 320
        self.rect_height = 130
        self.rect_margin = 20
        self.rect_color = (0, 0, 0, 180)  # Noir avec transparence
        
        # Paramètres pour la prévisualisation du plateau
        self.preview_size = 550
        self.preview_x = self.left_panel_width + 100
        self.preview_y = 120
        
        # Police et styles
        self.font = pygame.font.SysFont('Arial', 16)
        self.title_font = pygame.font.SysFont('Arial', 24, bold=True)
        self.header_font = pygame.font.SysFont('Arial', 20, bold=True)
        
        # Rectangles pour les sections
        self.nav_rect = pygame.Rect(
            20,
            20,
            self.rect_width,
            80
        )
        
        self.quadrant_rects = []
        for i in range(4):
            self.quadrant_rects.append(pygame.Rect(
                20,
                120 + i * (self.rect_height + self.rect_margin),
                self.rect_width,
                self.rect_height
            ))
        
        # Éléments UI
        self.back_button = None
        self.confirm_button = None
        self.quadrant_selectors = []
        self.quadrant_rotation_buttons = []
        
        # État
        self.selected_quadrants = initial_quadrants if initial_quadrants else [None] * 4
        self.running = True
    
    def show(self):
        """
        Procédure : affiche l'écran de configuration des quadrants et gère l'interaction utilisateur.
        Retourne uniquement lorsque l'utilisateur quitte l'écran ou confirme les modifications.
        
        Retourne:
            list: la configuration des quadrants sélectionnés
        """
        # Initialisation des composants de l'interface
        self.init_components()
        self.update_selected_quadrants()
        
        # Boucle principale de l'écran de configuration
        while self.running and self.selector.outer_running:
            dt = self.clock.tick(30) / 1000.0
            mouse_pos = pygame.mouse.get_pos()
            
            # Gestion des événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.selector.outer_running = False
                
                self.handle_events(event, mouse_pos)
            
            # Mise à jour des états
            self.update()
            
            # Rendu de l'interface
            self.draw()
            pygame.display.flip()
        
        return self.selected_quadrants
    
    def init_components(self):
        """
        Procédure : initialise tous les éléments de l'interface utilisateur.
        """
        # Boutons de navigation
        button_width = 140
        button_height = 40
        button_spacing = 20
        
        self.back_button = Button(
            self.nav_rect.left + 10,
            self.nav_rect.top + (self.nav_rect.height - button_height) // 2,
            button_width,
            button_height,
            "Retour",
            self.back_action
        )
        
        self.confirm_button = Button(
            self.nav_rect.left + self.nav_rect.width - button_width - 10,
            self.nav_rect.top + (self.nav_rect.height - button_height) // 2,
            button_width,
            button_height,
            "Confirmer",
            self.confirm_action
        )
        
        # Initialisation des sélecteurs de quadrants
        self.init_quadrant_selectors()
    
    def init_quadrant_selectors(self):
        """
        Procédure : initialise les sélecteurs de quadrants et les boutons de rotation.
        """
        self.quadrant_selectors = []
        self.quadrant_rotation_buttons = []
        
        # Dimensions et espacement
        element_margin = 20
        selector_width = 160
        selector_height = 30
        button_width = 35
        button_height = 30
        
        for i in range(4):
            rect = self.quadrant_rects[i]
            
            # Sélecteur de quadrant
            selector = Dropdown(
                rect.left + element_margin,
                rect.top + rect.height - selector_height - element_margin,
                selector_width,
                selector_height,
                self.quadrant_names,
                i % len(self.quadrant_names)
            )
            self.quadrant_selectors.append(selector)
            
            # Boutons de rotation
            left_button = Button(
                rect.left + element_margin + selector_width + 10,
                rect.top + rect.height - button_height - element_margin,
                button_width,
                button_height,
                "←",
                partial(self.rotate_left_handler, i)
            )
            right_button = Button(
                rect.left + element_margin + selector_width + button_width + 20,
                rect.top + rect.height - button_height - element_margin,
                button_width,
                button_height,
                "→",
                partial(self.rotate_right_handler, i)
            )
            self.quadrant_rotation_buttons.append((left_button, right_button))
    
    def handle_events(self, event, mouse_pos):
        """
        Procédure : gère les événements pour tous les composants de l'interface.
        
        Params:
            event (pygame.event): l'événement à traiter
            mouse_pos (tuple): la position actuelle de la souris (x, y)
        """
        handled = False
        
        # Gestion des boutons
        if self.back_button.handle_event(event):
            handled = True
        if not handled and self.confirm_button.handle_event(event):
            handled = True
        
        # Gestion des sélecteurs de quadrants
        if not handled:
            for selector in self.quadrant_selectors:
                if selector.handle_event(event, mouse_pos):
                    if not selector.is_open:
                        self.update_selected_quadrants()
                    handled = True
                    break
        
        # Gestion des boutons de rotation
        if not handled:
            for left_btn, right_btn in self.quadrant_rotation_buttons:
                if left_btn.handle_event(event):
                    handled = True
                    break
                if right_btn.handle_event(event):
                    handled = True
                    break
    
    def update(self):
        """
        Procédure : met à jour les états des composants de l'interface.
        """
        mouse_pos = pygame.mouse.get_pos()
        
        # Vérification des survols
        self.back_button.check_hover(mouse_pos)
        self.confirm_button.check_hover(mouse_pos)
        
        for left_btn, right_btn in self.quadrant_rotation_buttons:
            left_btn.check_hover(mouse_pos)
            right_btn.check_hover(mouse_pos)
    
    def draw(self):
        """
        Procédure : dessine tous les éléments de l'interface.
        """
        # Affichage du fond d'écran
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill((230, 230, 230))  # Fond gris clair par défaut
        
        # Titre principal
        title_text = self.title_font.render("Configuration des Quadrants", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.width // 2, 20))
        self.screen.blit(title_text, title_rect)
        
        # Zone de prévisualisation
        preview_rect = pygame.Rect(self.preview_x, self.preview_y, self.preview_size, self.preview_size)
        preview_label = self.header_font.render("Prévisualisation", True, (255, 255, 255))
        self.screen.blit(preview_label, (preview_rect.left, self.preview_y - 30))
        
        # Dessiner les rectangles semi-transparents
        self.draw_section(self.nav_rect, "")
        for i, rect in enumerate(self.quadrant_rects):
            self.draw_section(rect, f"QUADRANT {i+1}")
        
        # Prévisualisation du plateau de jeu
        self.quadrant_handler.draw_quadrants(
            self.screen, 
            self.selected_quadrants, 
            preview_rect
        )
        
        # Composants
        self.back_button.draw(self.screen)
        self.confirm_button.draw(self.screen)
        
        # Dessiner les sélecteurs et boutons de rotation
        for i, selector in enumerate(self.quadrant_selectors):
            selector.draw(self.screen)
            
            left_btn, right_btn = self.quadrant_rotation_buttons[i]
            left_btn.draw(self.screen)
            right_btn.draw(self.screen)
    
    def draw_section(self, rect, title):
        """
        Procédure : dessine un rectangle semi-transparent avec un titre.
        
        Params:
            rect (pygame.Rect): le rectangle à dessiner
            title (str): le titre à afficher dans le rectangle
        """
        # Création d'une surface avec canal alpha pour la transparence
        s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        s.fill(self.rect_color)
        self.screen.blit(s, (rect.left, rect.top))
        
        # Affichage du titre
        if title:
            title_text = self.header_font.render(title, True, (255, 255, 255))
            title_rect = title_text.get_rect(midtop=(rect.width // 2, 10))
            self.screen.blit(title_text, (rect.left + title_rect.left, rect.top + title_rect.top))
    
    def update_selected_quadrants(self):
        """
        Procédure : met à jour la configuration des quadrants sélectionnés.
        """
        self.selected_quadrants = self.quadrant_handler.update_selected_quadrants(
            self.quadrant_selectors,
            self.selected_quadrants,
            self.quadrants_config,
            self.quadrant_names
        )
    
    def rotate_left_handler(self, index):
        """
        Procédure : gestionnaire de rotation à gauche d'un quadrant.
        
        Params:
            index (int): index du quadrant à pivoter
        """
        self.selected_quadrants = self.quadrant_handler.rotate_left(
            self.selected_quadrants, 
            index
        )
    
    def rotate_right_handler(self, index):
        """
        Procédure : gestionnaire de rotation à droite d'un quadrant.
        
        Params:
            index (int): index du quadrant à pivoter
        """
        self.selected_quadrants = self.quadrant_handler.rotate_right(
            self.selected_quadrants, 
            index
        )
    
    def back_action(self):
        """
        Procédure : action du bouton retour.
        Quitte la page sans sauvegarder les modifications.
        """
        Logger.info("QuadrantConfig", "Retour à la page précédente")
        self.running = False
    
    def confirm_action(self):
        """
        Procédure : action du bouton confirmer.
        Sauvegarde les modifications et quitte la page.
        """
        Logger.info("QuadrantConfig", "Configuration des quadrants confirmée")
        self.running = False 