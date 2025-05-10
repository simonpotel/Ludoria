from test_base import TestBase
import unittest
from src.moves import available_move

class TestBlueKingMovement(TestBase):
    """Test du mouvement d'un pion situé sur une case bleue (mouvement de roi)"""
    
    def setUp(self):
        super().setUp()
        
        # voir src/board.py pour les couleurs des cases
        # les cases contiennent [joueur, couleur]
        # où couleur est: 0=rouge, 1=verte, 2=bleue, 3=jaune(marron)
        self.board = [
            [[None, None] for _ in range(8)] for _ in range(8)
        ]
        
        # place un pion sur une case bleue
        self.board[3][3] = [0, 2]  # joueur 0, case bleue
    
    def test_king_directions(self):
        """Test des mouvements valides dans les 8 directions"""
        # le roi peut se déplacer d'une case dans n'importe quelle direction
        self.assertTrue(available_move(self.board, 3, 3, 2, 2))  # test roi peut se déplacer en diagonale haut-gauche
        self.assertTrue(available_move(self.board, 3, 3, 2, 3))  # test roi peut se déplacer vers le haut
        self.assertTrue(available_move(self.board, 3, 3, 2, 4))  # test roi peut se déplacer en diagonale haut-droite
        self.assertTrue(available_move(self.board, 3, 3, 3, 2))  # test roi peut se déplacer vers la gauche
        self.assertTrue(available_move(self.board, 3, 3, 3, 4))  # test roi peut se déplacer vers la droite
        self.assertTrue(available_move(self.board, 3, 3, 4, 2))  # test roi peut se déplacer en diagonale bas-gauche
        self.assertTrue(available_move(self.board, 3, 3, 4, 3))  # test roi peut se déplacer vers le bas
        self.assertTrue(available_move(self.board, 3, 3, 4, 4))  # test roi peut se déplacer en diagonale bas-droite
    
    def test_king_distance_limits(self):
        """Test des limites de distance de déplacement"""
        # le roi ne peut pas se déplacer de plus d'une case
        self.assertFalse(available_move(self.board, 3, 3, 1, 3))  # test roi ne peut pas se déplacer de deux cases vers le haut
        self.assertFalse(available_move(self.board, 3, 3, 3, 1))  # test roi ne peut pas se déplacer de deux cases vers la gauche
        self.assertFalse(available_move(self.board, 3, 3, 5, 5))  # test roi ne peut pas se déplacer de deux cases en diagonale
        self.assertFalse(available_move(self.board, 3, 3, 3, 6))  # test roi ne peut pas se déplacer de trois cases vers la droite
    
    def test_king_edge_cases(self):
        """Test des cas particuliers en bord de plateau"""
        # place un pion en bordure
        self.board[3][3] = [None, None] # nettoie (voir setUp pour la modification initiale)
        self.board[0][0] = [0, 2] # joueur 0, case bleue en coin
        
        # le roi peut se déplacer dans les 3 directions disponibles en coin
        self.assertTrue(available_move(self.board, 0, 0, 0, 1))  # test roi peut se déplacer vers la droite
        self.assertTrue(available_move(self.board, 0, 0, 1, 0))  # test roi peut se déplacer vers le bas
        self.assertTrue(available_move(self.board, 0, 0, 1, 1))  # test roi peut se déplacer en diagonale

if __name__ == "__main__":
    unittest.main() 