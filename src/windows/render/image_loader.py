import pygame
from PIL import Image, ImageFilter
from src.utils.logger import Logger
from src.windows.render.constants import RenderConstants

class ImageLoader:
    """
    classe : gestionnaire de chargement des images du jeu.
    
    charge et prépare toutes les images, fonds et sprites utilisés par le moteur de rendu.
    """
    def __init__(self, cell_size, window_width, window_height):
        """
        constructeur : initialise le chargeur d'images.
        
        params:
            cell_size: taille d'une cellule en pixels
            window_width: largeur de la fenêtre en pixels
            window_height: hauteur de la fenêtre en pixels
        """
        self.cell_size = cell_size
        self.window_width = window_width
        self.window_height = window_height
        self.images = {}
        self.player_shadows = {}
        self.background = None
        
        Logger.info("ImageLoader", "Image loader initialized")

    def load_all_images(self):
        """
        procédure : charge et prépare toutes les images du jeu.
        
        retour:
            tuple (images, player_shadows, background): les images chargées
        """
        Logger.info("ImageLoader", "Loading images")
        
        try:
            self._load_background()
            self._load_cell_images()
            self._load_player_images()
            
            return self.images, self.player_shadows, self.background
            
        except Exception as e:
            Logger.error("ImageLoader", f"Error loading images: {e}")
            return {}, {}, None

    def _load_background(self):
        """
        procédure : charge l'image de fond et applique un flou.
        """
        try:
            # chargement et redimensionnement
            bg = Image.open(f"assets/{RenderConstants.THEME}/background.png")
            bg = bg.resize((self.window_width, self.window_height), Image.LANCZOS)
            
            # application du flou gaussien
            blurred = bg.filter(ImageFilter.GaussianBlur(radius=10))
            bg_data = blurred.convert("RGBA").tobytes("raw", "RGBA")
            
            # conversion en surface pygame
            self.background = pygame.image.fromstring(bg_data, blurred.size, "RGBA").convert_alpha()
            Logger.debug("ImageLoader", "Background loaded and blurred")
        except FileNotFoundError:
            Logger.warning("ImageLoader", "Background image not found")
            self.background = None

    def _load_cell_images(self):
        """
        procédure : charge les images de terrain pour les cellules.
        """
        # parcours des types de terrain définis
        for terrain_id, img_file in RenderConstants.CELL_IMAGES.items():
            if not img_file or terrain_id is None:
                continue
                
            try:
                # chargement et redimensionnement à la taille exacte d'une cellule
                path = f"assets/cells/{img_file}"
                cell_img = Image.open(path)
                
                # préserve le style pixel art avec NEAREST
                # prend en compte le fait que les images sont soit pixel art soit lanczos
                # pour les images de cellules, on utilise NEAREST pour préserver le style pixel art
                # pour les images de personnages, on utilise LANCZOS pour une meilleure qualité
                resized = cell_img.resize((self.cell_size, self.cell_size), 
                                          Image.NEAREST if 'pixel' in img_file else Image.LANCZOS)
                img_data = resized.convert("RGBA").tobytes("raw", "RGBA")
                
                # conversion en surface pygame
                surface = pygame.image.fromstring(img_data, resized.size, "RGBA").convert_alpha()
                self.images[f"cell_{terrain_id}"] = surface
            except Exception:
                pass
        
        Logger.debug("ImageLoader", f"{len([k for k in self.images if k.startswith('cell_')])} terrain images loaded")

    def _load_player_images(self):
        """
        procédure : charge les images des personnages et génère leurs ombres.
        """
        for player in range(2):  # joueurs 0 et 1
            try:
                # chargement de l'image du joueur
                path = f"assets/{RenderConstants.THEME}/joueur{player+1}.png"
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
                shadow.fill((0, 0, 0, RenderConstants.SHADOW_ALPHA), special_flags=pygame.BLEND_RGBA_MULT)
                self.player_shadows[key] = shadow
            except Exception:
                raise Exception(f"Error loading player image {player+1}")
        
        Logger.debug("ImageLoader", f"{len(self.player_shadows)} player images loaded") 