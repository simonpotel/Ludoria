import pygame
from PIL import Image, ImageFilter
from src.utils.logger import Logger

class Render:
    """
    classe : gestionnaire d'affichage graphique du jeu.
    
    utilise pygame pour le rendu et PIL pour traiter les images.
    gère le chargement des ressources, l'affichage du plateau, les animations
    et la détection des clics.
    """
    # constantes de configuration et de style
    INFO_BAR_HEIGHT = 50        # hauteur de la barre d'info en pixels
    BOARD_PADDING = 10          # marge autour du plateau de jeu
    SHADOW_OFFSET = (2, 2)      # décalage de l'ombre des pièces (x, y)
    SHADOW_ALPHA = 128          # transparence de l'ombre (0-255)
    SELECTION_COLOR = (255, 255, 255)  # couleur du cadre de sélection (blanc)
    SELECTION_WIDTH = 4         # épaisseur du cadre de sélection
    BOARD_BG_COLOR = (100, 100, 100)   # couleur de l'arrière-plan du plateau
    INFO_OVERLAY_COLOR = (0, 0, 0, 180) # couleur semi-transparente de la barre d'info

    # mapping des types de terrain vers les noms de fichiers
    CELL_IMAGES = {
        0: "red.png",      # feu
        1: "green.png",    # plante
        2: "blue.png",     # eau
        3: "brown.png",    # terre
        # ici on pourra ajouter d'autres files si on a besoin pour les camps par exemple si on 
        # veut faire un asset spécial en .png et pas juste une couleur 
    }
    
    QUADRANT_COLORS = {
        0: (255, 0, 0),    # red
        1: (0, 255, 0),    # green
        2: (0, 0, 255),    # blue
        3: (165, 42, 42),  # brown (remplace yellow)
        4: (255, 255, 255),# white
        5: (0, 0, 0),      # black
        None: (128, 128, 128) # grey
    }

    def __init__(self, game, canvas_size=600, window_width=1280, window_height=720):
        """
        procédure : initialise le moteur de rendu.
        
        params:
            game: instance du jeu à afficher
            canvas_size: taille logique du plateau de jeu (sans les marges)
            window_width: largeur de la fenêtre en pixels
            window_height: hauteur de la fenêtre en pixels
        """
        Logger.info("Render", "Initialisation du moteur de rendu")
        # données de base
        self.game = game
        self.canvas_size = canvas_size
        self.window_width = window_width
        self.window_height = window_height
        
        # dimensions calculées
        self.board_size = len(game.board.board) if game.board and game.board.board else 10
        self.cell_size = self.canvas_size // self.board_size
        self.board_surface_size = self.canvas_size + 2 * Render.BOARD_PADDING
        
        # état interne
        self.running = True
        self.info_text = ""
        self.needs_render = True
        
        # initialisation pygame
        self._setup_window()
        self.load_images()
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 20, bold=True)
        
        # premier rendu
        self.render_board()
        Logger.success("Render", "Moteur de rendu initialisé")

    def _setup_window(self):
        """
        procédure : configure la fenêtre et les surfaces de rendu.
        """
        pygame.init()
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption(f"Smart Games: {self.game.game_save}")
        
        # surface pour la barre d'info (avec transparence)
        self.info_surface = pygame.Surface((self.window_width, Render.INFO_BAR_HEIGHT), 
                                           pygame.SRCALPHA)
        
        # surface pour le plateau (avec marges)
        self.board_surface = pygame.Surface((self.board_surface_size, self.board_surface_size))
        
        # position du plateau centré dans la fenêtre
        self.board_x = (self.window_width - self.board_surface_size) // 2
        self.board_y = Render.INFO_BAR_HEIGHT + (self.window_height - Render.INFO_BAR_HEIGHT - 
                                               self.board_surface_size) // 2

    def load_images(self):
        """
        procédure : charge et prépare toutes les images du jeu.
        """
        Logger.info("Render", "Chargement des images")
        self.images = {}
        self.player_shadows = {}
        self.background = None
        
        try:
            # chargement du fond et application d'un flou gaussien
            self._load_background()
            
            # chargement des cellules (terrains)
            self._load_cell_images()
            
            # chargement des personnages joueurs
            self._load_player_images()
            
        except Exception as e:
            Logger.error("Render", f"Erreur lors du chargement des images: {e}")

    def _load_background(self):
        """
        procédure : charge l'image de fond et applique un flou.
        """
        try:
            # chargement et redimensionnement
            bg = Image.open("assets/tropique/background.png")
            bg = bg.resize((self.window_width, self.window_height), Image.LANCZOS)
            
            # application du flou gaussien
            blurred = bg.filter(ImageFilter.GaussianBlur(radius=10))
            bg_data = blurred.convert("RGBA").tobytes("raw", "RGBA")
            
            # conversion en surface pygame
            self.background = pygame.image.fromstring(bg_data, blurred.size, "RGBA").convert_alpha()
            Logger.debug("Render", "fond chargé et flouté")
        except FileNotFoundError:
            Logger.warning("Render", "image de fond non trouvée")
            self.background = None

    def _load_cell_images(self):
        """
        procédure : charge les images de terrain pour les cellules.
        """
        # parcours des types de terrain définis
        for terrain_id, img_file in self.CELL_IMAGES.items():
            if not img_file or terrain_id is None:
                continue
                
            try:
                # chargement et redimensionnement à la taille exacte d'une cellule
                path = f"assets/cells/{img_file}"
                cell_img = Image.open(path)
                
                # préserve le style pixel art avec NEAREST
                resized = cell_img.resize((self.cell_size, self.cell_size), 
                                          Image.NEAREST if 'pixel' in img_file else Image.LANCZOS)
                img_data = resized.convert("RGBA").tobytes("raw", "RGBA")
                
                # conversion en surface pygame
                surface = pygame.image.fromstring(img_data, resized.size, "RGBA").convert_alpha()
                self.images[f"cell_{terrain_id}"] = surface
            except Exception:
                # échec silencieux, une couleur de secours sera utilisée
                pass
        
        Logger.debug("Render", f"{len([k for k in self.images if k.startswith('cell_')])} images de terrain chargées")

    def _load_player_images(self):
        """
        procédure : charge les images des personnages et génère leurs ombres.
        """
        for player in range(2):  # joueurs 0 et 1
            try:
                # chargement de l'image du joueur
                path = f"assets/tropique/joueur{player+1}.png"
                img = Image.open(path).convert("RGBA")
                
                # redimensionnement pour remplir la hauteur d'une cellule
                aspect = img.width / img.height
                new_height = self.cell_size
                new_width = int(new_height * aspect)
                
                # utilise NEAREST pour préserver le style pixel art
                resized = img.resize((new_width, new_height), Image.NEAREST)
                img_data = resized.tobytes("raw", "RGBA")
                
                # conversion en surface pygame
                surface = pygame.image.fromstring(img_data, resized.size, "RGBA").convert_alpha()
                key = f"player_{player}"
                self.images[key] = surface
                
                # création de l'ombre du personnage
                shadow = surface.copy()
                shadow.fill((0, 0, 0, Render.SHADOW_ALPHA), special_flags=pygame.BLEND_RGBA_MULT)
                self.player_shadows[key] = shadow
            except Exception:
                raise Exception(f"Erreur lors du chargement de l'image du joueur {player+1}")
        
        Logger.debug("Render", f"{len(self.player_shadows)} images de personnages chargées")

    def edit_info_label(self, text):
        """
        procédure : met à jour le texte affiché dans la barre d'information.
        
        params:
            text: nouveau texte à afficher
        """
        if self.info_text != text:
            self.info_text = text
            self.needs_render = True
            Logger.info("Render", f"Mise à jour info: '{text}'")

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
        self._render_info_bar()
        
        # 3. plateau de jeu avec marges
        self._render_game_board()
        
        # 4. mise à jour de l'écran
        pygame.display.flip()
        Logger.board("Render", "Rendu terminé")

    def _render_info_bar(self):
        """
        procédure : dessine la barre d'information semi-transparente.
        """
        # effacement avec transparence totale
        self.info_surface.fill((0, 0, 0, 0))
        
        # dessine un rectangle semi-transparent
        pygame.draw.rect(self.info_surface, Render.INFO_OVERLAY_COLOR, self.info_surface.get_rect())
        
        # texte principal centré
        text_surface = self.font.render(self.info_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.window_width // 2, Render.INFO_BAR_HEIGHT // 2))
        self.info_surface.blit(text_surface, text_rect)
        
        # statut réseau (si applicable)
        if hasattr(self.game, 'is_network_game') and self.game.is_network_game:
            self._render_network_status()
            
        # affichage sur l'écran principal
        self.screen.blit(self.info_surface, (0, 0))

    def _render_network_status(self):
        """
        procédure : dessine le statut de connexion réseau dans la barre d'info.
        """
        if not hasattr(self.game, 'status_message') or not self.game.status_message:
            return
            
        # utilise la couleur définie par le jeu ou jaune par défaut
        color = getattr(self.game, 'status_color', (255, 255, 0))
        
        # dessine en bas à droite de la barre d'info
        font = pygame.font.SysFont('Arial', 16)
        text = font.render(self.game.status_message, True, color)
        rect = text.get_rect(bottomright=(self.window_width - 15, Render.INFO_BAR_HEIGHT - 5))
        self.info_surface.blit(text, rect)

    def _render_game_board(self):
        """
        procédure : dessine le plateau de jeu avec ses marges.
        """
        # fond gris pour les marges
        self.board_surface.fill(Render.BOARD_BG_COLOR)
        
        # dessine toutes les cellules du plateau
        for row_i, row in enumerate(self.game.board.board):
            for col_i, cell in enumerate(row):
                # calcule la position avec décalage dû aux marges
                x = Render.BOARD_PADDING + col_i * self.cell_size
                y = Render.BOARD_PADDING + row_i * self.cell_size
                self._draw_cell(row_i, col_i, cell, x, y)
        
        # affiche le plateau complet sur l'écran
        self.screen.blit(self.board_surface, (self.board_x, self.board_y))

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
            color = self.QUADRANT_COLORS.get(terrain_id, (128, 128, 128))
            pygame.draw.rect(self.board_surface, color, cell_rect)
        
        # 2. joueur (avec ombre) si présent
        self._draw_player_if_present(cell, cell_rect)
        
        # 3. cadre de sélection si sélectionné
        if hasattr(self.game, 'selected_piece') and self.game.selected_piece == (row, col):
            pygame.draw.rect(self.board_surface, Render.SELECTION_COLOR, cell_rect, Render.SELECTION_WIDTH)

    def _draw_player_if_present(self, cell, cell_rect):
        """
        procédure : dessine un joueur et son ombre s'il est présent dans la cellule.
        
        params:
            cell: données de la cellule
            cell_rect: rectangle de la cellule où dessiner
        """
        player = cell[0]
        if player is None:
            return
            
        image_key = f"player_{player}"
        if image_key not in self.images:
            return
            
        # récupère l'image du joueur
        player_image = self.images[image_key]
        player_rect = player_image.get_rect(center=cell_rect.center)
        
        # dessine l'ombre en premier (légèrement décalée)
        if image_key in self.player_shadows:
            shadow = self.player_shadows[image_key]
            shadow_pos = (player_rect.x + Render.SHADOW_OFFSET[0], player_rect.y + Render.SHADOW_OFFSET[1])
            self.board_surface.blit(shadow, shadow_pos)
        
        # dessine le joueur par-dessus l'ombre
        self.board_surface.blit(player_image, player_rect.topleft)

    def handle_click(self, pos):
        """
        procédure : traite un clic de souris et le transmet au jeu si pertinent.
        
        params:
            pos: tuple (x, y) des coordonnées du clic dans la fenêtre
        """
        x, y = pos
        
        # vérification rapide si le clic est sur le plateau
        if not (self.board_x <= x < self.board_x + self.board_surface_size and
                self.board_y <= y < self.board_y + self.board_surface_size):
            return  # clic en dehors du plateau
            
        # conversion en coordonnées relatives au plateau
        board_x = x - self.board_x - Render.BOARD_PADDING
        board_y = y - self.board_y - Render.BOARD_PADDING
        
        # vérifie si le clic est sur une cellule (pas sur la marge)
        if not (0 <= board_x < self.canvas_size and 0 <= board_y < self.canvas_size):
            return  # clic sur la marge
            
        # calcule les coordonnées logiques de la cellule
        row = board_y // self.cell_size
        col = board_x // self.cell_size
        
        # vérifie que ces coordonnées sont valides
        if not (0 <= row < self.board_size and 0 <= col < self.board_size):
            return  # coordonnées invalides
            
        # vérifie si le joueur peut jouer
        if hasattr(self.game, 'can_play') and self.game.can_play():
            # transmet le clic à la logique du jeu
            self.game.on_click(row, col)
            # note: on_click met à jour l'affichage via edit_info_label

    def run_game_loop(self):
        """
        procédure : exécute la boucle principale du jeu.
        """
        Logger.info("Render", "Démarrage de la boucle de jeu")
        self.running = True
        
        while self.running:
            # gestion des événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_click(event.pos)
                elif event.type == pygame.USEREVENT and hasattr(self.game, 'handle_events'):
                    self.game.handle_events(event)
            
            # rendu si nécessaire
            if self.needs_render:
                self.render_board()
                self.needs_render = False
            
            # limite le framerate
            self.clock.tick(30)
        
        Logger.info("Render", "Boucle de jeu terminée")
