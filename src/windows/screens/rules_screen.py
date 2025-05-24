import pygame
from src.windows.screens.base_screen import BaseScreen
from src.windows.components.image_button import ImageButton
from src.utils.theme_manager import ThemeManager
from src.utils.logger import Logger

class RulesScreen(BaseScreen):
    def __init__(self, game_name, rules_text):
        super().__init__(title=f"Ludoria - Rules of {game_name}")
        self.game_name = game_name
        self.rules_text = rules_text
        self.back_button = None
        self.rendered_rules = []
        self.rules_title_surface = None
        self.rules_title_rect = None

    def setup_ui(self):
        button_font = self.font_manager.get_font(30)
        back_button_width = 150
        back_button_height = 50
        back_button_img_path = "assets/Basic_GUI_Bundle/ButtonsText/ButtonText_Large_GreyOutline_Square.png"

        self.back_button = ImageButton(
            20, # position x
            self.height - back_button_height - 20, # position y
            back_button_width,
            back_button_height,
            "Back",
            self.go_back,
            bg_image_path=back_button_img_path,
            font=button_font
        )

        # font pour le texte des règles
        rules_font_size = 20
        rules_title_font_size = 30
        try:
            rules_font = pygame.font.SysFont('Arial', rules_font_size)
            rules_title_font = pygame.font.SysFont('Arial', rules_title_font_size)
        except Exception as e:
            Logger.error(f"Error loading Arial system font: {e}. Falling back to default.")
            # font par défaut si Arial n'est pas disponible
            rules_font = self.font_manager.get_font(rules_font_size)
            rules_title_font = self.font_manager.get_font(rules_title_font_size)

        max_text_width = self.width - 40 # espace de 20px sur chaque côté
        line_spacing = 5
        start_x = 20
        start_y = 80 # en dessous de la zone du titre
        current_y = start_y

        # titre de l'écran des règles avec Arial
        self.rules_title_surface = rules_title_font.render(f"Règles de {self.game_name}:", True, (255, 255, 255))
        self.rules_title_rect = self.rules_title_surface.get_rect(topleft=(start_x, current_y))
        current_y += self.rules_title_rect.height + line_spacing * 2

        for line in self.rules_text:
            words = line.split(' ')
            current_line = ''
            for word in words:
                test_line = current_line + word + ' '
                test_surface = rules_font.render(test_line, True, (255, 255, 255))
                if test_surface.get_width() < max_text_width:
                    current_line = test_line
                else:
                    self.rendered_rules.append((rules_font.render(current_line.strip(), True, (255, 255, 255)), (start_x + 10, current_y)))
                    current_y += self.rendered_rules[-1][0].get_height() + line_spacing
                    current_line = word + ' '
            if current_line.strip():
                 self.rendered_rules.append((rules_font.render(current_line.strip(), True, (255, 255, 255)), (start_x + 10, current_y)))
                 current_y += self.rendered_rules[-1][0].get_height() + line_spacing

    def handle_screen_events(self, event):
        self.back_button.handle_event(event)

    def update_screen(self, mouse_pos):
        self.back_button.check_hover(mouse_pos)

    def draw_screen(self):
        # dessiner le fond (on peut ajouter un fond spécifique plus tard si nécessaire)
        self.screen.fill((50, 50, 50))

        screen_title_font = self.font_manager.get_font(50)
        screen_title_surface = screen_title_font.render(self.title, True, (255, 255, 255))
        screen_title_rect = screen_title_surface.get_rect(center=(self.width // 2, 40))
        self.screen.blit(screen_title_surface, screen_title_rect)

        # titre et texte des règles avec Arial
        if self.rules_title_surface and self.rules_title_rect:
            self.screen.blit(self.rules_title_surface, self.rules_title_rect)

        for text_surface, pos in self.rendered_rules:
            self.screen.blit(text_surface, pos)

        # dessiner le bouton retour
        self.back_button.draw(self.screen)

    def go_back(self):
        Logger.info("RulesScreen", "Going back to mode selection")
        from src.windows.screens.game_selection.mode_selection import ModeSelectionScreen
        self.next_screen = ModeSelectionScreen
        self.running = False 