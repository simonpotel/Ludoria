import pygame
from src.windows.screens.base_screen import BaseScreen
from src.windows.components.button import Button
from src.utils.logger import Logger
from src.windows.selector.game_launcher import GameLauncher
from src.network.client.client import NetworkClient
from src.windows.components.text_input import TextInput
from src.windows.selector.config_loader import ConfigLoader

class JoinGameScreen(BaseScreen):
    def __init__(self):
        super().__init__(title="Ludoria - Join Network Game")
        self.game_launcher = GameLauncher()
        self.network_client = NetworkClient()
        self.config_loader = ConfigLoader()
        self.games_list = []
        self.selected_game_index = -1
        self.refresh_button = None
        self.join_button = None
        self.player_name_input = None
        
        # charger les quadrants par défaut
        self.quadrants_config = None
        config_result = self.config_loader.load_quadrants()
        if config_result:
            self.quadrants_config, self.quadrant_names, _ = config_result
            # initialiser les quadrants sélectionnés par défaut
            self.selected_quadrants = []
            for i in range(4):
                if i < len(self.quadrant_names):
                    self.selected_quadrants.append(self.quadrants_config.get(self.quadrant_names[i % len(self.quadrant_names)]))
        else:
            Logger.error("JoinGameScreen", "Failed to load quadrant configurations.")
            self.selected_quadrants = None
            
        self.connect_to_server()
        
    def connect_to_server(self):
        """procédure : se connecte au serveur de jeu et demande la liste des jeux"""
        if self.network_client.connect_to_lobby():
            self.network_client.register_handler("game_list_received", self.on_game_list_received)
            self.network_client.request_game_list()
            Logger.info("JoinGameScreen", "Connected to server lobby")
        else:
            Logger.error("JoinGameScreen", "Failed to connect to server lobby")
    
    def on_game_list_received(self, games):
        """procédure : gestionnaire pour recevoir la liste des jeux depuis le serveur"""
        self.games_list = games
        Logger.info("JoinGameScreen", f"Received {len(games)} games from server")
    
    def setup_ui(self):
        panel_width = 600
        #panel_height = 400
        padding = 20
        element_height = 30
        element_spacing = 20
        current_y = self.navbar_height + 40
        element_width = panel_width - 2 * padding
        
        title_font = pygame.font.SysFont('Arial', 24, bold=True)
        self.font = pygame.font.SysFont('Arial', 16)
        self.header_font = pygame.font.SysFont('Arial', 18, bold=True)
        
        self.labels = []
        
        title_text = "Join Network Game"
        title_surface = title_font.render(title_text, True, (50, 50, 50))
        title_x = (self.width - title_surface.get_width()) // 2
        self.labels.append((title_text, (title_x, current_y), title_font))
        current_y += title_font.get_height() + 30
        
        panel_x = (self.width - panel_width) // 2
        
        self.labels.append(("Your Name:", (panel_x, current_y), self.font))
        current_y += self.font.get_height() + 5
        
        self.player_name_input = TextInput(
            panel_x, current_y, element_width, element_height
        )
        current_y += element_height + element_spacing
        
        # dimensions de la table
        self.table_x = panel_x
        self.table_y = current_y
        self.table_width = element_width
        self.table_height = 250  
        self.row_height = 30
        
        current_y += self.table_height + element_spacing
        
        # boutons
        button_width = (element_width - padding) // 2
        
        self.refresh_button = Button(
            panel_x, current_y, button_width, 40, 
            "Refresh Games", self.refresh_games
        )
        
        self.join_button = Button(
            panel_x + button_width + padding, current_y, button_width, 40, 
            "Join Game", self.join_game
        )
        
        # dimensions des colonnes de la table (pourcentage de la largeur de la table)
        self.column_sizes = [0.30, 0.30, 0.40]
    
    def refresh_games(self):
        """procédure : demande la liste mise à jour des jeux depuis le serveur"""
        if not self.network_client.connected:
            self.connect_to_server()
        else:
            self.network_client.request_game_list()
            Logger.info("JoinGameScreen", "Refreshing game list")
    
    def join_game(self):
        """procédure : rejoindre le jeu sélectionné"""
        player_name = self.player_name_input.get()
        if not player_name:
            Logger.warning("JoinGameScreen", "Please enter your name before joining")
            return
            
        if self.selected_game_index < 0 or self.selected_game_index >= len(self.games_list):
            Logger.warning("JoinGameScreen", "No game selected")
            return
        
        selected_game = self.games_list[self.selected_game_index]
        game_name = selected_game.get("game_id")
        game_type = selected_game.get("game_type")
        
        if not game_name or not game_type:
            Logger.warning("JoinGameScreen", "Invalid game selection")
            return
        
        Logger.info("JoinGameScreen", f"Joining network game '{game_name}' of type '{game_type}'")
        
        # lancer le jeu directement au lieu d'aller à l'écran de configuration
        valid_params = self.game_launcher.validate_game_params(
            game_name, "Network", ["Solo", "Bot", "Network"]
        )
        
        if valid_params:
            Logger.info("JoinGameScreen", "Directly launching game")
            self.running = False
            
            # déconnecter la connexion du lobby
            if self.network_client.connected:
                self.network_client.disconnect("Starting game")
            
            # retour à l'écran de sélection de mode après la fin du jeu
            from src.windows.screens.game_selection.mode_selection import ModeSelectionScreen
            self.next_screen = ModeSelectionScreen
            
            # lancer le jeu avec le nom du joueur et les quadrants
            game_success = self.game_launcher.start_game(
                game_name, game_type, "Network", self.selected_quadrants, player_name=player_name
            )
            
            if not game_success:
                Logger.warning("JoinGameScreen", "Game exited with errors")
    
    def handle_screen_events(self, event):
        mouse_pos = pygame.mouse.get_pos()
        
        # gérer l'input du nom du joueur
        self.player_name_input.handle_event(event, mouse_pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            # vérifier si le clic est dans la zone de la table
            if (self.table_x <= mouse_pos[0] <= self.table_x + self.table_width and
                self.table_y <= mouse_pos[1] <= self.table_y + self.table_height):
                # calculer quelle ligne a été cliquée
                relative_y = mouse_pos[1] - self.table_y - self.row_height  # ignorer la première ligne
                if relative_y >= 0:
                    clicked_row = relative_y // self.row_height
                    if 0 <= clicked_row < len(self.games_list):
                        self.selected_game_index = clicked_row
        
        self.refresh_button.handle_event(event)
        self.join_button.handle_event(event)
    
    def update_screen(self, mouse_pos):
        self.player_name_input.update(16)
        self.refresh_button.check_hover(mouse_pos)
        self.join_button.check_hover(mouse_pos)
    
    def draw_screen(self):
        # dessiner les labels
        for text, pos, font in self.labels:
            text_surface = font.render(text, True, (0, 0, 0))
            self.screen.blit(text_surface, pos)
        
        # dessiner l'input du nom du joueur
        self.player_name_input.draw(self.screen)
        
        # dessiner la table
        self.draw_table()
        
        # dessiner les boutons
        self.refresh_button.draw(self.screen)
        self.join_button.draw(self.screen)
    
    def draw_table(self):
        # dessiner le fond de la table
        pygame.draw.rect(self.screen, (240, 240, 240), 
                        (self.table_x, self.table_y, self.table_width, self.table_height))
        
        # dessiner la bordure de la table
        pygame.draw.rect(self.screen, (200, 200, 200), 
                        (self.table_x, self.table_y, self.table_width, self.table_height), 1)
        
        # dessiner l'en-tête
        header_bg_rect = (self.table_x, self.table_y, self.table_width, self.row_height)
        pygame.draw.rect(self.screen, (220, 220, 220), header_bg_rect)
        pygame.draw.line(self.screen, (200, 200, 200), 
                        (self.table_x, self.table_y + self.row_height),
                        (self.table_x + self.table_width, self.table_y + self.row_height))
        
        # titres de l'en-tête
        header_titles = ["Game Name", "Game Type", "Status"]
        current_x = self.table_x + 10
        
        for i, title in enumerate(header_titles):
            column_width = int(self.column_sizes[i] * self.table_width)
            title_surface = self.header_font.render(title, True, (50, 50, 50))
            self.screen.blit(title_surface, (current_x, self.table_y + 5))
            current_x += column_width
            
            # dessiner le séparateur vertical
            if i < len(header_titles) - 1:
                pygame.draw.line(self.screen, (200, 200, 200),
                                (self.table_x + int(sum(self.column_sizes[:i+1]) * self.table_width), self.table_y),
                                (self.table_x + int(sum(self.column_sizes[:i+1]) * self.table_width), self.table_y + self.table_height))
        
        # dessiner les lignes
        for i, game in enumerate(self.games_list):
            row_y = self.table_y + self.row_height + (i * self.row_height)
            
            # dessiner le fond de la ligne (mettre en évidence si sélectionné)
            row_bg_color = (230, 240, 255) if i == self.selected_game_index else (255, 255, 255)
            row_bg_rect = (self.table_x, row_y, self.table_width, self.row_height)
            pygame.draw.rect(self.screen, row_bg_color, row_bg_rect)
            
            # dessiner les données de la ligne
            current_x = self.table_x + 10
            
            # nom du jeu
            game_name = game.get("game_id", "Unknown")
            text_surface = self.font.render(game_name, True, (0, 0, 0))
            self.screen.blit(text_surface, (current_x, row_y + 5))
            current_x += int(self.column_sizes[0] * self.table_width)
            
            # type de jeu
            game_type = game.get("game_type", "Unknown")
            text_surface = self.font.render(game_type, True, (0, 0, 0))
            self.screen.blit(text_surface, (current_x, row_y + 5))
            current_x += int(self.column_sizes[1] * self.table_width)
            
            # statut
            player_count = game.get("player_count", 0)
            max_players = game.get("max_players", 2)
            status = f"{player_count}/{max_players} Players"
            text_surface = self.font.render(status, True, (0, 0, 0))
            self.screen.blit(text_surface, (current_x, row_y + 5))
            
            # dessiner le séparateur de ligne
            pygame.draw.line(self.screen, (220, 220, 220),
                            (self.table_x, row_y + self.row_height),
                            (self.table_x + self.table_width, row_y + self.row_height)) 