from collections import Counter

class QuadrantValidator:
    """
    class QuadrantValidator : vérifie la validité des quadrants selon les règles du jeu
    """
    REQUIRED_COUNT = 4  # nombre requis de chaque couleur
    VALID_COLORS = {'red', 'green', 'blue', 'yellow'}  # couleurs valides

    def is_valid_quadrant(self, grid):
        """
        fonction : vérifie si un quadrant respecte les règles de construction
        paramètres :
            grid - grille 4x4 à valider
        retourne : True si le quadrant est valide, False sinon
        
        règles de validité :
        - grille 4x4 complète
        - exactement 4 cases de chaque couleur
        - uniquement des couleurs valides
        """
        # vérifie la taille de la grille
        if not grid or len(grid) != 4 or any(len(row) != 4 for row in grid):
            return False

        # compte les occurrences de chaque couleur
        color_counts = Counter()
        for row in grid:
            for cell in row:
                if cell not in self.VALID_COLORS:
                    return False
                color_counts[cell] += 1

        # vérifie que chaque couleur apparaît exactement 4 fois
        return all(count == self.REQUIRED_COUNT for count in color_counts.values()) and \
               len(color_counts) == len(self.VALID_COLORS) 