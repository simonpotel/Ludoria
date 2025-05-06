import pygame
import pygame.freetype
from functools import partial

from src.utils.logger import Logger
from src.windows.components import Button, Dropdown, TextInput
from src.windows.selector.config_loader import ConfigLoader
from src.windows.selector.quadrant_handler import QuadrantHandler
from src.windows.selector.game_launcher import GameLauncher


class Selector:
    """
    classe : interface graphique principale pour sélectionner et configurer un jeu.
    gère la sélection du type de jeu, du mode, du nom de sauvegarde et la configuration des quadrants.
    """
    GAMES = ["katerenga", "isolation", "congress"] # jeux disponibles
    GAME_MODES = ["Solo", "Bot", "Network"] # modes de jeu disponibles

    def __init__(self):
        """
        constructeur : procédure d'initialisation de la classe selector.
        initialise pygame, les gestionnaires (quadrant, config, lanceur de jeu) et la fenêtre principale.
        charge la configuration des quadrants et lance la boucle principale.
        """
        pygame.init()
        pygame.freetype.init()
        
        self.quadrant_handler = QuadrantHandler()
        self.config_loader = ConfigLoader()
        self.game_launcher = GameLauncher()
        
        self.width = 800
        self.height = 700
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Ludoria - Selector")
        self.clock = pygame.time.Clock()
        
        self.running = False # contrôle la boucle de l'interface de sélection
        self.outer_running = True # contrôle la boucle principale de l'application

        self.title_font = pygame.freetype.SysFont('Arial', 24)
        self.labels = []
        
        self.entry_game_save = None
        self.game_selection = None
        self.mode_selection = None
        self.load_button = None
        self.quadrant_selectors = []
        self.quadrant_rotation_buttons = []
        self.quadrant_preview_rect = pygame.Rect(400, 300, 320, 320) # zone de prévisualisation par défaut
        self.canvas_rect = None # sera défini dans setup_ui pour la zone de dessin
        
        config_result = self.config_loader.load_quadrants()
        if config_result:
            self.quadrants_config, self.quadrant_names, _ = config_result # _ quadrants_data non utilisé ici
            self.selected_quadrants = [None] * 4
        else:
            Logger.critical("Selector", "Failed to load quadrant configurations.")
            self.outer_running = False # empêche le lancement de la boucle principale si la config échoue
            return
        
        self.main_loop()

    def setup_ui(self):
        """
        procédure : configuration de l'interface utilisateur.
        crée et positionne tous les éléments graphiques (champs de texte, menus déroulants, boutons).
        initialise ou réinitialise les valeurs des éléments en préservant les sélections précédentes si possible.
        """
        left_panel_width = 300
        left_panel_margin = 20
        element_height = 30
        element_spacing = 15 # espacement vertical entre les éléments
        label_spacing = 5 # espacement entre le label et l'élément ui
        current_y = 30 # coordonnée y pour le positionnement vertical des éléments
        element_width = left_panel_width - 2 * left_panel_margin
        
        self.font = pygame.font.SysFont('Arial', 16)
        self.title_font = pygame.font.SysFont('Arial', 18, bold=True)
        
        self.labels = []
        
        self.labels.append(("Nom de la Partie:", (left_panel_margin, current_y)))
        current_y += self.title_font.get_height() + label_spacing
        previous_save_name = self.entry_game_save.get() if self.entry_game_save else "" # conserve le nom de sauvegarde précédent
        self.entry_game_save = TextInput(left_panel_margin, current_y, element_width, element_height, initial_text=previous_save_name)
        current_y += element_height + element_spacing
        
        self.labels.append(("Mode de Jeu:", (left_panel_margin, current_y)))
        current_y += self.title_font.get_height() + label_spacing
        previous_mode_idx = self.mode_selection.selected_index if self.mode_selection else 0 # conserve la sélection de mode précédente
        self.mode_selection = Dropdown(left_panel_margin, current_y, element_width, element_height, self.GAME_MODES, previous_mode_idx)
        current_y += element_height + element_spacing
        
        self.labels.append(("Jeu:", (left_panel_margin, current_y)))
        current_y += self.title_font.get_height() + label_spacing
        previous_game_idx = self.game_selection.selected_index if self.game_selection else 0 # conserve la sélection de jeu précédente
        self.game_selection = Dropdown(left_panel_margin, current_y, element_width, element_height, self.GAMES, previous_game_idx)
        current_y += element_height + element_spacing
        
        self.labels.append(("Configuration Quadrants:", (left_panel_margin, current_y)))
        current_y += self.title_font.get_height() + label_spacing
        
        self.quadrant_selectors = []
        self.quadrant_rotation_buttons = []
        button_width = 30
        selector_width = element_width - 2 * button_width - 10 # largeur ajustée pour le dropdown du quadrant et les boutons
        
        for i in range(4): # pour chacun des 4 quadrants
            previous_quad_idx = (self.quadrant_selectors[i].selected_index 
                                 if i < len(self.quadrant_selectors) and self.quadrant_selectors[i] 
                                 else (i % len(self.quadrant_names))) # conserve la sélection de quadrant ou une valeur par défaut
            selector = Dropdown(left_panel_margin, current_y, 
                                selector_width, element_height, 
                                self.quadrant_names, previous_quad_idx) 
            self.quadrant_selectors.append(selector)
            
            left_button = Button(
                left_panel_margin + selector_width + 5, current_y, 
                button_width, element_height, "< -", 
                partial(self._rotate_left_handler, i)
            )
            right_button = Button(
                left_panel_margin + selector_width + 10 + button_width, current_y, 
                button_width, element_height, "->", 
                partial(self._rotate_right_handler, i)
            )
            self.quadrant_rotation_buttons.append((left_button, right_button))
            
            current_y += element_height + 5 # espacement réduit entre les sélecteurs de quadrant
        
        current_y += element_spacing
        
        self.load_button = Button(
            left_panel_margin, current_y, 
            element_width, element_height, 
            "Démarrer / Charger", self.load_game
        )
        current_y += element_height + element_spacing
        
        preview_size = self.width - left_panel_width - 40 # taille pour la zone de prévisualisation carrée
        self.canvas_rect = pygame.Rect(left_panel_width + 20, 30, preview_size, preview_size)
        self.labels.append(("Prévisualisation:", (self.canvas_rect.left, 10)))
        
        self._update_selected_quadrants() # initialise les quadrants sélectionnés en fonction des dropdowns

    def _update_selected_quadrants(self):
        """
        procédure : mise à jour des quadrants sélectionnés.
        appelle le `quadrant_handler` pour mettre à jour la configuration des quadrants
        en fonction des sélections actuelles dans les menus déroulants.
        """
        self.selected_quadrants = self.quadrant_handler.update_selected_quadrants(
            self.quadrant_selectors, 
            self.selected_quadrants, 
            self.quadrants_config, 
            self.quadrant_names
        )

    def _rotate_left_handler(self, index):
        """
        procédure : gestionnaire de rotation à gauche d'un quadrant.
        params:
            index (int): index du quadrant à pivoter.
        """
        self.selected_quadrants = self.quadrant_handler.rotate_left(self.selected_quadrants, index)

    def _rotate_right_handler(self, index):
        """
        procédure : gestionnaire de rotation à droite d'un quadrant.
        params:
            index (int): index du quadrant à pivoter.
        """
        self.selected_quadrants = self.quadrant_handler.rotate_right(self.selected_quadrants, index)

    def main_loop(self):
        """
        procédure : boucle principale de l'interface de sélection.
        gère les événements utilisateurs, met à jour l'état de l'interface et dessine les éléments.
        cette boucle se réinitialise si un jeu est lancé puis quitté, permettant de revenir au sélecteur.
        """
        while self.outer_running: # boucle externe pour permettre de revenir au menu après un jeu
            self.screen = pygame.display.set_mode((self.width, self.height)) # réinitialise la surface de dessin
            pygame.display.set_caption("Ludoria- Selector")
            self.running = True # active la boucle interne du sélecteur
            self.setup_ui() # (ré)initialise l'interface utilisateur

            while self.running:
                dt = self.clock.tick(30) / 1000.0 # delta time pour les animations/mises à jour
                mouse_pos = pygame.mouse.get_pos()
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                        self.outer_running = False # quitte l'application complètement
                        continue 
                    
                    handled = False
                    
                    standard_input_elements = [
                        self.entry_game_save,
                        self.mode_selection,
                        self.game_selection
                    ]
                    for element in standard_input_elements:
                        if element.handle_event(event, mouse_pos):
                            handled = True
                            break
                    
                    if not handled:
                        for selector in self.quadrant_selectors:
                            if selector.handle_event(event, mouse_pos):
                                if not selector.is_open: # met à jour les quadrants seulement si le dropdown est fermé après l'événement
                                    self._update_selected_quadrants()
                                handled = True
                                break
                                
                    if not handled:
                        for left_btn, right_btn in self.quadrant_rotation_buttons:
                            if left_btn.handle_event(event):
                                handled = True
                                break
                            if right_btn.handle_event(event):
                                handled = True
                                break
                                
                    if not handled:
                        self.load_button.handle_event(event)
                
                open_dropdown = None
                all_dropdowns = [self.mode_selection, self.game_selection] + self.quadrant_selectors
                for dd in all_dropdowns:
                    if dd and dd.is_open:
                        open_dropdown = dd # identifie le menu déroulant actuellement ouvert
                        break 

                for left_btn, right_btn in self.quadrant_rotation_buttons:
                     left_btn.check_hover(mouse_pos)
                     right_btn.check_hover(mouse_pos)
                self.load_button.check_hover(mouse_pos)
                self.entry_game_save.update(dt * 1000) # mise à jour du champ de texte (ex: curseur clignotant)
                
                self.screen.fill((230, 230, 230)) # fond de l'écran
                for text, pos in self.labels:
                    text_surface = self.title_font.render(text, True, (0, 0, 0))
                    self.screen.blit(text_surface, pos)
                self.entry_game_save.draw(self.screen)
                
                for dd_element in all_dropdowns:
                    if dd_element and dd_element != open_dropdown:
                        dd_element.draw(self.screen) # dessine les dropdowns fermés
                
                for left_btn, right_btn in self.quadrant_rotation_buttons:
                    left_btn.draw(self.screen)
                    right_btn.draw(self.screen)
                self.load_button.draw(self.screen)
                self.quadrant_handler.draw_quadrants(self.screen, self.selected_quadrants, self.canvas_rect) # dessine la prévisualisation
                
                if open_dropdown:
                    open_dropdown.draw(self.screen) # dessine le dropdown ouvert par-dessus les autres éléments
                
                pygame.display.flip()
            
            if self.outer_running: # si on n'a pas quitté l'application via pygame.QUIT
                 Logger.info("Selector", "Returning to the game selection menu.")
                 # la boucle externe (`while self.outer_running`) recommence, réinitialisant l'ui via setup_ui()

        Logger.info("Selector", "Closing application.")
        pygame.quit()

    def load_game(self):
        """
        procédure : chargement et lancement d'un jeu.
        valide les paramètres de jeu (nom de sauvegarde, mode, type de jeu).
        si valide, informe le `game_launcher` pour démarrer le jeu sélectionné.
        met `self.running` à false pour quitter la boucle du sélecteur et permettre au jeu de prendre le relais.
        """
        game_save = self.entry_game_save.get().strip()
        selected_game = self.game_selection.get()
        selected_mode = self.mode_selection.get()
        
        if not self.game_launcher.validate_game_params(game_save, selected_mode, self.GAME_MODES):
            Logger.warning("Selector", "Invalid game parameters.")
            return
            
        Logger.info("Selector", f"Starting game: {selected_game}, name: {game_save}, mode: {selected_mode}")
        if selected_game not in self.GAMES:
             Logger.error("Selector", f"Unknown game type: {selected_game}")
             return
             
        self.running = False # arrête la boucle du sélecteur pour lancer le jeu
        
        self.game_launcher.start_game(game_save, selected_game, selected_mode, self.selected_quadrants)
