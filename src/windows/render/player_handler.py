import pygame
from src.windows.render.constants import RenderConstants

class PlayerHandler:
    """
    classe : gestionnaire des personnages joueurs.
    
    gère le rendu des personnages sur le plateau de jeu.
    """
    
    def __init__(self, player_shadows, images):
        """
        constructeur : initialise le gestionnaire de personnages.
        
        params:
            player_shadows: dictionnaire contenant les ombres des joueurs
            images: dictionnaire contenant les images des joueurs
        """
        self.player_shadows = player_shadows
        self.images = images
    
    def draw_player(self, surface, cell, cell_rect):
        """
        procédure : dessine un joueur et son ombre s'il est présent dans la cellule.
        
        params:
            surface: surface où dessiner
            cell: données de la cellule (joueur, type_terrain)
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
            shadow_pos = (player_rect.x + RenderConstants.SHADOW_OFFSET[0], 
                          player_rect.y + RenderConstants.SHADOW_OFFSET[1])
            surface.blit(shadow, shadow_pos)
        
        # dessine le joueur par-dessus l'ombre
        surface.blit(player_image, player_rect.topleft) 