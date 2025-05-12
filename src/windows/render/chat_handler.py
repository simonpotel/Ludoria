import pygame
from src.utils.logger import Logger
from src.windows.render.constants import RenderConstants

class ChatHandler:
    """
    classe : gestionnaire de chat pour les parties en réseau.
    
    gère l'affichage et l'interaction avec l'interface de chat.
    """
    
    def __init__(self, window_height):
        """
        constructeur : initialise le gestionnaire de chat.
        
        params:
            window_height: hauteur de la fenêtre en pixels
        """
        # hauteur du chat = hauteur de la fenêtre moins la barre d'info
        chat_height = window_height - RenderConstants.INFO_BAR_HEIGHT - RenderConstants.CHAT_MARGIN * 2
        
        # crée la surface avec transparence
        self.chat_surface = pygame.Surface((RenderConstants.CHAT_WIDTH, chat_height), pygame.SRCALPHA)
        
        # position du chat (coin supérieur gauche)
        self.chat_x = RenderConstants.CHAT_MARGIN
        self.chat_y = RenderConstants.INFO_BAR_HEIGHT + RenderConstants.CHAT_MARGIN
        
        Logger.info("ChatHandler", "Chat surface configured")
    
    def render(self, screen, fonts, game):
        """
        procédure : dessine l'interface de chat.
        
        params:
            screen: surface d'affichage principale
            fonts: dictionnaire contenant les polices
            game: instance du jeu
        """
        if not self.chat_surface or not hasattr(game, 'chat_messages'):
            return
            
        self.chat_surface.fill((0, 0, 0, 0))  # remplit la surface avec transparence
        
        chat_bg_rect = pygame.Rect(0, 0, RenderConstants.CHAT_WIDTH, self.chat_surface.get_height())  # rectangle de la fenêtre
        pygame.draw.rect(self.chat_surface, RenderConstants.CHAT_BG_COLOR, chat_bg_rect, 0, 10)  # dessine le rectangle
        
        title = fonts['status'].render("CHAT", True, RenderConstants.CHAT_TEXT_COLOR)  # titre de la fenêtre
        title_rect = title.get_rect(midtop=(RenderConstants.CHAT_WIDTH // 2, 5))  # position du titre
        self.chat_surface.blit(title, title_rect)  # dessine le titre
        
        if hasattr(game, 'chat_messages') and game.chat_messages:
            self._render_messages(fonts, game)
        
        # dessine l'input
        self._render_input_field(fonts, game)
        
        # affiche la surface complète
        screen.blit(self.chat_surface, (self.chat_x, self.chat_y))
        
    def _render_messages(self, fonts, game):
        """
        procédure : dessine les messages du chat.
        
        params:
            fonts: dictionnaire contenant les polices
            game: instance du jeu
        """
        chat_font = fonts['chat']
        
        # calcule la hauteur disponible pour les messages
        chat_surface_total_height = self.chat_surface.get_height()  # hauteur de la fenêtre
        chat_input_field_height = RenderConstants.CHAT_INPUT_HEIGHT  # hauteur du champ de saisie 
        bottom_area_reserved_for_input = chat_input_field_height + 5  # espace pour le champ de saisie
        top_area_reserved_for_title_and_padding = 30  # espace pour le titre et les marges
        available_height_for_message_text = chat_surface_total_height - (
            bottom_area_reserved_for_input + top_area_reserved_for_title_and_padding
        )  # hauteur disponible pour les messages
        single_chat_line_height = chat_font.get_linesize()  # hauteur d'une ligne de texte 
        
        if single_chat_line_height > 0 and available_height_for_message_text > 0:
            theoretical_max_lines = available_height_for_message_text // single_chat_line_height
            num_lines_to_try_fit = max(1, theoretical_max_lines)  # nombre de lignes à essayer de fitter
        else:
            num_lines_to_try_fit = 0  # si pas de hauteur disponible
        
        if num_lines_to_try_fit > 0:
            num_recent_messages_to_fetch = num_lines_to_try_fit  # nombre de messages à afficher
            messages_to_display = game.chat_messages[-num_recent_messages_to_fetch:]  # messages à afficher
        else:
            messages_to_display = []  # si pas de hauteur disponible

        original_messages_height_variable = self.chat_surface.get_height() - RenderConstants.CHAT_INPUT_HEIGHT - 20  # hauteur de la fenêtre
        y_pos = original_messages_height_variable - 5  # position initiale
        
        for msg in reversed(messages_to_display):  # reverse pour afficher les derniers messages en premier
            wrapped_lines = self._wrap_text(msg, RenderConstants.CHAT_WIDTH - 20, chat_font)  # wrap le texte
            
            for line in reversed(wrapped_lines):  # reverse pour afficher les lignes en premier
                text = chat_font.render(line, True, RenderConstants.CHAT_TEXT_COLOR)  # texte
                text_height = text.get_height()  # hauteur du texte
                
                if y_pos - text_height < 30:  # si la ligne est en dehors de la zone visible
                    break 
                    
                self.chat_surface.blit(text, (10, y_pos - text_height))  # dessine la ligne
                y_pos -= text_height + 2  # espace entre les lignes
            else: 
                y_pos -= 5 
                if y_pos < 30:  # si la ligne est en dehors de la zone visible
                    break
                continue 
            break
            
    def _render_input_field(self, fonts, game):
        """
        procédure : dessine le champ de saisie du chat.
        
        params:
            fonts: dictionnaire contenant les polices
            game: instance du jeu
        """
        input_rect = pygame.Rect(5, self.chat_surface.get_height() - RenderConstants.CHAT_INPUT_HEIGHT - 5, 
                                RenderConstants.CHAT_WIDTH - 10, RenderConstants.CHAT_INPUT_HEIGHT)
        
        # couleur différente si actif
        input_color = RenderConstants.CHAT_INPUT_ACTIVE_COLOR if hasattr(game, 'chat_active') and game.chat_active else RenderConstants.CHAT_INPUT_COLOR
        
        pygame.draw.rect(self.chat_surface, input_color, input_rect, 0, 5)  # dessine le rectangle
        
        # texte d'invite ou contenu de l'input
        input_text = game.chat_input if hasattr(game, 'chat_input') and game.chat_input else "..."
        
        available_width_for_text = input_rect.width - 10  # space avec padding de 5px de chaque côté
        ellipsis_chars = "..."

        full_text_width = fonts['chat'].size(input_text)[0]

        # si le texte est trop long, on essaie d'afficher la fin avec "..." au début.
        if full_text_width <= available_width_for_text:
            visible_text = input_text
        else:
            visible_text = ellipsis_chars
            for num_chars_in_suffix in range(1, len(input_text) + 1): 
                current_suffix = input_text[-num_chars_in_suffix:] 
                text_to_measure = ellipsis_chars + current_suffix 
                if fonts['chat'].size(text_to_measure)[0] <= available_width_for_text:
                    visible_text = text_to_measure
                else:
                    break 
            if visible_text == ellipsis_chars and fonts['chat'].size(ellipsis_chars)[0] > available_width_for_text:
                visible_text = ""
            
        # affiche le texte
        text_color = RenderConstants.CHAT_TEXT_COLOR if game.chat_active else (180, 180, 180)
        text = fonts['chat'].render(visible_text, True, text_color)
        text_rect = text.get_rect(midleft=(input_rect.left + 5, input_rect.centery))  # position du texte
        self.chat_surface.blit(text, text_rect)  # dessine le texte
    
    def _wrap_text(self, text, max_width, font):
        """
        fonction : divise un texte en lignes qui tiennent dans la largeur spécifiée.
        gère également les mots plus longs que la largeur maximale.
        
        params:
            text: texte à diviser
            max_width: largeur maximale en pixels
            font: police utilisée pour le rendu
            
        retour:
            liste des lignes de texte
        """
        lines = []
        if not text or max_width <= 0:
            return []

        words = text.split(' ')
        current_line = ""
        
        for word in words:
            # vérifie si le mot lui-même est trop long
            if font.size(word)[0] > max_width:
                if current_line:
                    lines.append(current_line)
                    current_line = ""
                
                part = ""
                for char in word:
                    test_part = part + char
                    if font.size(test_part)[0] <= max_width:
                        part = test_part
                    else:
                        lines.append(part)
                        part = char
                
                if part:
                    current_line = part
                continue
            
            if not current_line:
                current_line = word
            else:
                test_line = current_line + ' ' + word
                if font.size(test_line)[0] <= max_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
        
        if current_line:
            lines.append(current_line)
            
        return lines
        
    def handle_click(self, pos, game):
        """
        fonction : traite un clic sur l'interface de chat.
        
        params:
            pos: position du clic (x, y)
            game: instance du jeu
            
        retour:
            bool: True si le clic a été traité, False sinon
        """
        x, y = pos
        
        # vérifie si le clic est dans la zone de chat
        if self.chat_x <= x < self.chat_x + RenderConstants.CHAT_WIDTH and self.chat_y <= y < self.chat_y + self.chat_surface.get_height():
            # clic dans la zone input?
            input_rect = pygame.Rect(self.chat_x + 5, 
                                    self.chat_y + self.chat_surface.get_height() - RenderConstants.CHAT_INPUT_HEIGHT - 5, 
                                    RenderConstants.CHAT_WIDTH - 10, 
                                    RenderConstants.CHAT_INPUT_HEIGHT)
            if input_rect.collidepoint(x, y):
                # active l'input du chat
                game.chat_active = True
                return True
            return True  # clic traité même si pas sur l'input
            
        return False  # clic en dehors du chat 