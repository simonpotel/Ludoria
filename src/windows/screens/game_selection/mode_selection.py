import pygame
from src.windows.screens.base_screen import BaseScreen
from src.windows.components.image_button import ImageButton
from src.utils.logger import Logger
from src.utils.theme_manager import ThemeManager


class ModeSelectionScreen(BaseScreen):
    def __init__(self):
        super().__init__(title="Ludoria - Mode Selection")
        self.mode_buttons = []
        self.modes = ["Solo", "Bot", "Network"]
        self.theme_manager = ThemeManager()
        self.background = None

    def setup_ui(self):
        button_width = 220*1.5
        button_height = 80*1.5
        button_spacing = 50

        # Essayer de charger l'image de fond du thème actuel
        try:
            theme = self.theme_manager.current_theme
            bg_path = f"assets/{theme}/background.png"
            original_bg = pygame.image.load(bg_path).convert_alpha()
            self.background = pygame.transform.scale(original_bg, (self.width, self.height))
            
            # Ajouter un léger flou/assombrissement pour la lisibilité
            blur_effect = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            blur_effect.fill((0, 0, 0, 120))  # Moins sombre que l'écran de sélection de thème
            self.background.blit(blur_effect, (0, 0))
        except Exception as e:
            Logger.error("ModeSelectionScreen", f"Erreur lors du chargement de l'image de fond: {e}")
            self.background = None

        # calcul de la hauteur totale des boutons et de la position y du premier bouton en fonction de la hauteur de la fenêtre et de la navbar
        total_height = (button_height * len(self.modes)) + (button_spacing *
                                                            # calcul de la hauteur totale des boutons
                                                            (len(self.modes) - 1))
        start_y = (self.content_rect.height - total_height) // 2 + \
            self.navbar_height  # calcul de la position y du premier bouton

        for i, mode in enumerate(self.modes):
            # calcul de la position y du bouton
            y_pos = start_y + (button_height + button_spacing) * i

            button = ImageButton(
                (self.width - button_width) // 2,
                y_pos,
                button_width,
                button_height,
                mode,
                lambda m=mode: self.select_mode(m)
            )
            self.mode_buttons.append(button)

    def select_mode(self, mode):
        Logger.info("ModeSelectionScreen", f"Selected mode: {mode}")
        # imports dynamiques pour avoid l'import de modules inutiles
        if mode == "Solo" or mode == "Bot":
            from src.windows.screens.game_config.game_config import GameConfigScreen
            self.next_screen = lambda: GameConfigScreen(mode)
        elif mode == "Network":
            from src.windows.screens.network.network_options import NetworkOptionsScreen
            self.next_screen = NetworkOptionsScreen

        self.running = False

    def handle_screen_events(self, event):
        for button in self.mode_buttons:
            button.handle_event(event)

    def update_screen(self, mouse_pos):
        for button in self.mode_buttons:
            button.check_hover(mouse_pos)

    def draw_screen(self):
        # Dessiner l'arrière-plan thématique si disponible
        if self.background:
            self.screen.blit(self.background, (0, 0))
        
        # Titre avec style adapté au thème
        title_font = pygame.font.SysFont('Arial', 32, bold=True)
        title_text = "Select Game Mode"
        title_surface = title_font.render(title_text, True, (255, 255, 255))
        title_x = (self.width - title_surface.get_width()) // 2
        title_y = self.navbar_height + 40
        self.screen.blit(title_surface, (title_x, title_y))

        for button in self.mode_buttons:
            button.draw(self.screen)
