import pygame
from src.utils.logger import Logger
from src.windows.render.constants import RenderConstants
from src.windows.components.button import Button

class InfoBarHandler:
    """
    classe : gestionnaire de la barre d'informations.
    
    gère le rendu et les mises à jour de la barre d'informations en haut de l'écran.
    """
    
    def __init__(self, window_width):
        """
        constructeur : initialise le gestionnaire de barre d'informations.
        
        params:
            window_width: largeur de la fenêtre en pixels
        """
        self.window_width = window_width
        self.info_text = ""
        
        # surface pour la barre d'info (avec transparence)
        self.info_surface = pygame.Surface((window_width, RenderConstants.INFO_BAR_HEIGHT), 
                                          pygame.SRCALPHA)
        
        self.pause_button = Button(
            self.window_width - 120, 10, 100, 30, "Pause", None
        )
        
        Logger.info("InfoBarHandler", "Info bar handler initialized")
        
    def edit_info_label(self, text):
        """
        procédure : met à jour le texte affiché dans la barre d'information.
        
        params:
            text: nouveau texte à afficher
            
        retour:
            bool: True si le texte a changé, False sinon
        """
        if self.info_text != text:
            self.info_text = text
            Logger.info("InfoBarHandler", f"Update info: '{text}'")
            return True
        return False
            
    def render(self, screen, fonts, game):
        """
        procédure : dessine la barre d'information semi-transparente.
        
        params:
            screen: surface d'affichage principale
            fonts: dictionnaire contenant les polices
            game: instance du jeu
        """
        # effacement avec transparence totale
        self.info_surface.fill((0, 0, 0, 0))
        
        # dessine un rectangle semi-transparent
        pygame.draw.rect(self.info_surface, RenderConstants.INFO_OVERLAY_COLOR, self.info_surface.get_rect())
        
        # texte principal centré
        text_surface = fonts['main'].render(self.info_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.window_width // 2, RenderConstants.INFO_BAR_HEIGHT // 2))
        self.info_surface.blit(text_surface, text_rect)
        
        # statut réseau (si applicable)
        if hasattr(game, 'is_network_game') and game.is_network_game:
            self._render_network_status(fonts, game)
        
        # Mise à jour du survol du bouton pause
        mouse_pos = pygame.mouse.get_pos()
        self.pause_button.check_hover(mouse_pos)
        
        self.pause_button.draw(self.info_surface)
        
        # affichage sur l'écran principal
        screen.blit(self.info_surface, (0, 0))
        
    def _render_network_status(self, fonts, game):
        """
        procédure : dessine le statut de connexion réseau dans la barre d'info.
        
        params:
            fonts: dictionnaire contenant les polices
            game: instance du jeu
        """
        if not hasattr(game, 'status_message') or not game.status_message:
            return
            
        # utilise la couleur définie par le jeu ou jaune par défaut
        color = getattr(game, 'status_color', (255, 255, 0))
        
        # dessine en bas à droite de la barre d'info
        text = fonts['status'].render(game.status_message, True, color)
        rect = text.get_rect(bottomright=(self.window_width - 15, RenderConstants.INFO_BAR_HEIGHT - 5))
        self.info_surface.blit(text, rect) 

    def set_pause_callback(self, callback):
        self.pause_button.action = callback

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        self.pause_button.check_hover(mouse_pos)
        self.pause_button.handle_event(event) 