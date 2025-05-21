import pygame
from src.windows.screens.base_screen import BaseScreen
from src.windows.components.button import Button
from src.windows.components.dropdown import Dropdown
from src.windows.components.text_input import TextInput
from src.utils.logger import Logger
from src.windows.selector.game_launcher import GameLauncher
from src.windows.selector.config_loader import ConfigLoader
from src.windows.selector.quadrant_handler import QuadrantHandler
from src.network.client.client import NetworkClient

class CreateGameScreen(BaseScreen):
    GAMES = ["katerenga", "isolation", "congress"]
    
    def __init__(self):
        super().__init__(title="Ludoria - Create Network Game")
        self.game_launcher = GameLauncher()
        self.network_client = NetworkClient()
        self.config_loader = ConfigLoader()
        self.quadrant_handler = QuadrantHandler()
        
        self.game_name_input = None
        self.player_name_input = None
        self.game_dropdown = None
        self.create_button = None
        self.quadrant_config_button = None
        
        self.quadrants_config = None
        self.quadrant_names = None
        self.selected_quadrants = [None] * 4
        
        # charge les quadrants par défaut
        config_result = self.config_loader.load_quadrants()
        if config_result:
            self.quadrants_config, self.quadrant_names, _ = config_result
            # initialise avec les quadrants par défaut
            for i in range(4):
                if i < len(self.quadrant_names):
                    self.selected_quadrants[i] = self.quadrants_config.get(self.quadrant_names[i % len(self.quadrant_names)])
        else:
            Logger.error("CreateGameScreen", "Failed to load quadrant configurations.")
    
    def setup_ui(self):
        panel_width = 400
        padding = 20
        element_height = 30
        element_spacing = 20
        label_spacing = 5
        current_y = self.navbar_height + 40
        element_width = panel_width - 2 * padding
        
        title_font = pygame.font.SysFont('Arial', 24, bold=True)
        self.font = pygame.font.SysFont('Arial', 16)
        
        self.labels = []
        
        title_text = "Create Network Game"
        title_surface = title_font.render(title_text, True, (50, 50, 50))
        title_x = (self.width - title_surface.get_width()) // 2
        self.labels.append((title_text, (title_x, current_y)))
        current_y += title_font.get_height() + 30
        
        panel_x = (self.width - panel_width) // 2
        
        self.labels.append(("Game Name:", (panel_x, current_y)))
        current_y += self.font.get_height() + label_spacing
        
        self.game_name_input = TextInput(
            panel_x, current_y, element_width, element_height
        )
        current_y += element_height + element_spacing
        
        self.labels.append(("Your Name:", (panel_x, current_y)))
        current_y += self.font.get_height() + label_spacing
        
        self.player_name_input = TextInput(
            panel_x, current_y, element_width, element_height
        )
        current_y += element_height + element_spacing
        
        self.labels.append(("Game Type:", (panel_x, current_y)))
        current_y += self.font.get_height() + label_spacing
        
        self.game_dropdown = Dropdown(
            panel_x, current_y, element_width, element_height, self.GAMES, 0
        )
        current_y += element_height + element_spacing
        
        self.labels.append(("Quadrant Configuration:", (panel_x, current_y)))
        current_y += self.font.get_height() + label_spacing
        
        self.quadrant_config_button = Button(
            panel_x, current_y, element_width, 40, 
            "Configure Quadrants", self._open_quadrant_config
        )
        current_y += element_height + element_spacing * 2
        
        self.create_button = Button(
            panel_x, current_y, element_width, 40, 
            "Create Game", self.create_game
        )
        
        # Preview box for quadrants
        preview_size = 200
        self.preview_rect = pygame.Rect(
            panel_x + panel_width + 50,
            self.navbar_height + 100,
            preview_size,
            preview_size
        )
    
    def _open_quadrant_config(self):
        """procédure : ouvre l'écran de configuration des quadrants"""
        from src.windows.screens.game_config.quadrant_config import QuadrantConfigScreen
        self.next_screen = lambda: QuadrantConfigScreen(self)
        self.running = False
        Logger.info("CreateGameScreen", "Opening quadrant configuration screen")
    
    def create_game(self):
        game_name = self.game_name_input.get()
        player_name = self.player_name_input.get()
        selected_index = self.game_dropdown.selected_index
        selected_game = self.GAMES[selected_index]
        
        if not game_name:
            Logger.warning("CreateGameScreen", "Game name cannot be empty")
            return
        
        if not player_name:
            Logger.warning("CreateGameScreen", "Player name cannot be empty")
            return
        
        Logger.info("CreateGameScreen", f"Creating network game '{game_name}' of type '{selected_game}' for player '{player_name}'")
        
        valid_params = self.game_launcher.validate_game_params(
            game_name, "Network", ["Solo", "Bot", "Network"]
        )
        
        if valid_params:
            Logger.info("CreateGameScreen", f"Directly creating and launching game of type '{selected_game}'")
            self.running = False
            
            # retour à l'écran de sélection de mode
            from src.windows.screens.game_selection.mode_selection import ModeSelectionScreen
            self.next_screen = ModeSelectionScreen
            
            # lancer le jeu directement avec les quadrants configurés
            # passer le nom du joueur à start_game au lieu de se connecter séparément
            game_success = self.game_launcher.start_game(
                game_name, selected_game, "Network", self.selected_quadrants, player_name=player_name
            )
            
            if not game_success:
                Logger.warning("CreateGameScreen", "Game exited with errors")
    
    def handle_screen_events(self, event):
        mouse_pos = pygame.mouse.get_pos()
        
        self.game_name_input.handle_event(event, mouse_pos)
        self.player_name_input.handle_event(event, mouse_pos)
        self.game_dropdown.handle_event(event, mouse_pos)
        self.quadrant_config_button.handle_event(event)
        self.create_button.handle_event(event)
    
    def update_screen(self, mouse_pos):
        self.game_name_input.update(16)
        self.player_name_input.update(16)
        self.quadrant_config_button.check_hover(mouse_pos)
        self.create_button.check_hover(mouse_pos)
    
    def draw_screen(self):
        # dessiner les labels
        for text, pos in self.labels:
            text_surface = self.font.render(text, True, (0, 0, 0))
            self.screen.blit(text_surface, pos)
        
        # dessiner les inputs et les boutons
        self.game_name_input.draw(self.screen)
        self.player_name_input.draw(self.screen)
        self.game_dropdown.draw(self.screen)
        self.quadrant_config_button.draw(self.screen)
        self.create_button.draw(self.screen)
        
        # dessiner la prévisualisation des quadrants
        self.draw_quadrant_preview()
    
    def draw_quadrant_preview(self):
        # dessiner le titre de la prévisualisation
        preview_title = self.font.render("Quadrant Preview:", True, (0, 0, 0))
        self.screen.blit(preview_title, (self.preview_rect.x, self.preview_rect.y - 30))
        
        # dessiner le fond de la prévisualisation
        pygame.draw.rect(self.screen, (240, 240, 240), self.preview_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), self.preview_rect, 2)
        
        # dessiner les quadrants
        quadrant_size = self.preview_rect.width // 2
        
        for i in range(4):
            row = i // 2
            col = i % 2
            
            quadrant_rect = pygame.Rect(
                self.preview_rect.x + (col * quadrant_size),
                self.preview_rect.y + (row * quadrant_size),
                quadrant_size,
                quadrant_size
            )
            
            if i < len(self.selected_quadrants) and self.selected_quadrants[i]:
                quadrant_data = self.selected_quadrants[i]
                
                # utiliser la couleur des quadrants si disponible
                if "color" in quadrant_data:
                    color_hex = quadrant_data["color"]
                    fill_color = tuple(int(color_hex[j:j+2], 16) for j in (1, 3, 5))
                    pygame.draw.rect(self.screen, fill_color, quadrant_rect)
                else:
                    pygame.draw.rect(self.screen, (200, 200, 200), quadrant_rect)
                
                # dessiner le nom du quadrant si disponible
                if "name" in quadrant_data:
                    name_font = pygame.font.SysFont('Arial', 12)
                    name_surface = name_font.render(quadrant_data["name"], True, (0, 0, 0))
                    name_rect = name_surface.get_rect(center=quadrant_rect.center)
                    self.screen.blit(name_surface, name_rect)
            else:
                # dessiner le quadrant vide
                pygame.draw.rect(self.screen, (200, 200, 200), quadrant_rect)
            
            # dessiner les lignes de grille
            pygame.draw.rect(self.screen, (0, 0, 0), quadrant_rect, 1) 