import pygame
from src.windows.screens.base_screen import BaseScreen
from src.windows.components.image_button import ImageButton
from src.utils.theme_manager import ThemeManager
from src.utils.logger import Logger

class RulesScreen(BaseScreen):
    def __init__(self, game_name, rules_text):
        super().__init__(title=f"Ludoria - Règles de {game_name}")
        self.game_name = game_name
        self.rules_text = rules_text
        self.back_button = None
        self.rendered_rules = []

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
            "Retour",
            self.go_back,
            bg_image_path=back_button_img_path,
            font=button_font
        )

        # préparation du texte des règles pour le rendu avec le retour à la ligne
        rules_font = self.font_manager.get_font(20)
        max_text_width = self.width - 40 # espace de 20px sur chaque côté
        line_spacing = 5
        start_x = 20
        start_y = 80 # en dessous de la zone du titre
        current_y = start_y

        self.rendered_rules.append((rules_font.render(f"Règles de {self.game_name}:", True, (255, 255, 255)), (start_x, current_y)))
        current_y += self.rendered_rules[-1][0].get_height() + line_spacing * 2

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

        # dessiner le titre
        title_font = self.font_manager.get_font(50)
        title_surface = title_font.render(self.title, True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(self.width // 2, 40))
        self.screen.blit(title_surface, title_rect)

        # dessiner le texte des règles
        for text_surface, pos in self.rendered_rules:
            self.screen.blit(text_surface, pos)

        # dessiner le bouton retour
        self.back_button.draw(self.screen)

    def go_back(self):
        Logger.info("RulesScreen", "Going back to mode selection")
        from src.windows.screens.game_selection.mode_selection import ModeSelectionScreen
        self.next_screen = ModeSelectionScreen
        self.running = False 