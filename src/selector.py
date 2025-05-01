import pygame
import pygame.freetype
from pathlib import Path
import json
from src.katerenga.game import Game as Katerenga
from src.isolation.game import Game as Isolation
from src.congress.game import Game as Congress
from src.render import Render
from src.saves import load_game
from src.utils.logger import Logger


class Button:
    """
    classe : représente un bouton cliquable simple dans l'interface.
    """
    def __init__(self, x, y, width, height, text, action=None):
        """
        constructeur : initialise un bouton.

        params:
            x, y: coordonnées du coin supérieur gauche.
            width, height: dimensions du bouton.
            text: texte affiché sur le bouton.
            action: fonction à appeler lors du clic (callback).
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        # couleurs pour les états normal et survolé
        self.color = (200, 200, 200)
        self.hover_color = (160, 160, 160)
        self.text_color = (0, 0, 0)
        self.font = pygame.font.SysFont('Arial', 16)
        self.is_hover = False # true si la souris est sur le bouton
    
    def draw(self, surface):
        """
        procédure : dessine le bouton sur la surface donnée.
        change de couleur si la souris est dessus.

        params:
            surface: surface pygame sur laquelle dessiner.
        """
        color = self.hover_color if self.is_hover else self.color
        pygame.draw.rect(surface, color, self.rect) # fond
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 1) # bordure
        
        # dessine le texte centré
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    
    def check_hover(self, pos):
        """
        procédure : vérifie si la position donnée est sur le bouton.

        params:
            pos: tuple (x, y) de la position de la souris.
        """
        self.is_hover = self.rect.collidepoint(pos)
        
    def handle_event(self, event):
        """
        procédure : gère les événements pygame pour ce bouton.
        déclenche l'action si un clic gauche survient pendant le survol.

        params:
            event: événement pygame.

        retour:
            bool: True si l'action a été déclenchée, False sinon.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # clic gauche
            if self.is_hover and self.action:
                Logger.info("Button", f"Button '{self.text}' clicked, executing action.")
                self.action() # exécute l'action associée
                return True
        return False


