import pygame
import os
from src.windows.screens.base_screen import BaseScreen
from src.windows.components.image_button import ImageButton
from src.utils.logger import Logger
from src.utils.theme_manager import ThemeManager
from src.network.client.client import NetworkClient


class ModeSelectionScreen(BaseScreen):
    def __init__(self):
        super().__init__(title="Ludoria - Mode Selection")
        self.mode_buttons = []
        self.modes = ["SOLO", "BOT", "NETWORK"]
        self.theme_manager = ThemeManager()
        self.background = None
        self.player1_img = None
        self.player2_img = None
        self.version = "v1"
        self.server_address = NetworkClient().host

        # définition des règles pour chaque jeu
        self.game_rules = {
            "Movement": [
                "",
                "Unlike most board games, a pawn's movement does not depend on its nature since all pawns are identical, but on the color of the square it is located on.",
                "",
                "A pawn on a BLUE square moves like a chess king, i.e. to one of the 8 adjacent squares.",
                "",
                "A pawn on a GREEN square moves like a chess knight, i.e. in an L-shape (two squares in one direction, horizontal or vertical, and one square perpendicular to the first direction).",
                "",
                "A pawn on a YELLOW square moves like a chess bishop, i.e. diagonally over empty squares only, with the additional constraint that it must stop at the first yellow square it encounters.",
                "",
                "A pawn on a RED square moves like a chess rook, i.e. along the same row or column over empty squares only, with the additional constraint that it must stop at the first red square it encounters."
            ],
            "Katarenga": [
                "",
                " - Goal: Be the first player to place 2 of your pawns in the opponent's camps.",
                "   (Squares in the opposite corners of your starting camp)",
                "",
                " - Capture: A pawn can capture an opponent's pawn by moving to its square, EXCEPT ON THE VERY FIRST TURN of the game.",
                "   The captured pawn is removed from the board.",
                "",
                " - Camps: The camps are the four corner squares (0,0), (0,9), (9,0), (9,9).",
                "   - Once a pawn reaches an opponent's camp, it is BLOCKED and can no longer move.",
                "   - A pawn can only enter an opponent's camp if it is on the LAST ROW before that camp.",
                "",
                " - End of game: A player wins immediately if:",
                "   1. They place 2 of their pawns in the two opponent's camps.",
                "   2. The opponent can no longer make any legal moves (all their pawns are blocked or they have no squares to go to).",
                ""
            ],
            "Isolation": [
                "",
                " - Goal: Be the last player able to place a pawn.",
                "",
                " - Board: An empty board (8x8) where players place their pawns.",
                "",
                " - Gameplay: The game starts with an empty board.",
                "   - Players take turns placing one of their pawns on an empty square.",
                "   - A pawn can only be placed on a square where it cannot be potentially captured by any pawn already on the board (of either color).",
                "",
                " - Important: There are no moves or captures in this game.",
                "",
                " - End of game: The winner is the last player who can place a pawn."
            ],
            "Congress": [
                "",
                " - Goal: Be the first player to connect all their pawns together (form a continuous chain).",
                "",
                " - Board: A 8x8 board where the 16 pawns are placed on every other square around the board’s outermost border, starting with a black disc in the top-left corner and proceeding clockwise, alternating colors and leaving exactly one empty square between each piece.",
                "",
                " - Movement: The movements a are the basics movements of the pawns.",
                "",
                " - Connection: Two pawns are considered connected if they are on squares linked.",
                "   The connection is transitive (if A is connected to B and B to C, A is connected to C).",
                "   All of a player's pawns are connected if there exists a path of all the same color pawns.",
                "",
                " - Capture: There is no capture in Congress.",
                "",
                " - End of game: A player wins immediately if, at the end of their turn, all their pawns still on the board are connected to each other."
            ]
        }

    def setup_ui(self):
        button_font = self.font_manager.get_font(40)
        
        try:
            theme = self.theme_manager.current_theme
            bg_path = f"assets/{theme}/background.png"
            original_bg = pygame.image.load(bg_path).convert_alpha()
            self.background = pygame.transform.scale(original_bg, (self.width, self.height))
            
            blur_effect = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            blur_effect.fill((0, 0, 0, 180))
            self.background.blit(blur_effect, (0, 0))
        except Exception as e:
            Logger.error("ModeSelectionScreen", f"Error loading background image: {e}")
            self.background = None

        button_width = 280  
        button_height = 60  
        button_spacing = 10  
        button_img_path = "assets/Basic_GUI_Bundle/ButtonsText/ButtonText_Large_GreyOutline_Square.png"

        # ajout du bouton règles à la liste des modes pour le calcul de la hauteur
        all_buttons = self.modes + ["RULES"]

        total_height = (button_height * len(all_buttons)) + (button_spacing * (len(all_buttons) - 1))
        start_y = (self.height - total_height) // 2 + 30  

        first_button_y = 0
        last_button_bottom_y = 0
        
        for i, item in enumerate(all_buttons):
            y_pos = start_y + (button_height + button_spacing) * i
            
            if i == 0:
                first_button_y = y_pos
            if i == len(all_buttons) - 1:
                last_button_bottom_y = y_pos + button_height
                
            if item in self.modes:
                # bouton mode existant
                button = ImageButton(
                    (self.width - button_width) // 2,
                    y_pos,
                    button_width,
                    button_height,
                    item,
                    lambda m=item: self.select_mode(m),
                    bg_image_path=button_img_path,
                    font=button_font
                )
                self.mode_buttons.append(button)
            elif item == "RULES":
                # nouveau bouton règles
                rules_icon_path = "assets/Basic_GUI_Bundle/Icons/Icon_Regle.png"
                rules_button_bg_path = "assets/Basic_GUI_Bundle/ButtonsIcons/IconButton_Large_GreyOutline_Rounded.png"
                icon_button_size = 60 # on suppose que le bouton icône est carré et correspond à la hauteur pour l'instant

                rules_button = ImageButton(
                    (self.width - icon_button_size) // 2, # on centre le bouton icône
                    y_pos, # position en dessous du dernier bouton mode
                    icon_button_size,
                    icon_button_size,
                    "", # pas de texte sur le bouton icône
                    self.show_game_selection_popup, # lien vers la nouvelle méthode
                    bg_image_path=rules_button_bg_path,
                    icon_path=rules_icon_path
                )
                self.mode_buttons.append(rules_button)

        self.buttons_center_x = (self.width - button_width) // 2 + button_width // 2
        self.buttons_left_x = (self.width - button_width) // 2
        self.buttons_right_x = self.buttons_left_x + button_width

        # initialisation de l'état du popup règles
        self.rules_popup_visible = False
        self.rules_popup = None # sera initialisé lorsqu'il sera affiché

        try:
            theme = self.theme_manager.current_theme
            player1_path = f"assets/{theme}/joueur1.png"
            player2_path = f"assets/{theme}/joueur2.png"
            
            original_p1 = pygame.image.load(player1_path).convert_alpha()
            original_p2 = pygame.image.load(player2_path).convert_alpha()
            
            character_height = last_button_bottom_y - first_button_y
            
            p1_aspect = original_p1.get_width() / original_p1.get_height()
            p2_aspect = original_p2.get_width() / original_p2.get_height()
            
            p1_width = int(character_height * p1_aspect)
            p2_width = int(character_height * p2_aspect)
            
            self.player1_img = pygame.transform.smoothscale(original_p1, (p1_width, character_height))
            self.player2_img = pygame.transform.smoothscale(original_p2, (p2_width, character_height))
            
            self.p1_y = first_button_y
            self.p2_y = first_button_y
            
        except Exception as e:
            Logger.error("ModeSelectionScreen", f"Error loading player images: {e}")
            self.player1_img = None
            self.player2_img = None

    def select_mode(self, mode):
        Logger.info("ModeSelectionScreen", f"Selected mode: {mode}")
        if mode == "SOLO" or mode == "BOT":
            from src.windows.screens.game_config.game_config import GameConfigScreen
            self.next_screen = lambda: GameConfigScreen(mode)
        elif mode == "NETWORK":
            from src.windows.screens.network.network_options import NetworkOptionsScreen
            self.next_screen = NetworkOptionsScreen

        self.running = False

    def show_game_selection_popup(self):
        Logger.info("ModeSelectionScreen", "Showing game selection popup")
        popup_width = 400
        popup_height = 300
        popup_x = (self.width - popup_width) // 2
        popup_y = (self.height - popup_height) // 2
        self.rules_popup = pygame.Surface((popup_width, popup_height), pygame.SRCALPHA)
        self.rules_popup.fill((0, 0, 0, 200)) # fond semi-transparent noir

        title_font = self.font_manager.get_font(30)
        button_font = self.font_manager.get_font(25)
        line_spacing = 15
        text_start_x = 50
        text_start_y = 50
        current_y = text_start_y

        title_surface = title_font.render("Select a game:", True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(popup_width // 2, current_y))
        self.rules_popup.blit(title_surface, title_rect)
        current_y += title_rect.height + line_spacing * 2

        game_options = ["Movement", "Katarenga", "Isolation", "Congress"]
        self.game_selection_buttons = []

        for game_name in game_options:
            button_surface = button_font.render(game_name, True, (255, 255, 255))
            button_rect = button_surface.get_rect(center=(popup_width // 2, current_y))
            self.rules_popup.blit(button_surface, button_rect)
            self.game_selection_buttons.append((game_name, button_rect.move(popup_x, popup_y))) # stocker le rect avec le décalage du popup
            current_y += button_rect.height + line_spacing

        self.rules_popup_rect = self.rules_popup.get_rect(topleft=(popup_x, popup_y))
        self.rules_popup_visible = True
        self.current_popup_type = "selection" # suivi du popup visible

    def show_game_rules_popup(self, game_name):
        Logger.info("ModeSelectionScreen", f"Showing rules for {game_name}")
        # récupérer les règles de la classe
        rules_text = self.game_rules.get(game_name, ["Règles non disponibles pour ce jeu.", "Veuillez vérifier le nom du jeu."])

        popup_width = 700
        popup_height = 600 # hauteur augmentée pour accommoder plus de texte
        popup_x = (self.width - popup_width) // 2
        popup_y = (self.height - popup_height) // 2
        self.rules_popup = pygame.Surface((popup_width, popup_height), pygame.SRCALPHA)
        self.rules_popup.fill((0, 0, 0, 200)) # fond semi-transparent noir

        title_font = self.font_manager.get_font(30)
        rules_font = self.font_manager.get_font(20)
        line_spacing = 5
        text_start_x = 20
        text_start_y = 20
        current_y = text_start_y

        title_surface = title_font.render(f"Règles de {game_name}:", True, (255, 255, 255))
        self.rules_popup.blit(title_surface, (text_start_x, current_y))
        current_y += title_surface.get_height() + line_spacing * 2

        for line in rules_text:
            words = line.split(' ')
            rendered_lines = []
            current_line = ''
            for word in words:
                test_line = current_line + word + ' '
                test_surface = rules_font.render(test_line, True, (255, 255, 255))
                if test_surface.get_width() < popup_width - text_start_x * 2:
                    current_line = test_line
                else:
                    rendered_lines.append(current_line.strip())
                    current_line = word + ' '
            rendered_lines.append(current_line.strip())

            for rendered_line in rendered_lines:
                line_surface = rules_font.render(rendered_line, True, (255, 255, 255))
                self.rules_popup.blit(line_surface, (text_start_x + 10, current_y))
                current_y += line_surface.get_height() + line_spacing

        close_text = "Cliquez n'importe où pour fermer."
        close_surface = rules_font.render(close_text, True, (255, 255, 255))
        # calculer la position verticale en dessous de la dernière ligne de règle rendue
        close_y = current_y + line_spacing * 2 # ajouter un peu d'espace
        close_rect = close_surface.get_rect(center=(popup_width // 2, close_y))
        self.rules_popup.blit(close_surface, close_rect)

        self.rules_popup_rect = self.rules_popup.get_rect(topleft=(popup_x, popup_y))
        self.rules_popup_visible = True
        self.current_popup_type = "rules" # suivi du popup visible

    def handle_screen_events(self, event):
        # si le popup est visible, gérer les événements du popup en premier
        if self.rules_popup_visible:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # seulement gérer le clic gauche
                mouse_pos = event.pos
                clicked_on_button = False
                for game_name, button_rect in self.game_selection_buttons:
                    if button_rect.collidepoint(mouse_pos):
                        # masquer le popup de sélection
                        self.rules_popup_visible = False
                        self.rules_popup = None
                        self.game_selection_buttons = []

                        # transition vers l'écran des règles
                        from src.windows.screens.rules_screen import RulesScreen
                        # récupérer le texte des règles pour le jeu sélectionné
                        game_rules_text = self.game_rules.get(game_name, ["Règles non disponibles pour ce jeu.", "Veuillez vérifier le nom du jeu."])
                        self.next_screen = lambda: RulesScreen(game_name, game_rules_text)
                        self.running = False # arrêter la boucle de l'écran actuel
                        clicked_on_button = True
                        break # sortir de la boucle dès que le bouton est cliqué

                # si le clic n'est pas sur un bouton, masquer le popup de sélection
                if not clicked_on_button:
                    self.rules_popup_visible = False
                    self.rules_popup = None
                    self.game_selection_buttons = []

            return # consommer l'événement, ne pas le passer aux boutons

        # si aucun popup, gérer les événements des boutons
        for button in self.mode_buttons:
            button.handle_event(event)

    def update_screen(self, mouse_pos):
        # si le popup est visible, pas besoin de mettre à jour les boutons
        if self.rules_popup_visible:
             # vérifier le survol pour les boutons de sélection si le popup de sélection est visible
            if self.current_popup_type == "selection":
                 # pas de survol pour le texte pour l'instant, peut être ajouté plus tard si nécessaire
                 pass
            return

        for button in self.mode_buttons:
            button.check_hover(mouse_pos)

    def draw_screen(self):
        if self.background:
            self.screen.blit(self.background, (0, 0))
        
        title_text = "LUDORIA"
        title_font = self.font_manager.get_font(150)
        title_surface = title_font.render(title_text, True, (255, 255, 255))
        title_x = (self.width - title_surface.get_width()) // 2
        title_y = 100  
        self.screen.blit(title_surface, (title_x, title_y))

        if self.player1_img and self.player2_img:
            p1_x = self.buttons_left_x - self.player1_img.get_width() - 5  
            p2_x = self.buttons_right_x + 5  
            
            self.screen.blit(self.player1_img, (p1_x, self.p1_y))
            self.screen.blit(self.player2_img, (p2_x, self.p2_y))

        for button in self.mode_buttons:
            button.draw(self.screen)
        
        small_font = self.font_manager.get_font(20)
        
        server_text = f"SERVER: {self.server_address}"
        server_surface = small_font.render(server_text, True, (255, 255, 255))
        self.screen.blit(server_surface, (20, self.height - 30))
        
        version_surface = small_font.render(self.version, True, (255, 255, 255))
        version_x = self.width - version_surface.get_width() - 20
        version_y = self.height - 30
        self.screen.blit(version_surface, (version_x, version_y))
        
        # dessiner le popup des règles si visible
        if self.rules_popup_visible and self.rules_popup:
            self.screen.blit(self.rules_popup, self.rules_popup_rect.topleft)
        
