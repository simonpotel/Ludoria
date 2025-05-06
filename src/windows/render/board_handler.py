import pygame
from src.utils.logger import Logger
from src.windows.render.constants import RenderConstants
from src.windows.render.player_handler import PlayerHandler

class BoardHandler:
    """
    classe : gestionnaire du plateau de jeu.
    
    gère le rendu et les interactions avec le plateau de jeu.
    """
    
    def __init__(self, game, canvas_size, cell_size, images, player_shadows):
        """
        constructeur : initialise le gestionnaire de plateau.
        
        params:
            game: instance du jeu
            canvas_size: taille logique du plateau
            cell_size: taille d'une cellule en pixels
            images: dictionnaire contenant les images
            player_shadows: dictionnaire contenant les ombres des joueurs
        """
        self.game = game
        self.canvas_size = canvas_size
        self.cell_size = cell_size
        self.images = images
        self.board_size = len(game.board.board) if game.board and game.board.board else 10
        self.board_surface_size = canvas_size + 2 * RenderConstants.BOARD_PADDING
        
        # création de la surface du plateau
        self.board_surface = pygame.Surface((self.board_surface_size, self.board_surface_size))
        
        # gestionnaire des joueurs
        self.player_handler = PlayerHandler(player_shadows, images)
        
        Logger.info("BoardHandler", "Board handler initialized")
        
    def calculate_board_position(self, window_width, window_height, is_network_game=False):
        """
        fonction : calcule la position du plateau dans la fenêtre.
        
        params:
            window_width: largeur de la fenêtre
            window_height: hauteur de la fenêtre
            is_network_game: indique si c'est une partie réseau (pour décaler le plateau)
            
        retour:
            tuple (x, y): position du plateau
        """
        # position du plateau centré dans la fenêtre
        board_x = (window_width - self.board_surface_size) // 2
        if is_network_game:
            # décale le plateau vers la droite pour faire place au chat
            board_x = RenderConstants.CHAT_WIDTH + RenderConstants.CHAT_MARGIN * 2 + (
                window_width - RenderConstants.CHAT_WIDTH - self.board_surface_size) // 2
        
        board_y = RenderConstants.INFO_BAR_HEIGHT + (
            window_height - RenderConstants.INFO_BAR_HEIGHT - self.board_surface_size) // 2
            
        return board_x, board_y
        
    def render(self, screen, board_x, board_y):
        """
        procédure : dessine le plateau de jeu avec ses marges.
        
        params:
            screen: surface d'affichage principale
            board_x: position x du plateau
            board_y: position y du plateau
        """
        # fond gris pour les marges
        self.board_surface.fill(RenderConstants.BOARD_BG_COLOR)
        
        # dessine toutes les cellules du plateau
        for row_i, row in enumerate(self.game.board.board):
            for col_i, cell in enumerate(row):
                # calcule la position avec décalage dû aux marges
                x = RenderConstants.BOARD_PADDING + col_i * self.cell_size
                y = RenderConstants.BOARD_PADDING + row_i * self.cell_size
                self._draw_cell(row_i, col_i, cell, x, y)
        
        # affiche le plateau complet sur l'écran
        screen.blit(self.board_surface, (board_x, board_y))
        
    def _draw_cell(self, row, col, cell, x, y):
        """
        procédure : dessine une cellule individuelle et son contenu.
        
        params:
            row, col: coordonnées logiques de la cellule
            cell: données de la cellule (joueur, type_terrain)
            x, y: position en pixels où dessiner la cellule
        """
        cell_rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
        
        # 1. fond de la cellule (terrain)
        terrain_id = cell[1]
        image_key = f"cell_{terrain_id}"
        
        if image_key in self.images:
            # utilise l'image chargée
            self.board_surface.blit(self.images[image_key], cell_rect.topleft)
        else:
            color = RenderConstants.QUADRANT_COLORS.get(terrain_id, (128, 128, 128))
            pygame.draw.rect(self.board_surface, color, cell_rect)
        
        # 2. joueur (avec ombre) si présent
        self.player_handler.draw_player(self.board_surface, cell, cell_rect)
        
        # 3. cadre de sélection si sélectionné
        if hasattr(self.game, 'selected_piece') and self.game.selected_piece == (row, col):
            pygame.draw.rect(self.board_surface, RenderConstants.SELECTION_COLOR, cell_rect, 
                            RenderConstants.SELECTION_WIDTH)
            
    def handle_click(self, pos, board_x, board_y):
        """
        fonction : traite un clic sur le plateau et le convertit en coordonnées logiques.
        
        params:
            pos: position (x, y) du clic
            board_x: position x du plateau
            board_y: position y du plateau
            
        retour:
            tuple (row, col) ou None si le clic est en dehors du plateau
        """
        x, y = pos
        
        # vérification rapide si le clic est sur le plateau
        if not (board_x <= x < board_x + self.board_surface_size and
                board_y <= y < board_y + self.board_surface_size):
            return None  # clic en dehors du plateau
            
        # conversion en coordonnées relatives au plateau
        board_x_rel = x - board_x - RenderConstants.BOARD_PADDING
        board_y_rel = y - board_y - RenderConstants.BOARD_PADDING
        
        # vérifie si le clic est sur une cellule (pas sur la marge)
        if not (0 <= board_x_rel < self.canvas_size and 0 <= board_y_rel < self.canvas_size):
            return None  # clic sur la marge
            
        # calcule les coordonnées logiques de la cellule
        row = board_y_rel // self.cell_size
        col = board_x_rel // self.cell_size
        
        # vérifie que ces coordonnées sont valides
        if not (0 <= row < self.board_size and 0 <= col < self.board_size):
            return None  # coordonnées invalides
            
        return row, col 