class Dropdown:
    """
    classe : représente une liste déroulante pour sélectionner une option.
    """
    def __init__(self, x, y, width, height, options, default_index=0):
        """
        constructeur : initialise la liste déroulante.

        params:
            x, y: coordonnées du coin supérieur gauche.
            width, height: dimensions de la boîte principale.
            options: liste des chaînes de caractères à afficher.
            default_index: index de l'option sélectionnée par défaut.
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options
        self.selected_index = default_index
        self.font = pygame.font.SysFont('Arial', 16)
        self.color = (240, 240, 240) # couleur de fond
        self.text_color = (0, 0, 0)
        self.is_open = False # true si la liste des options est visible
        self.option_height = 30 # hauteur de chaque option dans la liste
        self.option_rects = [] # rectangles pour chaque option (pour la détection de clic)
        self.update_option_rects()
        
    def update_option_rects(self):
        """
        procédure : calcule les rectangles pour chaque option de la liste déroulante.
        appelée à l'initialisation et potentiellement si les options changent.
        """
        self.option_rects = []
        for i in range(len(self.options)):
            # positionne chaque option sous la boîte principale
            self.option_rects.append(
                pygame.Rect(self.rect.x, self.rect.y + self.rect.height + i * self.option_height, 
                           self.rect.width, self.option_height)
            )
    
    def draw(self, surface):
        """
        procédure : dessine la liste déroulante sur la surface donnée.

        params:
            surface: surface pygame sur laquelle dessiner.
        """
        # dessine la boîte principale
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 1) # bordure
        
        # dessine l'option actuellement sélectionnée
        if 0 <= self.selected_index < len(self.options):
            text = self.options[self.selected_index]
            text_surface = self.font.render(text, True, self.text_color)
            # aligne le texte à gauche avec une petite marge
            text_rect = text_surface.get_rect(midleft=(self.rect.left + 5, self.rect.centery))
            surface.blit(text_surface, text_rect)
        
        # dessine la flèche déroulante
        arrow_points = [
            (self.rect.right - 15, self.rect.centery - 5), # haut gauche
            (self.rect.right - 5, self.rect.centery - 5),  # haut droit
            (self.rect.right - 10, self.rect.centery + 5) # bas milieu
        ]
        pygame.draw.polygon(surface, (0, 0, 0), arrow_points)
        
        # dessine les options si la liste est ouverte
        if self.is_open:
            for i, option_rect in enumerate(self.option_rects):
                # couleur de fond légèrement différente pour les options
                pygame.draw.rect(surface, (230, 230, 230), option_rect)
                pygame.draw.rect(surface, (0, 0, 0), option_rect, 1) # bordure
                
                text = self.options[i]
                text_surface = self.font.render(text, True, self.text_color)
                text_rect = text_surface.get_rect(midleft=(option_rect.left + 5, option_rect.centery))
                surface.blit(text_surface, text_rect)
    
    def handle_event(self, event, pos):
        """
        procédure : gère les événements pygame pour la liste déroulante.
        ouvre/ferme la liste ou sélectionne une option au clic.

        params:
            event: événement pygame.
            pos: tuple (x, y) de la position de la souris.

        retour:
            bool: True si un clic a été géré par cet élément, False sinon.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # clic gauche
            # clic sur la boîte principale pour ouvrir/fermer
            if self.rect.collidepoint(pos):
                self.is_open = not self.is_open
                Logger.debug("Dropdown", f"Dropdown toggled. Is open: {self.is_open}")
                return True # clic géré
            # clic sur une option si la liste est ouverte
            elif self.is_open:
                for i, option_rect in enumerate(self.option_rects):
                    if option_rect.collidepoint(pos):
                        old_selection = self.get()
                        self.selected_index = i
                        self.is_open = False
                        new_selection = self.get()
                        Logger.info("Dropdown", f"Option selected: {new_selection} (Index: {i}). Previous: {old_selection}")
                        return True # clic géré
                # clic en dehors des options ferme la liste
                self.is_open = False
                # ne retourne pas true ici, car le clic n'était pas sur cet élément
        return False # clic non géré par cet élément
    
    def get(self):
        """
        fonction : retourne la valeur de l'option actuellement sélectionnée.

        retour:
            str | None: la chaîne de l'option sélectionnée, ou None si invalide.
        """
        if 0 <= self.selected_index < len(self.options):
            return self.options[self.selected_index]
        Logger.warning("Dropdown", f"Selected index {self.selected_index} is out of bounds for options.")
        return None


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
            bool: True si l'événement a été géré par ce champ, False sinon.
        """
        # clic pour activer/désactiver
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            was_active = self.active
            self.active = self.rect.collidepoint(pos)
            if self.active != was_active:
                 Logger.debug("TextInput", f"Text input active state changed to: {self.active}")
            return self.active # retourne true si le clic l'a activé
        
        # ignore les autres événements si pas actif
        if not self.active:
            return False
            
        # gestion de la saisie clavier
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
                Logger.debug("TextInput", f"Backspace pressed. Text: '{self.text}'")
            elif event.key == pygame.K_RETURN:
                self.active = False # désactive à l'appui sur entrée
                Logger.debug("TextInput", "Enter pressed. Deactivating text input.")
            elif event.unicode.isprintable():
                # ajoute le caractère si imprimable et si la largeur le permet (simple vérification)
                if self.font.size(self.text + event.unicode)[0] < self.rect.width - 15:
                     self.text += event.unicode
                     Logger.debug("TextInput", f"Character '{event.unicode}' added. Text: '{self.text}'")
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


class Selector:
    """
    classe : interface graphique principale pour sélectionner et configurer un jeu.
    permet de choisir le type de jeu, le mode, le nom de sauvegarde et la configuration des quadrants.
    """
    GAMES = ["katerenga", "isolation", "congress"] # jeux disponibles
    GAME_MODES = ["Solo", "Bot", "Network"] # modes de jeu disponibles

    def __init__(self):
        """
        constructeur : initialise pygame, charge les configurations et met en place l'interface.
        lance ensuite la boucle principale.
        """
        Logger.initialize() # s'assure que le logger est prêt
        Logger.info("Selector", "Initializing game selector interface")
        
        pygame.init()
        pygame.font.init() # initialise le module font explicitement
        
        self.width, self.height = 800, 600 # dimensions de la fenêtre
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Smart Games: Selector")
        
        self.clock = pygame.time.Clock()
        self.running = True # contrôle la boucle principale
        
        self.quadrants = self.load_quadrants() # charge les configurations de quadrants depuis json
        self.selected_quadrants = [] # état actuel des 4 quadrants (avec rotations)
        if self.quadrants: # vérifie si le chargement a réussi
            for i in range(4):
                # copie profonde pour permettre les rotations indépendantes
                default_index = i % len(self.quadrants)
                self.selected_quadrants.append([row[:] for row in self.quadrants[default_index]])
        else:
             # si le chargement échoue, on ne peut pas continuer
             Logger.critical("Selector", "Failed to load quadrants. Cannot initialize UI.")
             self.running = False
             return
        
        self.setup_ui() # crée les éléments de l'interface (boutons, dropdowns, etc.)
        
        if self.running:
             Logger.info("Selector", "Initialization complete. Starting main loop.")
             self.main_loop() # lance la boucle d'événements et de rendu
        
        Logger.info("Selector", "Selector shutdown.")

    def load_quadrants(self):
        """
        fonction : charge les différentes configurations de quadrants depuis un fichier JSON.
        
        retour:
            list | None: liste des configurations de quadrants (chaque quadrant est une liste de listes), ou None en cas d'erreur.
        """
        Logger.info("Selector", "Loading quadrants configuration from 'configs/quadrants.json'")
        config_path = Path('configs/quadrants.json')
        if not config_path.is_file():
             self._handle_config_error(f"Quadrants configuration file not found at {config_path}")
             return None
             
        try:
            with config_path.open('r') as file:
                self.quadrants_config = json.load(file)
                # trie les noms pour un affichage cohérent
                self.quadrant_names = sorted(self.quadrants_config.keys())
                quadrants_data = [self.quadrants_config[key] for key in self.quadrant_names]
                Logger.success("Selector", f"Successfully loaded {len(quadrants_data)} quadrant configurations.")
                return quadrants_data
        except json.JSONDecodeError as e:
            self._handle_config_error(f"Invalid JSON format in {config_path}: {e}")
            return None
        except Exception as e:
             self._handle_config_error(f"An unexpected error occurred while loading quadrants: {e}")
             return None

    def _handle_config_error(self, message):
        """
        procédure : gère les erreurs lors du chargement de la configuration.
        affiche un message d'erreur et prépare l'arrêt.

        params:
            message: message d'erreur spécifique.
        """
        Logger.critical("Selector", message)
        # idéalement, afficher une boîte de dialogue d'erreur à l'utilisateur ici
        self.running = False # arrête la boucle principale proprement

    def setup_ui(self):
        """
        procédure : crée et positionne tous les éléments de l'interface utilisateur.
        """
        # constantes pour le positionnement
        left_panel_width = 300
        left_panel_margin = 20
        element_height = 30
        element_spacing = 15 # espace vertical entre éléments
        label_spacing = 5 # espace entre label et élément
        current_y = 30 # position verticale courante
        element_width = left_panel_width - 2 * left_panel_margin
        
        # polices
        self.font = pygame.font.SysFont('Arial', 16)
        self.title_font = pygame.font.SysFont('Arial', 18, bold=True)
        
        self.labels = [] # liste pour stocker les labels et leurs positions
        
        # champ nom de la partie/sauvegarde
        self.labels.append(("Nom de la Partie:", (left_panel_margin, current_y)))
        current_y += self.title_font.get_height() + label_spacing
        self.entry_game_save = TextInput(left_panel_margin, current_y, element_width, element_height)
        current_y += element_height + element_spacing
        
        # sélection mode de jeu
        self.labels.append(("Mode de Jeu:", (left_panel_margin, current_y)))
        current_y += self.title_font.get_height() + label_spacing
        self.mode_selection = Dropdown(left_panel_margin, current_y, element_width, element_height, self.GAME_MODES, 0)
        current_y += element_height + element_spacing
        
        # sélection type de jeu
        self.labels.append(("Jeu:", (left_panel_margin, current_y)))
        current_y += self.title_font.get_height() + label_spacing
        self.game_selection = Dropdown(left_panel_margin, current_y, element_width, element_height, self.GAMES, 0)
        current_y += element_height + element_spacing
        
        # sélection des quadrants (4 dropdowns + boutons de rotation)
        self.labels.append(("Configuration Quadrants:", (left_panel_margin, current_y)))
        current_y += self.title_font.get_height() + label_spacing
        
        self.quadrant_selectors = []
        self.quadrant_rotation_buttons = []
        button_width = 30
        selector_width = element_width - 2 * button_width - 10 # largeur pour le dropdown du quadrant
        
        for i in range(4):
            # dropdown pour choisir le type de quadrant
            selector = Dropdown(left_panel_margin, current_y, 
                                selector_width, element_height, 
                                self.quadrant_names, i % len(self.quadrant_names)) # index par défaut pour varier
            self.quadrant_selectors.append(selector)
            
            # boutons de rotation gauche/droite
            left_button = Button(
                left_panel_margin + selector_width + 5, current_y, 
                button_width, element_height, "<-", # texte simple pour rotation gauche
                lambda idx=i: self.rotate_left(idx) # utilise lambda pour capturer l'index
            )
            right_button = Button(
                left_panel_margin + selector_width + 10 + button_width, current_y, 
                button_width, element_height, "->", # texte simple pour rotation droite
                lambda idx=i: self.rotate_right(idx)
            )
            self.quadrant_rotation_buttons.append((left_button, right_button))
            
            current_y += element_height + 5 # espace réduit entre les sélecteurs de quadrant
        
        current_y += element_spacing # espace après les quadrants
        
        # bouton charger/démarrer partie
        self.load_button = Button(
            left_panel_margin, current_y, 
            element_width, element_height, 
            "Démarrer / Charger", self.load_game
        )
        current_y += element_height + element_spacing
        
        # zone de prévisualisation du plateau
        preview_size = self.width - left_panel_width - 40 # taille de la zone carrée
        self.canvas_rect = pygame.Rect(left_panel_width + 20, 30, preview_size, preview_size)
        self.labels.append(("Prévisualisation:", (self.canvas_rect.left, 10)))

    def main_loop(self):
        """
        procédure : boucle principale d'événements et de rendu de l'interface de sélection.
        """
        while self.running:
            dt = self.clock.tick(30) / 1000.0 # delta time en secondes
            mouse_pos = pygame.mouse.get_pos()
            
            # gestion des événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    
                # passe l'événement aux éléments ui actifs
                # note: l'ordre peut importer si des éléments se superposent (dropdown ouvert)
                handled = self.entry_game_save.handle_event(event, mouse_pos)
                if not handled: handled = self.mode_selection.handle_event(event, mouse_pos)
                if not handled: handled = self.game_selection.handle_event(event, mouse_pos)
                
                # gère les dropdowns des quadrants (important s'ils sont ouverts)
                if not handled:
                    for selector in self.quadrant_selectors:
                         if selector.handle_event(event, mouse_pos):
                              self.update_selected_quadrants() # met à jour l'état si sélection change
                              handled = True
                              break # un seul dropdown peut gérer un clic
                              
                # gère les boutons de rotation
                if not handled:
                     for left_btn, right_btn in self.quadrant_rotation_buttons:
                          if left_btn.handle_event(event): handled = True; break
                          if right_btn.handle_event(event): handled = True; break
                          
                # gère le bouton principal
                if not handled:
                     self.load_button.handle_event(event)
            
            # mise à jour du survol pour tous les boutons
            for left_btn, right_btn in self.quadrant_rotation_buttons:
                 left_btn.check_hover(mouse_pos)
                 right_btn.check_hover(mouse_pos)
            self.load_button.check_hover(mouse_pos)
            
            # mise à jour des éléments (curseur du textinput)
            self.entry_game_save.update(dt * 1000) # dt attendu en ms par textinput
            
            # dessin de l'interface
            self.screen.fill((230, 230, 230)) # fond général
            
            # dessine les labels
            for text, pos in self.labels:
                text_surface = self.title_font.render(text, True, (0, 0, 0))
                self.screen.blit(text_surface, pos)
            
            # dessine les éléments ui (l'ordre importe pour le recouvrement)
            self.entry_game_save.draw(self.screen)
            # dessine les dropdowns des quadrants avant les autres pour que les options ouvertes soient visibles
            for selector in self.quadrant_selectors:
                selector.draw(self.screen)
            self.mode_selection.draw(self.screen)
            self.game_selection.draw(self.screen)
            
            # dessine les boutons
            for left_btn, right_btn in self.quadrant_rotation_buttons:
                left_btn.draw(self.screen)
                right_btn.draw(self.screen)
            self.load_button.draw(self.screen)
            
            # dessine la prévisualisation du plateau
            self.draw_quadrants()
            
            pygame.display.flip() # met à jour l'affichage complet
        
        pygame.quit() # nettoie pygame à la sortie de la boucle

    def get_saved_games(self):
        """
        fonction : récupère la liste des fichiers de sauvegarde existants dans le dossier 'saves'.
        
        retour:
            list: liste des noms de sauvegardes (sans l'extension .json).
        """
        saves_dir = Path('saves')
        saves_dir.mkdir(exist_ok=True) # crée le dossier s'il n'existe pas
        saved_games = [file.stem for file in saves_dir.glob('*.json')]
        Logger.debug("Selector", f"Found saved games: {saved_games}")
        return saved_games

    def load_game(self):
        """
        procédure : action déclenchée par le bouton "Démarrer / Charger".
        valide les sélections, ferme l'interface de sélection et lance le jeu.
        """
        game_save = self.entry_game_save.get().strip() # nettoie le nom
        selected_game = self.game_selection.get()
        selected_mode = self.mode_selection.get()
        
        # validation des paramètres
        if not self._validate_game_params(game_save, selected_mode):
            # idéalement, afficher un message d'erreur à l'utilisateur ici
            Logger.warning("Selector", "Game parameters validation failed.")
            return
            
        Logger.info("Selector", f"Attempting to start/load game: Type={selected_game}, Name={game_save}, Mode={selected_mode}")
        
        # vérifie si le type de jeu est valide
        if selected_game not in self.GAMES:
             Logger.error("Selector", f"Invalid game type selected: {selected_game}")
             # afficher message erreur
             return
             
        # le nom est valide, le type est valide, le mode est valide
        self.running = False # signale la fin de la boucle du sélecteur
        pygame.quit() # ferme la fenêtre du sélecteur
        
        # démarre le jeu choisi
        self._start_game(game_save, selected_game, selected_mode)
        
        # après la fin du jeu, propose de rejouer (relance le sélecteur)
        # self.ask_replay() # commenté car peut causer des problèmes si mal géré

    def _validate_game_params(self, game_save, selected_mode):
        """
        fonction : valide les paramètres de jeu saisis ou sélectionnés.

        params:
            game_save: nom de la partie/sauvegarde.
            selected_mode: mode de jeu sélectionné.

        retour:
            bool: True si les paramètres sont valides, False sinon.
        """
        if not game_save:
            Logger.warning("Selector", "Validation failed: Game name cannot be empty.")
            # afficher message erreur
            return False
            
        # on pourrait ajouter d'autres validations ici (caractères interdits, etc.)
        
        if selected_mode not in self.GAME_MODES:
             Logger.warning("Selector", f"Validation failed: Invalid game mode '{selected_mode}'.")
             return False
             
        return True

    def _start_game(self, game_save, selected_game, selected_mode):
        """
        procédure : crée l'instance du jeu et lance sa boucle principale.
        gère le chargement de sauvegarde si le fichier existe.

        params:
            game_save: nom de la partie/sauvegarde.
            selected_game: type de jeu ("katerenga", "isolation", "congress").
            selected_mode: mode de jeu ("Solo", "Bot", "Network").
        """
        try:
            # crée l'instance du jeu approprié
            game_instance = self._create_game_instance(selected_game, game_save, selected_mode)
            
            # vérifie si une sauvegarde existe pour ce nom
            save_file_path = Path(f'saves/{game_save}.json')
            if save_file_path.is_file():
                Logger.info("Selector", f"Loading saved game state from: {save_file_path}")
                # la fonction load_game met à jour l'état de game_instance
                success = load_game(game_instance)
                if success:
                     Logger.success("Selector", "Game state loaded successfully.")
                     # assure que le rendu initial reflète l'état chargé
                     if hasattr(game_instance, 'render') and game_instance.render:
                          game_instance.render.render_board()
                else:
                     Logger.error("Selector", "Failed to load game state, starting new game.")
            else:
                 Logger.info("Selector", f"No save file found for '{game_save}'. Starting new game.")
            
            # lance la boucle principale du jeu chargé ou nouveau
            if hasattr(game_instance, 'load_game'):
                game_instance.load_game() # cette méthode contient la boucle principale du jeu
                Logger.success("Selector", f"Game '{selected_game}' finished.")
            else:
                 Logger.error("Selector", f"Game instance for '{selected_game}' does not have a 'load_game' method.")

        except Exception as e:
            Logger.critical("Selector", f"Critical error during game execution: {str(e)}", exc_info=True)
            # assure que pygame est quitté même en cas d'erreur grave
            pygame.quit()
            exit(1)

    def _create_game_instance(self, game_type, game_save, mode):
        """
        fonction : crée et retourne une instance du jeu correspondant au type donné.

        params:
            game_type: chaîne identifiant le jeu ("katerenga", etc.).
            game_save: nom de la partie/sauvegarde.
            mode: mode de jeu ("Solo", "Bot", "Network").

        retour:
            object: instance de la classe de jeu appropriée (Katerenga, Isolation, Congress).
        
        exceptions:
            ValueError: si game_type est inconnu.
        """
        Logger.info("Selector", f"Creating game instance: Type={game_type}, Name={game_save}, Mode={mode}")
        # utilise les quadrants sélectionnés et potentiellement pivotés
        current_quadrants_config = self.selected_quadrants 
        
        match game_type:
            case "katerenga":
                return Katerenga(game_save, current_quadrants_config, mode)
            case "isolation":
                return Isolation(game_save, current_quadrants_config, mode)
            case "congress":
                return Congress(game_save, current_quadrants_config, mode)
            case _:
                # lève une exception si le type de jeu n'est pas reconnu
                Logger.error("Selector", f"Attempted to create unknown game type: {game_type}")
                raise ValueError(f"Undefined game type: {game_type}")

    def ask_replay(self):
        """
        procédure : (potentiellement problématique) tente de relancer le sélecteur.
        note: recréer __init__ dans une méthode existante est une mauvaise pratique.
        il faudrait une structure différente pour gérer le flux rejouer/quitter.
        """
        Logger.warning("Selector", "ask_replay called. Re-initializing selector - this might be unstable.")
        pass

    def draw_quadrants(self):
        """
        procédure : dessine la prévisualisation des 4 quadrants configurés sur le canvas dédié.
        """
        quadrant_area_size = self.canvas_rect.width // 2 # taille d'un carré pour un quadrant
        cell_size = quadrant_area_size // 4 # taille d'une cellule dans la prévisualisation
        
        # dessine chaque quadrant à sa position (0, 1, 2, 3)
        for i in range(4):
            # récupère les données du quadrant actuellement sélectionné et potentiellement pivoté
            quadrant_data = self.selected_quadrants[i]
            # calcule le décalage x, y pour ce quadrant dans la grille 2x2
            x_offset = (i % 2) * quadrant_area_size + self.canvas_rect.left
            y_offset = (i // 2) * quadrant_area_size + self.canvas_rect.top
            # dessine le quadrant cellule par cellule
            self._draw_quadrant(quadrant_data, x_offset, y_offset, cell_size)
            # dessine une bordure autour de la zone du quadrant
            pygame.draw.rect(self.screen, (50, 50, 50), 
                             (x_offset, y_offset, quadrant_area_size, quadrant_area_size), 2)


    def _draw_quadrant(self, quadrant_data, x_offset, y_offset, cell_size):
        """
        procédure : dessine un quadrant spécifique cellule par cellule.

        params:
            quadrant_data: liste de listes représentant le quadrant (contient l'index couleur).
            x_offset, y_offset: coin supérieur gauche de la zone de dessin du quadrant.
            cell_size: taille d'une cellule dans la prévisualisation.
        """
        for row_i, row in enumerate(quadrant_data):
            for col_i, cell_state in enumerate(row):
                x1 = x_offset + col_i * cell_size
                y1 = y_offset + row_i * cell_size
                
                # récupère la couleur rgb à partir de l'index stocké dans cell_state[1]
                color_index = cell_state[1]
                cell_color = Render.QUADRANTS_CELLS_COLORS.get(color_index, (128, 128, 128)) # gris par défaut
                
                # dessine le rectangle de la cellule
                pygame.draw.rect(
                    self.screen, 
                    cell_color, 
                    (x1, y1, cell_size, cell_size)
                )
                # dessine la bordure de la cellule
                pygame.draw.rect(
                    self.screen, 
                    (0, 0, 0), # bordure noire
                    (x1, y1, cell_size, cell_size),
                    1 # épaisseur 1
                )

    def update_selected_quadrants(self):
        """
        procédure : met à jour la liste self.selected_quadrants en fonction des sélections
        faites dans les dropdowns. réinitialise les rotations.
        """
        Logger.debug("Selector", "Updating selected quadrants based on dropdowns.")
        new_selected_quadrants = []
        for i, selector in enumerate(self.quadrant_selectors):
            selected_name = selector.get()
            if selected_name and selected_name in self.quadrants_config:
                 # prend une copie profonde de la configuration de base pour ce nom
                 new_selected_quadrants.append([row[:] for row in self.quadrants_config[selected_name]])
            else:
                 # si la sélection est invalide, garde la configuration par défaut (ou l'ancienne?)
                 # gardons l'ancienne pour l'instant pour éviter une réinitialisation inattendue
                 Logger.warning("Selector", f"Invalid quadrant name '{selected_name}' selected for quadrant {i}. Keeping previous.")
                 # ou utiliser une valeur par défaut:
                 # default_index = i % len(self.quadrants)
                 # new_selected_quadrants.append([row[:] for row in self.quadrants[default_index]])
                 new_selected_quadrants.append(self.selected_quadrants[i]) # garde l'ancien état

        self.selected_quadrants = new_selected_quadrants

    def rotate_right(self, index):
        """
        procédure : fait pivoter le quadrant sélectionné à l'index donné de 90 degrés vers la droite.

        params:
            index: index (0-3) du quadrant à pivoter dans self.selected_quadrants.
        """
        if not (0 <= index < 4):
             Logger.error("Selector", f"Invalid index {index} for rotation.")
             return
             
        Logger.debug("Selector", f"Rotating quadrant {index} right.")
        quadrant = self.selected_quadrants[index]
        size = len(quadrant) # taille du quadrant (normalement 4)
        rotated = [[(None, None) for _ in range(size)] for _ in range(size)] # crée une nouvelle grille vide
        for i in range(size):
            for j in range(size):
                rotated[j][size - 1 - i] = quadrant[i][j]
        self.selected_quadrants[index] = rotated

    def rotate_left(self, index):
        """
        procédure : fait pivoter le quadrant sélectionné à l'index donné de 90 degrés vers la gauche.

        params:
            index: index (0-3) du quadrant à pivoter dans self.selected_quadrants.
        """
        if not (0 <= index < 4):
             Logger.error("Selector", f"Invalid index {index} for rotation.")
             return
             
        Logger.debug("Selector", f"Rotating quadrant {index} left.")
        quadrant = self.selected_quadrants[index]
        size = len(quadrant) # taille du quadrant (normalement 4)
        rotated = [[(None, None) for _ in range(size)] for _ in range(size)] # crée une nouvelle grille vide
        for i in range(size):
            for j in range(size):
                rotated[size - 1 - j][i] = quadrant[i][j]
        self.selected_quadrants[index] = rotated
