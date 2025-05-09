import pygame
from src.utils.logger import Logger
from src.windows.render.constants import RenderConstants
from src.windows.render.image_loader import ImageLoader
from src.windows.render.board_handler import BoardHandler
from src.windows.render.info_bar_handler import InfoBarHandler
from src.windows.render.chat_handler import ChatHandler
from src.windows.components.button import Button
import sys

class Render:
    """
    classe : gestionnaire d'affichage graphique du jeu.
    
    utilise pygame pour le rendu et PIL pour traiter les images.
    gère le chargement des ressources, l'affichage du plateau, les animations
    et la détection des clics.
    """
    
    def __init__(self, game, canvas_size=600, window_width=1280, window_height=720):
        """
        procédure : initialise le moteur de rendu.
        
        params:
            game: instance du jeu à afficher
            canvas_size: taille logique du plateau de jeu (sans les marges)
            window_width: largeur de la fenêtre en pixels
            window_height: hauteur de la fenêtre en pixels
        """
        Logger.info("Render", "Render engine initialization")
        # données de base
        self.game = game
        self.canvas_size = canvas_size
        self.window_width = window_width
        self.window_height = window_height
        
        # dimensions calculées
        self.board_size = len(game.board.board) if game.board and game.board.board else 10
        self.cell_size = self.canvas_size // self.board_size
        
        # état interne
        self.running = True
        self.needs_render = True
        
        # initialisation pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption(f"Ludoria: {self.game.game_save}")
        self.clock = pygame.time.Clock()
        
        # chargement des ressources
        self._load_font()
        self._load_images()
        
        # initialisation des gestionnaires
        self.info_bar_handler = InfoBarHandler(self.window_width)
        self.board_handler = BoardHandler(self.game, self.canvas_size, self.cell_size, 
                                        self.images, self.player_shadows)
        
        # calcule la position du plateau
        is_network_game = hasattr(self.game, 'is_network_game') and self.game.is_network_game
        self.board_x, self.board_y = self.board_handler.calculate_board_position(
            self.window_width, self.window_height, is_network_game)
        
        # initialisation du chat en cas de jeu réseau
        self.chat_handler = None
        if is_network_game:
            self.chat_handler = ChatHandler(self.window_height)
        
        # premier rendu
        self.render_board()
        Logger.success("Render", "Render engine initialized")

    def _load_images(self):
        """
        procédure : charge toutes les images du jeu.
        """
        image_loader = ImageLoader(self.cell_size, self.window_width, self.window_height)
        self.images, self.player_shadows, self.background = image_loader.load_all_images()

    def _load_font(self):
        """
        procédure : charge la police de caractères personnalisée.
        """
        font_path = "assets/fonts/BlackHanSans-Regular.ttf"
        self.fonts = {
            'main': pygame.font.Font(font_path, 24),
            'status': pygame.font.Font(font_path, 18),
            'chat': pygame.font.Font(font_path, 14)
        }
        Logger.info("Render", f"Font loaded: {font_path}")

    def edit_info_label(self, text):
        """
        procédure : met à jour le texte affiché dans la barre d'information.
        
        params:
            text: nouveau texte à afficher
        """
        if self.info_bar_handler.edit_info_label(text):
            self.needs_render = True

    def show_end_popup(self, winner_text):
        """
        Active la pop-up de fin de partie avec le texte du gagnant.
        """
        self.end_popup_active = True
        self.end_popup_text = winner_text
        self.end_popup_buttons = []
        popup_width, popup_height = 500, 260
        popup_x = (self.window_width - popup_width) // 2
        popup_y = (self.window_height - popup_height) // 2
        button_width, button_height = 260, 50
        button_spacing = 30
        # Play Again
        play_again_btn = Button(
            popup_x + (popup_width - button_width) // 2,
            popup_y + 90,
            button_width,
            button_height,
            "PLAY AGAIN",
            action=self._popup_play_again
        )
        # Quitter
        quit_btn = Button(
            popup_x + (popup_width - button_width) // 2,
            popup_y + 90 + button_height + button_spacing,
            button_width,
            button_height,
            "QUITTER",
            action=self._popup_quit
        )
        self.end_popup_buttons = [play_again_btn, quit_btn]
        self.needs_render = True

    def _popup_play_again(self):
        self.running = False
        self.end_popup_action = "play_again"

    def _popup_quit(self):
        self.running = False
        pygame.quit()
        sys.exit()

    def render_board(self):
        """
        procédure : dessine l'état complet du jeu (fond, info, plateau).
        """
        # 1. arrière-plan flouté sur tout l'écran
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill((30, 30, 30))  # fallback si pas d'image
        
        # 2. barre d'info semi-transparente
        self.info_bar_handler.render(self.screen, self.fonts, self.game)
        
        # 3. chat si en mode réseau
        if self.chat_handler:
            self.chat_handler.render(self.screen, self.fonts, self.game)
        
        # 4. plateau de jeu avec marges
        self.board_handler.render(self.screen, self.board_x, self.board_y)
        
        # 5. mise à jour de l'écran
        pygame.display.flip()
        Logger.board("Render", "Rendering complete")
        # Affichage de la pop-up de fin de partie si active
        if hasattr(self, 'end_popup_active') and self.end_popup_active:
            self._draw_end_popup()

    def _draw_end_popup(self):
        popup_width, popup_height = 500, 260
        popup_x = (self.window_width - popup_width) // 2
        popup_y = (self.window_height - popup_height) // 2
        # fond semi-transparent
        s = pygame.Surface((popup_width, popup_height), pygame.SRCALPHA)
        s.fill((240, 240, 240, 210))
        self.screen.blit(s, (popup_x, popup_y))
        # texte gagnant centré
        font = self.fonts['main']
        text_surface = font.render(self.end_popup_text, True, (40, 40, 40))
        text_rect = text_surface.get_rect(center=(self.window_width//2, popup_y + 50))
        self.screen.blit(text_surface, text_rect)
        # boutons
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.end_popup_buttons:
            btn.check_hover(mouse_pos)
            btn.draw(self.screen)
        pygame.display.flip()

    def handle_click(self, pos):
        """
        procédure : traite un clic de souris et le transmet au jeu si pertinent.
        
        params:
            pos: tuple (x, y) des coordonnées du clic dans la fenêtre
        """
        if hasattr(self, 'end_popup_active') and self.end_popup_active:
            for btn in self.end_popup_buttons:
                btn.check_hover(pos)
                fake_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': pos, 'button': 1})
                if btn.handle_event(fake_event):
                    return
            return
        
        # 1. vérifier si le clic est sur le chat
        if self.chat_handler and self.chat_handler.handle_click(pos, self.game):
            self.needs_render = True
            return
        
        # 2. vérifier si le clic est sur le plateau
        board_coords = self.board_handler.handle_click(pos, self.board_x, self.board_y)
        if board_coords:
            row, col = board_coords
            # vérifie si le joueur peut jouer
            if hasattr(self.game, 'can_play') and self.game.can_play():
                # transmet le clic à la logique du jeu
                self.game.on_click(row, col)
                # note: on_click met à jour l'affichage via edit_info_label

    def run_game_loop(self):
        """
        procédure : exécute la boucle principale du jeu.
        """
        Logger.info("Render", "Starting game loop")
        self.running = True
        
        while self.running:
            # gestion des événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # clic gauche
                        self.handle_click(event.pos)
                elif event.type == pygame.USEREVENT and hasattr(self.game, 'handle_events'):
                    self.game.handle_events(event)
                elif hasattr(self.game, 'handle_events'):
                    # gestion des événements clavier pour le chat
                    if not self.game.handle_events(event):
                        self.needs_render = True
            
            # rendu si nécessaire
            if self.needs_render:
                self.render_board()
                self.needs_render = False
            
            # limite le framerate
            self.clock.tick(30)
        
        Logger.info("Render", "Game loop finished") 