import pygame
from functools import partial

from src.utils.logger import Logger
from src.windows.components import Button, Dropdown, TextInput
from src.windows.selector.quadrant_config import QuadrantConfigScreen


class SoloConfigScreen:
    """
    Classe : interface graphique pour la configuration du mode Solo.
    Permet à l'utilisateur de configurer les paramètres de jeu pour le mode Solo
    et visualiser le plateau de jeu avant de lancer la partie.
    """
    
    def __init__(self, selector):
        """
        Constructeur : initialise l'écran de configuration Solo.
        
        Params:
            selector (Selector): référence à l'instance de la classe Selector principale
        """
        self.selector = selector 
        self.quadrant_handler = selector.quadrant_handler
        self.game_launcher = selector.game_launcher
        self.quadrants_config = selector.quadrants_config
        self.quadrant_names = selector.quadrant_names
        self.games = selector.GAMES
        
        # Interface graphique
        self.width = selector.width
        self.height = selector.height
        self.screen = selector.screen
        self.clock = selector.clock
        
        # Fond d'écran
        self.background = selector.background
        
        # Paramètres de mise en page
        self.rect_width = 320
        self.rect_height = 130
        self.rect_margin = 20
        self.rect_color = (0, 0, 0, 180)  # Noir avec transparence
        
        # Paramètres pour la prévisualisation du plateau
        self.preview_size = 500  
        self.preview_x = self.width - self.preview_size - 100
        self.preview_y = 80
        
        # Police et styles
        self.font = pygame.font.SysFont('Arial', 16)
        self.title_font = pygame.font.SysFont('Arial', 24, bold=True)
        self.header_font = pygame.font.SysFont('Arial', 20, bold=True)
        
        # Rectangles pour les sections
        self.game_select_rect = pygame.Rect(
            50,
            50,
            self.rect_width,
            self.rect_height
        )
        
        self.quadrant_rect = pygame.Rect(
            50,
            50 + self.rect_height + self.rect_margin,
            self.rect_width,
            self.rect_height
        )
        
        self.game_name_rect = pygame.Rect(
            50,
            50 + 2 * (self.rect_height + self.rect_margin),
            self.rect_width,
            self.rect_height
        )
        
        self.start_rect = pygame.Rect(
            50,
            50 + 3 * (self.rect_height + self.rect_margin),
            self.rect_width,
            self.rect_height
        )
        
        # Éléments UI
        self.game_name_input = None
        self.game_selection = None
        self.quadrant_button = None
        self.start_button = None
        self.back_button = None
        
        # Pour la configuration des quadrants
        self.quadrant_selectors = []
        self.quadrant_rotation_buttons = []
        
        # État
        self.selected_quadrants = [None] * 4
        self.show_quadrant_config = False
    
    def show(self):
        """
        Procédure : affiche l'écran de configuration Solo et gère l'interaction utilisateur.
        Retourne uniquement lorsque l'utilisateur quitte l'écran ou lance une partie.
        """
        show_config = True
        
        # Initialisation des composants de l'interface
        self.init_components()
        self.init_quadrant_selectors()
        self.update_selected_quadrants()
        
        # Boucle principale de l'écran de configuration
        while show_config and self.selector.outer_running:
            dt = self.clock.tick(30) / 1000.0
            mouse_pos = pygame.mouse.get_pos()
            
            # Gestion des événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    show_config = False
                    self.selector.outer_running = False
                
                self.handle_events(event, mouse_pos)
            
            # Mise à jour des états
            self.update(dt)
            
            # Rendu de l'interface
            self.draw()
            pygame.display.flip()
    
    def init_components(self):
        """
        Procédure : initialise tous les éléments de l'interface utilisateur.
        """
        # Menu déroulant pour le choix du jeu
        dropdown_width = self.rect_width - 40
        dropdown_height = 30
        
        self.game_selection = Dropdown(
            self.game_select_rect.left + 20,
            self.game_select_rect.top + 70,
            dropdown_width,
            dropdown_height,
            self.games,
            0
        )
        
        # Bouton pour configurer les quadrants
        self.quadrant_button = Button(
            self.quadrant_rect.left + 20,
            self.quadrant_rect.top + 70,
            dropdown_width,
            dropdown_height,
            "Configurer les quadrants",
            self.open_quadrant_config_page
        )
        
        # Champ de texte pour le nom de la partie
        self.game_name_input = TextInput(
            self.game_name_rect.left + 20,
            self.game_name_rect.top + 70,
            dropdown_width,
            dropdown_height
        )
        
        # Bouton de lancement
        self.start_button = Button(
            self.start_rect.left + 20,
            self.start_rect.top + 70,
            dropdown_width,
            dropdown_height,
            "Démarrer la partie",
            self.start_game_action
        )
        
        # Bouton de retour (flèche)
        self.back_button = Button(
            self.width - 60,  # Position X à droite
            15,
            40,
            40,
            "←",
            self.back_action
        )
    
    def init_quadrant_selectors(self):
        """
        Procédure : initialise les sélecteurs de quadrants et les boutons de rotation.
        Cette fonction est maintenue pour la compatibilité avec le code existant,
        mais les sélecteurs ne seront pas affichés dans cette interface.
        """
        self.quadrant_selectors = []
        self.quadrant_rotation_buttons = []
        
        element_width = self.rect_width - 40
        button_width = 30
        selector_width = element_width - 2 * button_width - 10
        
        for i in range(4):
            # Sélecteur de quadrant
            selector = Dropdown(
                self.preview_x - 300,
                self.preview_y + i * 40,
                selector_width,
                30,
                self.quadrant_names,
                i % len(self.quadrant_names)
            )
            self.quadrant_selectors.append(selector)
            
            # Boutons de rotation
            left_button = Button(
                self.preview_x - 300 + selector_width + 5,
                self.preview_y + i * 40,
                button_width,
                30,
                "←",
                partial(self.rotate_left_handler, i)
            )
            right_button = Button(
                self.preview_x - 300 + selector_width + 10 + button_width,
                self.preview_y + i * 40,
                button_width,
                30,
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
        
        # Gestion du bouton de retour
        if self.back_button.handle_event(event):
            handled = True
        
        # Gestion du champ de texte
        if not handled and self.game_name_input.handle_event(event, mouse_pos):
            handled = True
        
        # Gestion du sélecteur de jeu
        if not handled and self.game_selection.handle_event(event, mouse_pos):
            handled = True
        
        # Gestion du bouton de configuration de quadrants
        if not handled:
            if self.quadrant_button.handle_event(event):
                handled = True
        
        # Gestion du bouton de lancement
        if not handled:
            self.start_button.handle_event(event)
    
    def update(self, dt):
        """
        Procédure : met à jour les états des composants de l'interface.
        
        Params:
            dt (float): temps écoulé depuis la dernière mise à jour en secondes
        """
        mouse_pos = pygame.mouse.get_pos()
        
        # Vérification des survols
        self.back_button.check_hover(mouse_pos)
        self.quadrant_button.check_hover(mouse_pos)
        self.start_button.check_hover(mouse_pos)
        
        # Mise à jour du champ de texte
        self.game_name_input.update(dt * 1000)
    
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
        title_text = self.title_font.render("Configuration Mode Solo", True, (0, 0, 0))
        title_rect = title_text.get_rect(center=(self.width // 2, 20))
        self.screen.blit(title_text, title_rect)
        
        # Affichage des rectangles semi-transparents
        self.draw_section(self.game_select_rect, "SELECT GAME")
        self.draw_section(self.quadrant_rect, "CHANGE QUADRANT")
        self.draw_section(self.game_name_rect, "GAME NAME")
        self.draw_section(self.start_rect, "")  # Rectangle pour le bouton start sans titre
        
        # Zone de prévisualisation
        preview_rect = pygame.Rect(self.preview_x, self.preview_y, self.preview_size, self.preview_size)
        preview_label = self.header_font.render("Prévisualisation", True, (0, 0, 255))
        self.screen.blit(preview_label, (preview_rect.left, self.preview_y - 30))
        
        # Composants
        self.game_selection.draw(self.screen)
        self.quadrant_button.draw(self.screen)
        self.game_name_input.draw(self.screen)
        self.start_button.draw(self.screen)
        self.back_button.draw(self.screen)
        
        # Prévisualisation du plateau de jeu
        self.quadrant_handler.draw_quadrants(
            self.screen, 
            self.selected_quadrants, 
            preview_rect
        )
    
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
            title_rect = title_text.get_rect(midtop=(rect.width // 2, 20))
            self.screen.blit(title_text, (rect.left + title_rect.left, rect.top + title_rect.top))
    
    def back_action(self):
        """
        Procédure : action du bouton retour (flèche).
        Quitte l'écran de configuration pour revenir à l'écran d'accueil.
        """
        Logger.info("SoloConfig", "Retour à l'écran d'accueil")
        self.selector.welcome_screen()  # Retour à l'écran d'accueil
        self.selector.running = False   # Termine la boucle de l'écran de configuration
    
    def open_quadrant_config_page(self):
        """
        Procédure : ouvre une nouvelle page pour la configuration des quadrants.
        """
        Logger.info("SoloConfig", "Ouverture de la page de configuration des quadrants")
        
        # Crée et affiche la page de configuration des quadrants
        quadrant_config = QuadrantConfigScreen(self.selector, self.selected_quadrants)
        updated_quadrants = quadrant_config.show()
        
        # Met à jour les quadrants si la configuration a été confirmée
        if updated_quadrants:
            self.selected_quadrants = updated_quadrants
            Logger.info("SoloConfig", "Configuration des quadrants mise à jour")
    
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
    
    def start_game_action(self):
        """
        Procédure : lance le jeu avec la configuration actuelle.
        Vérifie d'abord la validité des paramètres.
        """
        game_save = self.game_name_input.get().strip()
        selected_game = self.games[self.game_selection.selected_index]
        
        if not game_save:
            Logger.warning("SoloConfig", "Nom de sauvegarde invalide.")
            return
            
        Logger.info("SoloConfig", f"Starting solo game: {selected_game}, name: {game_save}")
        
        # Mise à jour des sélections dans la classe principale
        self.selector.entry_game_save = TextInput(0, 0, 1, 1, initial_text=game_save)  # Crée un TextInput temporaire
        self.selector.game_selection = self.game_selection
        if self.selector.mode_selection:
            self.selector.mode_selection.selected_index = 0  # Mode Solo
        
        # Mise à jour des quadrants
        self.selector.selected_quadrants = self.selected_quadrants
        
        # Lancement du jeu
        self.game_launcher.start_game(game_save, selected_game, "Solo", self.selected_quadrants)
        
        # Signal à la boucle principale que cette interface est terminée
        self.selector.running = False