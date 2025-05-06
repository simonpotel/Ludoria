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
    # système temporaire de sélection de thème 
    THEME = "nordique"
    
    
    # constantes de configuration et de style
    INFO_BAR_HEIGHT = 50        # hauteur de la barre d'info en pixels
    BOARD_PADDING = 10          # marge autour du plateau de jeu
    SHADOW_OFFSET = (2, 2)      # décalage de l'ombre des pièces (x, y)
    SHADOW_ALPHA = 128          # transparence de l'ombre (0-255)
    SELECTION_COLOR = (255, 255, 255)  # couleur du cadre de sélection (blanc)
    SELECTION_WIDTH = 4         # épaisseur du cadre de sélection
    BOARD_BG_COLOR = (100, 100, 100)   # couleur de l'arrière-plan du plateau
    INFO_OVERLAY_COLOR = (0, 0, 0, 180) # couleur semi-transparente de la barre d'info
    
    # constantes pour le chat
    CHAT_WIDTH = 250            # largeur du panneau de chat en pixels
    CHAT_MARGIN = 10            # marge autour du chat en pixels
    CHAT_INPUT_HEIGHT = 30      # hauteur de la zone de saisie du chat
    CHAT_BG_COLOR = (30, 30, 30, 200)  # couleur semi-transparente du fond de chat
    CHAT_INPUT_COLOR = (50, 50, 50, 255)  # couleur de la zone de saisie
    CHAT_TEXT_COLOR = (255, 255, 255)  # couleur du texte du chat
    CHAT_INPUT_ACTIVE_COLOR = (70, 70, 70, 255)  # couleur de la zone de saisie active

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
        self._load_font()
        
        # chat
        self.chat_surface = None
        if hasattr(self.game, 'is_network_game') and self.game.is_network_game:
            self._setup_chat_surface()
        
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
        # ajuste la position si mode réseau pour faire de la place au chat
        self.board_x = (self.window_width - self.board_surface_size) // 2
        if hasattr(self.game, 'is_network_game') and self.game.is_network_game:
            # décale le plateau vers la droite pour faire place au chat
            self.board_x = Render.CHAT_WIDTH + Render.CHAT_MARGIN * 2 + (self.window_width - Render.CHAT_WIDTH - self.board_surface_size) // 2
        
        self.board_y = Render.INFO_BAR_HEIGHT + (self.window_height - Render.INFO_BAR_HEIGHT - 
                                               self.board_surface_size) // 2

    def _setup_chat_surface(self):
        """
        procédure : configure la surface pour le chat.
        """
        # hauteur du chat = hauteur de la fenêtre moins la barre d'info
        chat_height = self.window_height - Render.INFO_BAR_HEIGHT - Render.CHAT_MARGIN * 2
        
        # crée la surface avec transparence
        self.chat_surface = pygame.Surface((Render.CHAT_WIDTH, chat_height), pygame.SRCALPHA)
        
        # position du chat (coin supérieur gauche)
        self.chat_x = Render.CHAT_MARGIN
        self.chat_y = Render.INFO_BAR_HEIGHT + Render.CHAT_MARGIN
        
        Logger.info("Render", "Surface de chat configurée")

    def _load_font(self):
        """
        procédure : charge la police de caractères personnalisée.
        """
        font_path = "assets/fonts/BlackHanSans-Regular.ttf"
        self.main_font = pygame.font.Font(font_path, 24) 
        self.status_font = pygame.font.Font(font_path, 18)
        self.chat_font = pygame.font.Font(font_path, 14)
        Logger.info("Render", f"Police chargée: {font_path}")

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
            bg = Image.open(f"assets/{self.THEME}/background.png")
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
                path = f"assets/{self.THEME}/joueur{player+1}.png"
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
        
        # 3. chat si en mode réseau
        if hasattr(self.game, 'is_network_game') and self.game.is_network_game:
            self._render_chat()
        
        # 4. plateau de jeu avec marges
        self._render_game_board()
        
        # 5. mise à jour de l'écran
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
        text_surface = self.main_font.render(self.info_text, True, (255, 255, 255))
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
        text = self.status_font.render(self.game.status_message, True, color)
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

    def _render_chat(self):
        """
        procédure : dessine l'interface de chat.
        """
        if not self.chat_surface or not hasattr(self.game, 'chat_messages'):
            return
            
        self.chat_surface.fill((0, 0, 0, 0)) # remplit la surface avec transparence
        
        chat_bg_rect = pygame.Rect(0, 0, Render.CHAT_WIDTH, self.chat_surface.get_height()) # rectangle de la fenêtre
        pygame.draw.rect(self.chat_surface, Render.CHAT_BG_COLOR, chat_bg_rect, 0, 10) # dessine le rectangle
        
        title = self.status_font.render("CHAT", True, Render.CHAT_TEXT_COLOR) # titre de la fenêtre
        title_rect = title.get_rect(midtop=(Render.CHAT_WIDTH // 2, 5)) # position du titre
        self.chat_surface.blit(title, title_rect) # dessine le titre
        
        if hasattr(self.game, 'chat_messages') and self.game.chat_messages:
            # calcule la hauteur disponible pour les messages
            chat_surface_total_height = self.chat_surface.get_height() # hauteur de la fenêtre
            chat_input_field_height = Render.CHAT_INPUT_HEIGHT # hauteur du champ de saisie 
            bottom_area_reserved_for_input = chat_input_field_height + 5 # espace pour le champ de saisie
            top_area_reserved_for_title_and_padding = 30 # espace pour le titre et les marges
            available_height_for_message_text = chat_surface_total_height - (
                bottom_area_reserved_for_input + top_area_reserved_for_title_and_padding
            ) # hauteur disponible pour les messages
            single_chat_line_height = self.chat_font.get_linesize() # hauteur d'une ligne de texte 
            if single_chat_line_height > 0 and available_height_for_message_text > 0:
                theoretical_max_lines = available_height_for_message_text // single_chat_line_height
                num_lines_to_try_fit = max(1, theoretical_max_lines) # nombre de lignes à essayer de fitter
            else:
                num_lines_to_try_fit = 0 # si pas de hauteur disponible
            
            if num_lines_to_try_fit > 0:
                num_recent_messages_to_fetch = num_lines_to_try_fit # nombre de messages à afficher
                messages_to_display = self.game.chat_messages[-num_recent_messages_to_fetch:] # messages à afficher
            else:
                messages_to_display = [] # si pas de hauteur disponible

            original_messages_height_variable = self.chat_surface.get_height() - Render.CHAT_INPUT_HEIGHT - 20 # hauteur de la fenêtre
            y_pos = original_messages_height_variable - 5 # position initiale
            
            for msg in reversed(messages_to_display): # reverse pour afficher les derniers messages en premier
                wrapped_lines = self._wrap_text(msg, Render.CHAT_WIDTH - 20, self.chat_font) # wrap le texte
                
                for line in reversed(wrapped_lines): # reverse pour afficher les lignes en premier
                    text = self.chat_font.render(line, True, Render.CHAT_TEXT_COLOR) # texte
                    text_height = text.get_height() # hauteur du texte
                    
                    if y_pos - text_height < 30: # si la ligne est en dehors de la zone visible
                        break 
                        
                    self.chat_surface.blit(text, (10, y_pos - text_height)) # dessine la ligne
                    y_pos -= text_height + 2 # espace entre les lignes
                else: 
                    y_pos -= 5 
                    if y_pos < 30: # si la ligne est en dehors de la zone visible
                        break
                    continue 
                break 
        
        # dessine l'input
        input_rect = pygame.Rect(5, self.chat_surface.get_height() - Render.CHAT_INPUT_HEIGHT - 5, 
                                Render.CHAT_WIDTH - 10, Render.CHAT_INPUT_HEIGHT)
        
        # couleur différente si actif
        input_color = Render.CHAT_INPUT_ACTIVE_COLOR if hasattr(self.game, 'chat_active') and self.game.chat_active else Render.CHAT_INPUT_COLOR
        
        pygame.draw.rect(self.chat_surface, input_color, input_rect, 0, 5) # dessine le rectangle
        
        # texte d'invite ou contenu de l'input
        input_text = self.game.chat_input if hasattr(self.game, 'chat_input') and self.game.chat_input else "Appuyez sur Entrée pour chatter..."
        
        available_width_for_text = input_rect.width - 10 # space avec padding de 5px de chaque côté
        ellipsis_chars = "..."

        full_text_width = self.chat_font.size(input_text)[0]

        # si le texte est trop long, on essaie d'afficher la fin avec "..." au début.
        if full_text_width <= available_width_for_text:
            visible_text = input_text
        else:
            visible_text = ellipsis_chars
            for num_chars_in_suffix in range(1, len(input_text) + 1): 
                current_suffix = input_text[-num_chars_in_suffix:] 
                text_to_measure = ellipsis_chars + current_suffix 
                if self.chat_font.size(text_to_measure)[0] <= available_width_for_text:
                    visible_text = text_to_measure
                else:
                    break 
            if visible_text == ellipsis_chars and self.chat_font.size(ellipsis_chars)[0] > available_width_for_text:
                visible_text = ""
            
        # affiche le texte
        text = self.chat_font.render(visible_text, True, Render.CHAT_TEXT_COLOR if self.game.chat_active else (180, 180, 180))
        text_rect = text.get_rect(midleft=(input_rect.left + 5, input_rect.centery)) # position du texte
        self.chat_surface.blit(text, text_rect) # dessine le texte
        
        # affiche la surface complète
        self.screen.blit(self.chat_surface, (self.chat_x, self.chat_y)) # dessine la surface

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

    def handle_click(self, pos):
        """
        procédure : traite un clic de souris et le transmet au jeu si pertinent.
        
        params:
            pos: tuple (x, y) des coordonnées du clic dans la fenêtre
        """
        x, y = pos
        
        # vérifie si le clic est dans la zone de chat
        if hasattr(self.game, 'is_network_game') and self.game.is_network_game:
            if self.chat_x <= x < self.chat_x + Render.CHAT_WIDTH and self.chat_y <= y < self.chat_y + self.chat_surface.get_height():
                # clic dans la zone input?
                input_rect = pygame.Rect(self.chat_x + 5, 
                                        self.chat_y + self.chat_surface.get_height() - Render.CHAT_INPUT_HEIGHT - 5, 
                                        Render.CHAT_WIDTH - 10, 
                                        Render.CHAT_INPUT_HEIGHT)
                if input_rect.collidepoint(x, y):
                    # active l'input du chat
                    self.game.chat_active = True
                    self.needs_render = True
                return  # clic traité
        
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
        
        Logger.info("Render", "Boucle de jeu terminée")
