import pygame
import os
from src.windows.screens.base_screen import BaseScreen
from src.windows.components.image_button import ImageButton
from src.windows.components.button import Button
from src.utils.logger import Logger
from src.utils.theme_manager import ThemeManager


class ThemeSelectionScreen(BaseScreen):
    """
    classe : écran de sélection du thème visuel de l'application.
    """
    def __init__(self):
        """
        constructeur : initialise l'écran de sélection de thème.
        """
        super().__init__(title="Ludoria - Sélection de Thème")
        self.themes = ["tropique", "grec", "japon", "nordique", "sahara"]
        self.theme_buttons = []
        self.selected_theme = None
        self.current_theme_index = 0
        self.background = None
        self.title_font = None
        self.subtitle_font = None
        self.blurred_backgrounds = {}
        self.left_arrow_btn = None
        self.right_arrow_btn = None
        self.theme_manager = ThemeManager()
        
        # variables pour l'animation de transition
        self.is_transitioning = False
        self.transition_start_time = 0
        self.transition_duration = 300
        self.transition_direction = 0
        self.transition_progress = 0.0
        self.previous_theme_index = 0
        
    def setup_ui(self):
        """
        procédure : configure les éléments d'interface utilisateur.
        """
        self.title_font = pygame.font.SysFont('Arial', 86, bold=True)
        self.subtitle_font = pygame.font.SysFont('Arial', 36, bold=True)
        
        # chargement des images de fond floues pour chaque thème
        for theme in self.themes:
            try:
                bg_path = f"assets/{theme}/background.png"
                original_bg = pygame.image.load(bg_path).convert_alpha()
                
                # redimensionnement de l'image pour l'écran
                scaled_bg = pygame.transform.scale(original_bg, (self.width, self.height))
                
                # création de l'effet de flou
                blur_effect = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                blur_effect.fill((0, 0, 0, 180))  # surface noire semi-transparente
                
                # combinaison de l'image et de l'effet de flou
                scaled_bg.blit(blur_effect, (0, 0))
                self.blurred_backgrounds[theme] = scaled_bg
            except Exception as e:
                Logger.error("ThemeSelectionScreen", f"Erreur lors du chargement de l'image {bg_path}: {e}")
                # image de secours en cas d'échec
                self.blurred_backgrounds[theme] = pygame.Surface((self.width, self.height))
                self.blurred_backgrounds[theme].fill((30, 30, 30))
        
        # création des boutons de thème
        self.create_theme_buttons()
        
        # création des boutons de navigation (flèches)
        arrow_width = 70
        arrow_height = 100
        arrow_y = self.height // 2 + 75
        
        # flèche gauche
        self.left_arrow_btn = Button(
            10,
            arrow_y,
            arrow_width,
            arrow_height,
            "<",
            lambda: self.navigate_themes(-1)
        )
        
        # flèche droite
        self.right_arrow_btn = Button(
            self.width - 10 - arrow_width,
            arrow_y,
            arrow_width,
            arrow_height,
            ">",
            lambda: self.navigate_themes(1)
        )

    def create_theme_buttons(self):
        """
        procédure : crée les boutons pour chaque thème disponible.
        """
        button_width = 550
        button_height = 350
        spacing = 100
        
        # positions pour l'affichage horizontal
        center_x = self.width // 2
        center_y = self.height - 230
        
        self.theme_buttons = []
        
        # indices pour la navigation circulaire
        max_offset = len(self.themes) // 2
        
        for i in range(-max_offset, max_offset + 1):
            # calcul de l'indice dans le tableau circulaire
            theme_index = (self.current_theme_index + i) % len(self.themes)
            theme = self.themes[theme_index]
            
            # position avec décalage (0 au centre)
            x_pos = center_x + (i * (button_width + spacing)) - button_width // 2
            
            # création du bouton sans texte
            button = CustomImageButton(
                x_pos,
                center_y - button_height // 2,
                button_width,
                button_height,
                "",
                lambda t=theme: self.select_theme(t),
                f"assets/{theme}/background.png"
            )
            
            # stockage des métadonnées
            button.theme_name = theme
            button.offset = i
            
            self.theme_buttons.append(button)

    def select_theme(self, theme):
        """
        procédure : sélectionne un thème et navigue vers l'écran suivant.
        
        params:
            theme - le thème sélectionné
        """
        Logger.info("ThemeSelectionScreen", f"Thème sélectionné: {theme}")
        self.selected_theme = theme
        
        # enregistrement du thème dans le gestionnaire
        self.theme_manager.current_theme = theme
        
        # transition vers l'écran suivant
        from src.windows.screens.game_selection.mode_selection import ModeSelectionScreen
        self.next_screen = ModeSelectionScreen
        self.running = False
        
    def settings_action(self):
        """
        procédure : action du bouton paramètres (désactivée dans cet écran).
        """
        Logger.info("ThemeSelectionScreen", "Bouton paramètres ignoré sur l'écran de sélection de thème")
        pass

    def navigate_themes(self, direction):
        """
        procédure : change le thème affiché au centre.
        
        params:
            direction - direction de navigation (-1 pour gauche, 1 pour droite)
        """
        if not self.is_transitioning:
            self.previous_theme_index = self.current_theme_index
            self.current_theme_index = (self.current_theme_index + direction) % len(self.themes)
            self.transition_direction = direction
            self.transition_start_time = pygame.time.get_ticks()
            self.is_transitioning = True

    def handle_screen_events(self, event):
        """
        procédure : gère les événements spécifiques à cet écran.
        
        params:
            event - événement pygame à traiter
        """
        # gestion des touches du clavier
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.navigate_themes(-1)
            elif event.key == pygame.K_RIGHT:
                self.navigate_themes(1)
            elif event.key == pygame.K_RETURN:
                # sélection du thème central avec la touche entrée
                current_theme = self.themes[self.current_theme_index]
                self.select_theme(current_theme)
        
        # gestion des clics de souris
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # priorité aux flèches de navigation
            if self.left_arrow_btn.rect.collidepoint(mouse_pos):
                if self.left_arrow_btn.handle_event(event):
                    return
                    
            if self.right_arrow_btn.rect.collidepoint(mouse_pos):
                if self.right_arrow_btn.handle_event(event):
                    return
            
            # traitement des boutons de thème
            for button in self.theme_buttons:
                if button.offset == 0:  # seul le thème central est sélectionnable
                    button.handle_event(event)
        else:
            # autres types d'événements
            self.left_arrow_btn.handle_event(event)
            self.right_arrow_btn.handle_event(event)
            
            for button in self.theme_buttons:
                if button.offset == 0:
                    button.handle_event(event)

    def update_screen(self, mouse_pos):
        """
        procédure : met à jour l'état des éléments d'interface.
        
        params:
            mouse_pos - position actuelle de la souris
        """
        for button in self.theme_buttons:
            button.check_hover(mouse_pos)
            
        self.left_arrow_btn.check_hover(mouse_pos)
        self.right_arrow_btn.check_hover(mouse_pos)
        
        # Mettre à jour l'animation de transition si elle est active
        if self.is_transitioning:
            # Force un nouveau rendu à chaque frame pendant la transition
            self.needs_render = True
            
            # Si la transition est terminée
            current_time = pygame.time.get_ticks()
            if current_time - self.transition_start_time >= self.transition_duration:
                self.is_transitioning = False
                self.create_theme_buttons()  # Recréer les boutons avec les nouvelles positions

    def draw_screen(self):
        """
        procédure : dessine tous les éléments de l'écran.
        """
        # arrière-plan du thème actuel
        current_theme = self.themes[self.current_theme_index]
        self.screen.blit(self.blurred_backgrounds[current_theme], (0, 0))
        
        # titre LUDORIA
        title_text = "LUDORIA"
        title_surface = self.title_font.render(title_text, True, (255, 255, 255))
        title_x = (self.width - title_surface.get_width()) // 2
        title_y = self.navbar_height + 50
        self.screen.blit(title_surface, (title_x, title_y))
        
        # sous-titre
        subtitle_text = "CHOISISSEZ VOTRE THÈME :"
        subtitle_surface = self.subtitle_font.render(subtitle_text, True, (255, 255, 255))
        subtitle_x = (self.width - subtitle_surface.get_width()) // 2
        subtitle_y = title_y + title_surface.get_height() + 30
        self.screen.blit(subtitle_surface, (subtitle_x, subtitle_y))
        
        # boutons de thème avec transparence variable
        for button in self.theme_buttons:
            # sauvegarde de l'alpha original
            original_alpha = button.bg_image.get_alpha()
            
            # transparence selon la distance au centre
            if button.offset != 0:
                alpha_value = max(100, 255 - (abs(button.offset) * 100))
                button.bg_image.set_alpha(alpha_value)
            else:
                button.bg_image.set_alpha(255)  # pleine visibilité au centre
                
            # affichage du bouton
            button.draw(self.screen)
            
            # réinitialisation de l'alpha
            button.bg_image.set_alpha(original_alpha)
            
            # ajout du nom du thème
            theme_name = button.theme_name.capitalize()
            name_font = pygame.font.SysFont('Arial', 30, bold=True)
            name_surface = name_font.render(theme_name, True, (255, 255, 255))
            name_x = button.rect.centerx - name_surface.get_width() // 2
            name_y = button.rect.bottom + 10
            
            # transparence du texte similaire au bouton
            if button.offset != 0:
                alpha_surface = pygame.Surface((name_surface.get_width(), name_surface.get_height()), pygame.SRCALPHA)
                alpha_value = max(100, 255 - (abs(button.offset) * 100))
                alpha_surface.fill((255, 255, 255, alpha_value))
                name_surface.blit(alpha_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                
            self.screen.blit(name_surface, (name_x, name_y))
        
        # flèches de navigation
        self.left_arrow_btn.draw(self.screen)
        self.right_arrow_btn.draw(self.screen)
        
        # Animation de transition entre les thèmes
        if self.is_transitioning:
            self.animate_theme_transition()

    def animate_theme_transition(self):
        """
        procédure : gère l'animation de transition entre les thèmes.
        """
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.transition_start_time
        
        if elapsed_time < self.transition_duration:
            # calcul de la progression de l'animation
            progress = elapsed_time / self.transition_duration
            # fonction d'accélération pour un mouvement plus naturel
            eased_progress = progress * progress * (3 - 2 * progress)
            
            # transition du fond d'écran
            prev_theme = self.themes[self.previous_theme_index]
            current_theme = self.themes[self.current_theme_index]
            
            # afficher l'ancien fond avec une opacité décroissante
            self.screen.blit(self.blurred_backgrounds[prev_theme], (0, 0))
            
            # créer une surface semi-transparente pour le nouveau fond
            new_bg = self.blurred_backgrounds[current_theme].copy()
            new_bg.set_alpha(int(255 * eased_progress))
            self.screen.blit(new_bg, (0, 0))
            
            # afficher le titre LUDORIA
            title_text = "LUDORIA"
            title_surface = self.title_font.render(title_text, True, (255, 255, 255))
            title_x = (self.width - title_surface.get_width()) // 2
            title_y = self.navbar_height + 50
            self.screen.blit(title_surface, (title_x, title_y))
            
            # afficher le sous-titre
            subtitle_text = "CHOISISSEZ VOTRE THÈME :"
            subtitle_surface = self.subtitle_font.render(subtitle_text, True, (255, 255, 255))
            subtitle_x = (self.width - subtitle_surface.get_width()) // 2
            subtitle_y = title_y + title_surface.get_height() + 30
            self.screen.blit(subtitle_surface, (subtitle_x, subtitle_y))
            
            # animation des boutons de thème
            button_width = 550
            button_height = 350
            spacing = 100
            center_x = self.width // 2
            center_y = self.height - 230
            
            # calculer le décalage pour l'animation de glissement
            slide_offset = int(spacing * self.transition_direction * (1 - eased_progress))
            
            for button in self.theme_buttons:
                # calculer la position animée
                animated_offset = button.offset - self.transition_direction * eased_progress
                x_pos = center_x + (animated_offset * (button_width + spacing)) - button_width // 2
                
                # définir la nouvelle position du bouton pour l'animation
                button.rect.x = int(x_pos + slide_offset)
                
                # ajuster l'opacité du bouton en fonction de sa distance au centre
                distance = abs(animated_offset)
                if distance < 0.1:  # presque au centre
                    alpha = 255
                else:
                    alpha = max(100, int(255 - (distance * 100)))
                
                button.bg_image.set_alpha(alpha)
                
                # afficher le bouton à sa position temporaire
                button.draw(self.screen)
                
                # afficher le nom du thème sous le bouton
                theme_name = button.theme_name.capitalize()
                name_font = pygame.font.SysFont('Arial', 30, bold=True)
                name_surface = name_font.render(theme_name, True, (255, 255, 255))
                name_x = button.rect.centerx - name_surface.get_width() // 2
                name_y = button.rect.bottom + 10
                
                # transparence du texte similaire au bouton
                alpha_surface = pygame.Surface((name_surface.get_width(), name_surface.get_height()), pygame.SRCALPHA)
                alpha_surface.fill((255, 255, 255, alpha))
                name_surface.blit(alpha_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                
                self.screen.blit(name_surface, (name_x, name_y))
            
            # toujours afficher les flèches de navigation
            self.left_arrow_btn.draw(self.screen)
            self.right_arrow_btn.draw(self.screen)
        else:
            # fin de la transition
            self.is_transitioning = False
            self.transition_progress = 0.0
            self.create_theme_buttons()  # recréer les boutons avec leurs positions finales

class CustomImageButton(ImageButton):
    """
    classe : version personnalisée du bouton d'image avec métadonnées supplémentaires.
    """
    def __init__(self, x, y, width, height, text, action=None, bg_image_path="assets/cta_background.png"):
        """
        constructeur : initialise un bouton image personnalisé.
        
        params:
            x, y - coordonnées du coin supérieur gauche
            width, height - dimensions du bouton
            text - texte affiché sur le bouton
            action - fonction à appeler lors du clic
            bg_image_path - chemin de l'image d'arrière-plan
        """
        super().__init__(x, y, width, height, text, action, bg_image_path)
        self.theme_name = ""
        self.offset = 0