from collections import Counter

class QuadrantValidator:
    # nombre requis de chaque couleur et couleurs valides
    REQUIRED_COUNT = 4
    VALID_COLORS = {'red', 'green', 'blue', 'yellow'}

    def is_valid_quadrant(self, grid):
        # vérifie si le quadrant est valide (4x4 avec 4 de chaque couleur)
        if not grid or len(grid) != 4 or any(len(row) != 4 for row in grid):
            return False

        color_counts = Counter()
        for row in grid:
            for cell in row:
                if cell not in self.VALID_COLORS:
                    return False
                color_counts[cell] += 1

        return all(count == self.REQUIRED_COUNT for count in color_counts.values()) and \
               len(color_counts) == len(self.VALID_COLORS) 