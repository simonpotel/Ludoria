import pygame
from src.windows.screens.base_screen import BaseScreen
from src.windows.components.button import Button
from src.windows.components.image_button import ImageButton
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
        self.server_info = f"Server: {self.network_client.host}:{self.network_client.port}"
        self.version = "V1"
        self.quit_requested = False 
        
        self.refresh_timer = 0
        self.refresh_interval = 5000 
        
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
        
        theme = self.theme_manager.current_theme
        self.background = pygame.image.load(f'assets/{theme}/background.png').convert()
        Logger.info("JoinGameScreen", f"Using theme: {theme} for background")
        
        self.icon_green_circle = pygame.image.load('assets/Basic_GUI_Bundle/ButtonsIcons/IconButton_Large_Green_Circle.png').convert_alpha()
        self.icon_red_circle = pygame.image.load('assets/Basic_GUI_Bundle/ButtonsIcons/IconButton_Large_Red_Circle.png').convert_alpha()
        
        try:
            self.icon_refresh = pygame.image.load('assets/Basic_GUI_Bundle/ButtonsIcons/IconButton_Large_Green_Circle.png').convert_alpha()
        except:
            Logger.warning("JoinGameScreen", "Navigation icons not found, using defaults")
            self.icon_refresh = self.icon_green_circle
            
        self.connect_to_server()
        
        self.last_refresh_time = pygame.time.get_ticks()
        
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
        self.title_font = self.font_manager.get_font(48)
        self.status_font = self.font_manager.get_font(20)
        self.host_font = self.font_manager.get_font(18)
        self.button_font = self.font_manager.get_font(18)
        self.footer_font = self.font_manager.get_font(14)
            
        panel_width = int(self.width * 0.7)
        panel_height = int(self.height * 0.6)
        self.panel_x = (self.width - panel_width) // 2
        
        self.panel_y = self.navbar_height + 120 
        
        self.panel_width = panel_width
        self.panel_height = panel_height
        
        list_margin_top = 80
        list_margin_bottom = 50
        self.list_area_x = self.panel_x + 20
        self.list_area_y = self.panel_y + list_margin_top
        self.list_area_width = self.panel_width - 40
        self.list_area_height = self.panel_height - list_margin_top - list_margin_bottom
        
        self.row_height = 80
        self.row_spacing = 12
        
        button_refresh_path = 'assets/Basic_GUI_Bundle/ButtonsText/ButtonText_Large_GreyOutline_Square.png'
        refresh_button_width = 120
        refresh_button_height = 40
        
        self.refresh_button = ImageButton(
            self.panel_x + self.panel_width - refresh_button_width - 20, 
            self.panel_y + 20, 
            refresh_button_width, 
            refresh_button_height,
            "REFRESH", 
            lambda: self.refresh_games(),
            bg_image_path=button_refresh_path,
            font=self.button_font,
            text_color=(255, 255, 255)
        )
        
    def go_to_previous_screen(self):
        """
        procédure : retourne à l'écran de sélection de mode précédent
        ferme l'écran actuel et définit l'écran suivant
        """
        from src.windows.screens.game_selection.mode_selection import ModeSelectionScreen
        self.running = False
        self.next_screen = ModeSelectionScreen
        
    def show_menu(self):
        """
        procédure : affiche le menu d'options (à implémenter)
        enregistre l'action dans le journal pour une implémentation future
        """
        Logger.info("JoinGameScreen", "Menu button clicked")
        
    def join_game(self, game_index):
        """
        procédure : rejoint la partie sélectionnée par son index dans la liste
        
        params:
            game_index - index de la partie à rejoindre dans self.games_list
            
        valide le jeu sélectionné, se déconnecte du lobby et lance la partie réseau
        """
        # Vérifie si l'index est valide
        if game_index < 0 or game_index >= len(self.games_list):
            Logger.warning("JoinGameScreen", "Invalid game selection")
            return
            
        selected_game = self.games_list[game_index]
        game_name = selected_game.get("game_id")
        game_type = selected_game.get("game_type")
        
        if not game_name or not game_type:
            Logger.warning("JoinGameScreen", "Invalid game selection")
            return
        
        Logger.info("JoinGameScreen", f"Joining network game '{game_name}' of type '{game_type}'")
        
        player_name = "Player"
        
        valid_params = self.game_launcher.validate_game_params(
            game_name, "Network", ["Solo", "Bot", "Network"]
        )
        
        if valid_params:
            Logger.info("JoinGameScreen", "Directly launching game")
            self.running = False
            
            if self.network_client.connected:
                self.network_client.disconnect("Starting game")
            
            from src.windows.screens.game_selection.mode_selection import ModeSelectionScreen
            self.next_screen = ModeSelectionScreen
            
            game_success = self.game_launcher.start_game(
                game_name, game_type, "Network", self.selected_quadrants, player_name=player_name
            )
            
            if not game_success:
                Logger.warning("JoinGameScreen", "Game exited with errors")
    
    def refresh_games(self):
        """
        procédure : demande la liste mise à jour des jeux au serveur
        
        établit la connexion si nécessaire, puis envoie une requête de liste de parties
        """
        if not self.network_client.connected:
            self.connect_to_server()
        else:
            self.network_client.request_game_list()
            Logger.info("JoinGameScreen", "Refreshing game list")
    
    def handle_screen_events(self, event):
        """
        procédure : gère les événements pour cet écran
        
        params:
            event - événement pygame à traiter
            
        traite les interactions utilisateur avec les boutons et la liste des parties
        """
        mouse_pos = pygame.mouse.get_pos()
        
        self.refresh_button.handle_event(event)
        
        if hasattr(self, 'join_buttons'):
            for button in self.join_buttons:
                button.handle_event(event)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.panel_x <= mouse_pos[0] <= self.panel_x + self.panel_width:
                for i, game in enumerate(self.games_list):
                    row_y = self.list_area_y + i * (self.row_height + self.row_spacing)
                    if row_y <= mouse_pos[1] <= row_y + self.row_height:
                        join_button_width = 100
                        join_button_height = 40
                        join_button_x = self.list_area_x + self.list_area_width - 16 - join_button_width
                        join_button_y = row_y + (self.row_height - join_button_height) // 2
                        
                        if (join_button_x <= mouse_pos[0] <= join_button_x + join_button_width and 
                            join_button_y <= mouse_pos[1] <= join_button_y + join_button_height):
                            self.join_game(i)
                            break
    
    def update_screen(self, mouse_pos):
        """
        procédure : met à jour l'état de l'écran
        
        params:
            mouse_pos - position actuelle de la souris
            
        vérifie le survol des boutons et gère le rafraîchissement automatique
        """
        self.refresh_button.check_hover(mouse_pos)
        
        if hasattr(self, 'join_buttons'):
            for button in self.join_buttons:
                button.check_hover(mouse_pos)
                
        current_time = pygame.time.get_ticks()
        if current_time - self.last_refresh_time > self.refresh_interval:
            self.refresh_games()
            self.last_refresh_time = current_time
    
    def apply_blur(self, surface, amount=3):
        """
        fonction : applique un effet de flou à une surface pygame
        
        params:
            surface - la surface pygame à flouter
            amount - intensité du flou (valeur entière > 0)
            
        retour:
            surface - la surface floutée
        """
        width, height = surface.get_size()
        scaled = pygame.transform.smoothscale(surface, (width//amount, height//amount))
        return pygame.transform.smoothscale(scaled, (width, height))
    
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
        procédure : dessine tous les éléments de l'écran de jointure de partie
        
        affiche l'arrière-plan, le panneau principal, les titres, le bouton de rafraîchissement
        et la liste des parties disponibles avec leurs informations et boutons
        """
        if self.width > 0 and self.height > 0:
            bg_scaled = pygame.transform.scale(self.background, (self.width, self.height))
            bg_blurred = self.apply_blur(bg_scaled, 2)
            self.screen.blit(bg_blurred, (0, 0))
        
        self.draw_rounded_rect(self.screen, (self.panel_x, self.panel_y, self.panel_width, self.panel_height), 
                            (255, 255, 255), radius=12, alpha=153)  # 60% opacity (153/255)
        
        title_network = self.title_font.render("NETWORK", True, (255, 255, 255))
        title_join = self.title_font.render("JOIN A GAME", True, (255, 255, 255))
        title_network_x = (self.width - title_network.get_width()) // 2
        title_join_x = (self.width - title_join.get_width()) // 2
        self.screen.blit(title_network, (title_network_x, self.panel_y - 110))
        self.screen.blit(title_join, (title_join_x, self.panel_y - 60))
        
        self.refresh_button.draw(self.screen)
        
        visible_count = min(len(self.games_list), 
                          int(self.list_area_height // (self.row_height + self.row_spacing)))
        
        self.join_buttons = []
        button_img_path = "assets/Basic_GUI_Bundle/ButtonsText/ButtonText_Large_GreyOutline_Square.png"
        
        for i in range(visible_count):
            if i >= len(self.games_list):
                break
                
            game = self.games_list[i]
            row_y = self.list_area_y + i * (self.row_height + self.row_spacing)
            
            self.draw_rounded_rect(self.screen, 
                               (self.list_area_x, row_y, self.list_area_width, self.row_height),
                               (50, 50, 60), radius=8, alpha=80)
            
            player_count = game.get("player_count", 0)
            max_players = game.get("max_players", 2)
            icon = self.icon_green_circle if player_count < max_players else self.icon_red_circle
            icon = pygame.transform.scale(icon, (48, 48))
            self.screen.blit(icon, (self.list_area_x + 16, row_y + (self.row_height - 48) // 2))
            
            game_type = game.get("game_type", "UNKNOWN").upper()
            status_text = f"{player_count}/{max_players} {game_type}"
            status_surface = self.status_font.render(status_text, True, (255, 255, 255))
            self.screen.blit(status_surface, (self.list_area_x + 16 + 48 + 8, 
                                          row_y + (self.row_height - 48) // 2))
            
            game_name = game.get("game_id", "UNKNOWN").upper()
            game_name_surface = self.host_font.render(game_name, True, (221, 221, 221))
            self.screen.blit(game_name_surface, (self.list_area_x + 16 + 48 + 8, 
                                        row_y + (self.row_height - 48) // 2 + 28))
            
            join_button_width = 100
            join_button_height = 40
            join_button_x = self.list_area_x + self.list_area_width - 16 - join_button_width
            join_button_y = row_y + (self.row_height - join_button_height) // 2
            
            join_button = ImageButton(
                join_button_x, 
                join_button_y, 
                join_button_width, 
                join_button_height,
                "JOIN", 
                lambda idx=i: self.join_game(idx),
                bg_image_path=button_img_path,
                font=self.button_font,
                text_color=(255, 255, 255)
            )
            
            self.join_buttons.append(join_button)
            join_button.draw(self.screen)
        
        server_surface = self.footer_font.render(self.server_info, True, (255, 255, 255, 204))  # 80% opacity
        version_surface = self.footer_font.render(self.version, True, (255, 255, 255, 204))  # 80% opacity
        
        self.screen.blit(server_surface, (self.panel_x + 16, self.panel_y + self.panel_height - 16 - server_surface.get_height()))
        self.screen.blit(version_surface, (self.panel_x + self.panel_width - 16 - version_surface.get_width(), 
                                       self.panel_y + self.panel_height - 16 - version_surface.get_height()))
