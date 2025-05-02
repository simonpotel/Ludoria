import pygame
from PIL import Image
from src.utils.logger import Logger


class Render:
    """
    classe : gère l'affichage graphique du jeu (plateau, pièces, informations).
    utilise pygame pour le rendu et PIL pour le chargement/redimensionnement des images.
    """
    # couleurs des cellules à l'intérieur des quadrants en fonction de leur index
    QUADRANTS_CELLS_COLORS = {
        0: (255, 0, 0),    # red
        1: (0, 255, 0),    # green
        2: (0, 0, 255),    # blue
        3: (255, 255, 0),  # yellow
        4: (255, 255, 255),# white
        5: (0, 0, 0),      # black
        None: (128, 128, 128) # grey
    }

    def __init__(self, game, canvas_size=600):
        """
        constructeur : initialise le module de rendu, la fenêtre pygame et charge les ressources.

        params:
            game: instance de la classe de jeu (ex: Game de Katerenga, Isolation, etc.).
            canvas_size: taille du côté du canvas principal en pixels (le plateau sera carré).
        """
        Logger.info("Render", "Initializing game renderer")
        self.game = game # référence à l'instance du jeu pour accéder à l'état (board, etc.)
        self.canvas_size = canvas_size
        # déterminer la taille du plateau (nombre de cellules par côté)
        self.board_size = len(game.board.board) if game.board and game.board.board else 10 # valeur par défaut si board non initialisé
        self.running = True # contrôle la boucle principale de rendu
        self._setup_window()
        self.load_images()  # charge les images des pièces
        self.clock = pygame.time.Clock() # pour limiter le framerate
        self.info_text = "" # texte affiché dans la barre d'info
        self.font = pygame.font.SysFont('Arial', 20) # police pour les textes
        self.needs_render = True # flag pour contrôler le rendu
        self.render_board()  # premier rendu du plateau
        Logger.success("Render", "Game renderer initialized successfully")

    def _setup_window(self):
        """
        procédure : configure la fenêtre principale pygame et les surfaces.
        """
        pygame.init()
        # la hauteur totale inclut la barre d'info
        self.screen = pygame.display.set_mode((self.canvas_size, self.canvas_size + 50))
        pygame.display.set_caption(f"Smart Games: {self.game.game_save}") # titre de la fenêtre
        
        # surfaces séparées pour la barre d'info et le plateau
        self.info_surface = pygame.Surface((self.canvas_size, 50))
        self.board_surface = pygame.Surface((self.canvas_size, self.canvas_size))

    def load_images(self):
        """
        procédure : charge les images des pièces (tours) depuis les fichiers assets.
        redimensionne les images pour s'adapter à la taille des cellules.
        """
        Logger.info("Render", "Loading game piece images")
        self.images = {} # dictionnaire pour stocker les images chargées
        cell_size = self.canvas_size // self.board_size

        try:
            # charge l'image pour chaque joueur (0 et 1)
            for player in [0, 1]:
                image_path = f"assets/towns/{player}_tower.png"
                image = Image.open(image_path)
                # calcule les dimensions en gardant le ratio
                aspect_ratio = image.width / image.height
                new_height = cell_size - 10 # laisse une petite marge
                new_width = int(new_height * aspect_ratio)
                resized_image = image.resize((new_width, new_height), Image.LANCZOS) # redimensionne avec antialiasing
                
                # convertit l'image pil en surface pygame
                pil_image_data = resized_image.convert("RGBA").tobytes("raw", "RGBA")
                pygame_image = pygame.image.fromstring(pil_image_data, resized_image.size, "RGBA")
                
                image_key = f"tower_player_{player}"
                self.images[image_key] = pygame_image
                Logger.success("Render", f"Successfully loaded and resized image '{image_path}' as key '{image_key}'")
        except FileNotFoundError as e:
            Logger.error("Render", f"Image file not found: {e}. Make sure assets folder is correct.")
            raise # relance l'erreur pour arrêter si les images sont critiques
        except Exception as e:
            Logger.error("Render", f"Failed to load game piece images: {str(e)}")
            raise

    def edit_info_label(self, text):
        """
        procédure : met à jour le texte affiché dans la barre d'information.
        si le texte change, déclenche un nouveau rendu.

        params:
            text: nouveau texte à afficher.
        """
        Logger.info("Render", f"Updating info label to: '{text}'")
        if self.info_text != text:
            self.info_text = text
            self.needs_render = True 

    def render_board(self):
        """
        procédure : dessine l'état actuel complet du jeu (plateau, pièces, infos).
        c'est la fonction principale de rendu appelée à chaque mise à jour nécessaire.
        """
        Logger.board("Render", "Rendering game board and info")
        
        # efface les surfaces avant de redessiner
        self.board_surface.fill((200, 200, 200)) # fond gris clair pour le plateau
        self.info_surface.fill((220, 220, 220)) # fond gris un peu plus clair pour l'info
        
        # dessine le texte d'information principal (tour du joueur, messages, etc.)
        text_surface = self.font.render(self.info_text, True, (0, 0, 0)) # texte en noir
        text_rect = text_surface.get_rect(center=(self.canvas_size // 2, 15)) # centré en haut de la barre d'info
        self.info_surface.blit(text_surface, text_rect)
        
        # affiche le statut réseau si pertinent
        if hasattr(self.game, 'is_network_game') and self.game.is_network_game:
            self.display_network_status() # affiche le message réseau en dessous

        # dessine le plateau cellule par cellule
        cell_size = self.canvas_size // self.board_size
        for row_i, row in enumerate(self.game.board.board):
            for col_i, cell in enumerate(row):
                self._draw_cell(row_i, col_i, cell, cell_size)
        
        # copie les surfaces dessinées sur l'écran principal
        self.screen.blit(self.info_surface, (0, 0)) # barre d'info en haut
        self.screen.blit(self.board_surface, (0, 50)) # plateau en dessous
        pygame.display.flip() # met à jour l'écran visible par l'utilisateur
        
        Logger.success("Render", "Game board rendered successfully")

    def _draw_cell(self, row, col, cell, cell_size):
        """
        procédure : dessine une cellule individuelle du plateau.

        params:
            row: index de la ligne de la cellule.
            col: index de la colonne de la cellule.
            cell: tuple contenant l'état de la cellule (joueur, couleur_quadrant).
            cell_size: taille d'une cellule en pixels.
        """
        x1, y1 = col * cell_size, row * cell_size # coordonnées du coin supérieur gauche
        
        # dessine le fond de la cellule avec la couleur du quadrant
        quadrant_color_index = cell[1]
        cell_color = self.QUADRANTS_CELLS_COLORS.get(quadrant_color_index, (128, 128, 128)) # gris si index inconnu
        pygame.draw.rect(
            self.board_surface, 
            cell_color, 
            (x1, y1, cell_size, cell_size)
        )
        
        # dessine la bordure de la cellule
        pygame.draw.rect(
            self.board_surface, 
            (100, 100, 100), # couleur gris foncé pour les bordures
            (x1, y1, cell_size, cell_size), 
            1 # épaisseur de la bordure
        )

        # dessine la pièce (tour) si la cellule est occupée
        player = cell[0]
        if player is not None:
            piece_type = "tower" # pour l'instant, seulement des tours
            image_key = f"{piece_type}_player_{player}"
            if image_key in self.images:
                image = self.images[image_key]
                # centre l'image dans la cellule
                image_rect = image.get_rect(center=(x1 + cell_size // 2, y1 + cell_size // 2))
                self.board_surface.blit(image, image_rect)
            else:
                Logger.warning("Render", f"Image key '{image_key}' not found for cell ({row},{col}).")

        # dessine un cadre bleu si la pièce est sélectionnée
        if hasattr(self.game, 'selected_piece') and self.game.selected_piece == (row, col):
            pygame.draw.rect(
                self.board_surface, 
                (0, 0, 255), # couleur bleue pour la sélection
                (x1, y1, cell_size, cell_size), 
                3 # épaisseur du cadre
            )

    def handle_click(self, pos):
        """
        procédure : gère un clic de souris de l'utilisateur.
        calcule la cellule cliquée et appelle la méthode on_click du jeu.

        params:
            pos: tuple (x, y) des coordonnées du clic dans la fenêtre.
        """
        x, y = pos
        y_adjusted = y - 50  # ajuste pour la hauteur de la barre d'info
        
        # ignore les clics dans la barre d'info
        if y_adjusted < 0:
            Logger.info("Render", "Click detected in info bar area, ignoring.")
            return
            
        # calcule la ligne et la colonne cliquées sur le plateau
        cell_size = self.canvas_size // self.board_size
        row = y_adjusted // cell_size
        col = x // cell_size

        Logger.game("Render", f"Click detected at pixel ({x},{y}), adjusted y={y_adjusted}, calculated cell=({row},{col})")

        # vérifie si le clic est dans les limites du plateau
        if 0 <= row < self.board_size and 0 <= col < self.board_size:
            # vérifie si le joueur peut jouer (important pour le mode réseau)
            if hasattr(self.game, 'can_play') and self.game.can_play():
                # transmet le clic à la logique du jeu
                continue_game = self.game.on_click(row, col)
                if not continue_game:
                    # le jeu est terminé ou le coup était invalide et a déjà mis à jour le message
                    Logger.info("Render", f"Game logic indicated end or invalid move after click at ({row},{col}).")
                    # pas besoin de render ici, on_click ou edit_info_label l'a fait
                else:
                    # le coup était valide et le jeu continue
                    Logger.success("Render", f"Successfully processed click at ({row},{col}) by game logic.")
                    # le rendu est déclenché par edit_info_label dans on_click
            else:
                 # le joueur ne peut pas jouer (ex: pas son tour en réseau)
                 Logger.warning("Render", f"Player tried to click at ({row},{col}) but cannot play now.")
                 # on pourrait afficher un message, mais can_play met déjà à jour le statut
                 pass
        else:
            Logger.warning("Render", f"Click at ({x},{y}) is outside board boundaries ({row},{col}).")

    def run_game_loop(self):
        """
        procédure : exécute la boucle principale d'événements et de rendu du jeu.
        attend les actions de l'utilisateur (clic, fermeture) et les événements système (timer).
        """
        Logger.info("Render", "Starting main game loop.")

        while self.running:
            # traite tous les événements en attente
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    Logger.info("Render", "Quit event received, stopping game loop.")
                    self.running = False
                    pygame.quit()
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # clic gauche
                        self.handle_click(event.pos)
                # gestion des événements personnalisés (ex: timer du bot)
                elif event.type == pygame.USEREVENT:
                    if hasattr(self.game, 'handle_events'):
                        # passe l'événement à la logique du jeu (qui gère le timer)
                        self.game.handle_events(event)

            # render seulement si nécessaire, après avoir traité les événements
            if self.needs_render:
                self.render_board()
                self.needs_render = False # réinitialiser le flag après le rendu

            # le rendu n'est pas systématiquement appelé ici
            # il est déclenché par les changements d'état via edit_info_label -> render_board()
            # revoir peut être plus tard le timing des rendus -> si des animations de frames sont ajoutées plus tard
            
            self.clock.tick(30)  # limite le framerate à 30 fps car c'est un jeu de plateau
        
        Logger.info("Render", "Exited main game loop.")
            
    def display_network_status(self):
        """
        procédure : affiche le message de statut réseau dans la barre d'information.
        utilise le message et la couleur définis dans l'instance de jeu (GameBase).
        """
        # vérifie si les attributs nécessaires existent (pour éviter les erreurs si jeu non réseau)
        if not hasattr(self.game, 'status_message') or not self.game.status_message:
            return
            
        # rend le texte avec la couleur définie
        status_color = self.game.status_color if hasattr(self.game, 'status_color') else (0, 0, 0)
        text_surface = self.font.render(self.game.status_message, True, status_color)
        # positionne le texte en bas de la barre d'info, centré
        text_rect = text_surface.get_rect(center=(self.canvas_size // 2, 35))
        self.info_surface.blit(text_surface, text_rect)
