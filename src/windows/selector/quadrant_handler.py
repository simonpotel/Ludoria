import pygame
from typing import List, Optional, Dict, Any, Tuple
from src.utils.logger import Logger
from src.windows.render.constants import RenderConstants

class QuadrantHandler:
    """
    classe : gestionnaire des opérations sur les quadrants.
    fournit des méthodes pour le dessin, la rotation (gauche/droite), 
    et la mise à jour des configurations de quadrants sélectionnées par l'utilisateur.
    """
    
    def __init__(self) -> None:
        """
        constructeur : procédure d'initialisation du gestionnaire de quadrants.
        aucune initialisation spécifique requise.
        """
        pass
    
    def draw_quadrants(self, screen: pygame.Surface, selected_quadrants: List[List[List[List[Optional[int]]]]], canvas_rect: pygame.Rect) -> None:
        """
        procédure : dessin de la prévisualisation des quatre quadrants.
        dessine les quadrants configurés sur une zone spécifiée de l'écran (`canvas_rect`).
        
        params:
            screen (pygame.surface.Surface): surface pygame sur laquelle dessiner.
            selected_quadrants (list): liste des quatre configurations de quadrants actuellement sélectionnées.
            canvas_rect (pygame.Rect): rectangle définissant la zone de dessin pour la prévisualisation.
        """
        quadrant_area_size = canvas_rect.width // 2
        cell_size = quadrant_area_size // 4 # chaque quadrant est supposé être 4x4 pour la prévisualisation
        
        for i in range(4): # itère sur les quatre positions de quadrant (0, 1, 2, 3)
            quadrant_data = selected_quadrants[i]
            
            if quadrant_data is None:
                Logger.warning("QuadrantHandler", f"Quadrant data at index {i} not available. Skipping drawing.")
                continue
                
            # calcule le décalage x, y pour positionner le quadrant dans la grille 2x2
            x_offset = (i % 2) * quadrant_area_size + canvas_rect.left
            y_offset = (i // 2) * quadrant_area_size + canvas_rect.top
            
            self.draw_quadrant(screen, quadrant_data, x_offset, y_offset, cell_size)
            pygame.draw.rect( # dessine une bordure autour de chaque zone de quadrant
                screen, 
                (50, 50, 50), # couleur gris foncé pour la bordure
                (x_offset, y_offset, quadrant_area_size, quadrant_area_size), 
                2 # épaisseur de la bordure
            )

    def draw_quadrant(self, screen: pygame.Surface, quadrant_data: List[List[List[Optional[int]]]], x_offset: int, y_offset: int, cell_size: int) -> None:
        """
        procédure : dessin d'un quadrant individuel.
        dessine chaque cellule du quadrant donné avec la couleur appropriée.

        params:
            screen (pygame.surface.Surface): surface pygame sur laquelle dessiner.
            quadrant_data (list): liste de listes (matrice) représentant la configuration du quadrant.
                               chaque cellule contient typiquement un tuple (type_pion, index_couleur).
            x_offset (int): coordonnée x du coin supérieur gauche de la zone de dessin du quadrant.
            y_offset (int): coordonnée y du coin supérieur gauche de la zone de dessin du quadrant.
            cell_size (int): taille en pixels d'une cellule dans la prévisualisation.
        """         
        for row_i, row in enumerate(quadrant_data):
            for col_i, cell_state in enumerate(row):
                x1 = x_offset + col_i * cell_size
                y1 = y_offset + row_i * cell_size
                
                color_index = 0 # couleur par défaut (ex: case vide)
                if isinstance(cell_state, (list, tuple)) and len(cell_state) > 1:
                    color_index = cell_state[1] # l'index de couleur est attendu comme deuxième élément
                elif cell_state is not None: # si ce n'est pas none mais format incorrect
                    Logger.warning("QuadrantHandler", f"Invalid cell state format in quadrant data: {cell_state}")
                
                cell_color = RenderConstants.QUADRANT_COLORS.get(color_index, (128, 128, 128)) # gris si index couleur inconnu
                pygame.draw.rect(
                    screen, 
                    cell_color, 
                    (x1, y1, cell_size, cell_size)
                )
                pygame.draw.rect( # dessine la bordure de la cellule
                    screen, 
                    (0, 0, 0), # noir
                    (x1, y1, cell_size, cell_size),
                    1 # épaisseur de 1 pixel
                )

    def update_selected_quadrants(self, quadrant_selectors: List[Any], selected_quadrants: List[List[List[List[Optional[int]]]]], 
                                quadrants_config: Dict[str, List[List[List[Optional[int]]]]], quadrant_names: List[str]) -> List[List[List[List[Optional[int]]]]]:
        """
        fonction : mise à jour des configurations de quadrants sélectionnées.
        basée sur les choix de l'utilisateur dans les menus déroulants (`quadrant_selectors`).
        
        params:
            quadrant_selectors (list): liste des 4 objets `Dropdown` pour la sélection des quadrants.
            selected_quadrants (list): liste actuelle des configurations de quadrants.
            quadrants_config (dict): dictionnaire de toutes les configurations de quadrants disponibles (nom -> données).
            quadrant_names (list): liste triée des noms de toutes les configurations de quadrants.
            
        retour:
            list: nouvelle liste des configurations de quadrants mises à jour.
        """
        Logger.debug("QuadrantHandler", "Updating selected quadrants based on dropdown menus.")
        new_selected_quadrants = []
        
        if not quadrants_config:
            Logger.error("QuadrantHandler", "Quadrant configuration not loaded, unable to update selections.")
            return [[[] for _ in range(4)]] # return empty structure mais du même format
        
        for i, selector in enumerate(quadrant_selectors):
            selected_name = selector.get()
            
            if selected_name and selected_name in quadrants_config:
                # copie profonde pour éviter de modifier la configuration originale lors des rotations
                quadrant_copy = [row[:] for row in quadrants_config[selected_name]]
                new_selected_quadrants.append(quadrant_copy)
            else:
                Logger.warning("QuadrantHandler", f"Invalid quadrant name '{selected_name}' selected for quadrant {i}. Keeping previous or default.")
                if i < len(selected_quadrants) and selected_quadrants[i] is not None:
                    new_selected_quadrants.append(selected_quadrants[i]) # conserve l'ancien si valide
                else:
                    # fallback vers une configuration par défaut si l'ancien n'est pas valide ou non existant
                    default_name = quadrant_names[0] if quadrant_names else None
                    if default_name and default_name in quadrants_config:
                        default_copy = [row[:] for row in quadrants_config[default_name]]
                        new_selected_quadrants.append(default_copy)
                        Logger.warning("QuadrantHandler", f"Returning to default configuration '{default_name}' for index {i}.")
                    else:
                        raise ValueError(f"No default configuration found for index {i}.")

        return new_selected_quadrants

    def _rotate_matrix(self, matrix: List[List[List[Optional[int]]]], direction: str) -> List[List[List[Optional[int]]]]:
        """
        fonction : effectue une rotation de matrice (quadrant).
        pivote une matrice de 90 degrés dans la direction spécifiée.

        params:
            matrix (list): la matrice (quadrant) à pivoter.
            direction (str): "droite" ou "gauche".

        retour:
            list: la nouvelle matrice pivotée.
        """
        size = len(matrix)
        new_matrix = [[(None, None) for _ in range(size)] for _ in range(size)]
        for r in range(size):
            for c in range(size):
                if direction == "right":
                    new_matrix[c][size - 1 - r] = matrix[r][c]
                elif direction == "left":
                    new_matrix[size - 1 - c][r] = matrix[r][c]
        return new_matrix

    def rotate_right(self, selected_quadrants: List[List[List[List[Optional[int]]]]], index: int) -> List[List[List[List[Optional[int]]]]]:
        """
        fonction : rotation d'un quadrant vers la droite.
        fait pivoter le quadrant spécifié de 90 degrés vers la droite (sens horaire).

        params:
            selected_quadrants (list): liste des configurations de quadrants actuelles.
            index (int): index (0-3) du quadrant à pivoter.
            
        retour:
            list: liste mise à jour des configurations de quadrants avec le quadrant pivoté.
        """
        if not (0 <= index < len(selected_quadrants)) or selected_quadrants[index] is None:
            Logger.error("QuadrantHandler", f"Invalid index {index} or quadrant data is None for right rotation.")
            return selected_quadrants
        
        Logger.debug("QuadrantHandler", f"Rotating quadrant {index} to the right.")
        
        rotated_quadrant = self._rotate_matrix(selected_quadrants[index], "right")
        
        new_selected_quadrants = list(selected_quadrants) # copie pour éviter la modification de la liste originale en place
        new_selected_quadrants[index] = rotated_quadrant
        return new_selected_quadrants

    def rotate_left(self, selected_quadrants: List[List[List[List[Optional[int]]]]], index: int) -> List[List[List[List[Optional[int]]]]]:
        """
        fonction : rotation d'un quadrant vers la gauche.
        fait pivoter le quadrant spécifié de 90 degrés vers la gauche (sens anti-horaire).

        params:
            selected_quadrants (list): liste des configurations de quadrants actuelles.
            index (int): index (0-3) du quadrant à pivoter.
            
        retour:
            list: liste mise à jour des configurations de quadrants avec le quadrant pivoté.
        """
        if not (0 <= index < len(selected_quadrants)) or selected_quadrants[index] is None:
            Logger.error("QuadrantHandler", f"Invalid index {index} or quadrant data is None for left rotation.")
            return selected_quadrants
        
        Logger.debug("QuadrantHandler", f"Rotating quadrant {index} to the left.")
        
        rotated_quadrant = self._rotate_matrix(selected_quadrants[index], "left")

        new_selected_quadrants = list(selected_quadrants) # copie pour éviter la modification de la liste originale en place
        new_selected_quadrants[index] = rotated_quadrant
        return new_selected_quadrants 