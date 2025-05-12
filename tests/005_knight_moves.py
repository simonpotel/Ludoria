from test_base import TestBase
import unittest
from src.moves import available_move

class TestGreenKnightMovement(TestBase):
    """Test du mouvement d'un pion situé sur une case verte (mouvement de cavalier)"""
    
    def setUp(self):
        super().setUp()
        
        # voir src/board.py pour les couleurs des cases
        # les cases contiennent [joueur, couleur]
        # 0 = rouge, 1 = verte, 2 = bleue, 3 = jaune (marron)
        self.board = [
            [[None, None] for _ in range(8)] for _ in range(8)
        ]
        
        self.board[4][4] = [0, 1]  # joueur 0, case verte
    
    def test_knight_directions(self):
        """test des mouvements valides dans toutes les directions L"""
        # un cavalier se déplace en L: 2 cases puis 1 perpendiculairement
        self.assertTrue(available_move(self.board, 4, 4, 2, 3))  # test cavalier peut se déplacer de 2 vers le haut et 1 vers la gauche
        self.assertTrue(available_move(self.board, 4, 4, 2, 5))  # test cavalier peut se déplacer de 2 vers le haut et 1 vers la droite
        self.assertTrue(available_move(self.board, 4, 4, 3, 2))  # test cavalier peut se déplacer de 1 vers le haut et 2 vers la gauche
        self.assertTrue(available_move(self.board, 4, 4, 3, 6))  # test cavalier peut se déplacer de 1 vers le haut et 2 vers la droite
        self.assertTrue(available_move(self.board, 4, 4, 5, 2))  # test cavalier peut se déplacer de 1 vers le bas et 2 vers la gauche
        self.assertTrue(available_move(self.board, 4, 4, 5, 6))  # test cavalier peut se déplacer de 1 vers le bas et 2 vers la droite
        self.assertTrue(available_move(self.board, 4, 4, 6, 3))  # test cavalier peut se déplacer de 2 vers le bas et 1 vers la gauche
        self.assertTrue(available_move(self.board, 4, 4, 6, 5))  # test cavalier peut se déplacer de 2 vers le bas et 1 vers la droite
    
    def test_knight_invalid_moves(self):
        """test des mouvements non valides"""
        # un cavalier ne peut pas se déplacer différemment
        self.assertFalse(available_move(self.board, 4, 4, 4, 5))  # test cavalier ne peut pas se déplacer horizontalement d'une case
        self.assertFalse(available_move(self.board, 4, 4, 5, 4))  # test cavalier ne peut pas se déplacer verticalement d'une case
        self.assertFalse(available_move(self.board, 4, 4, 4, 6))  # test cavalier ne peut pas se déplacer horizontalement de deux cases
        self.assertFalse(available_move(self.board, 4, 4, 6, 4))  # test cavalier ne peut pas se déplacer verticalement de deux cases
        self.assertFalse(available_move(self.board, 4, 4, 5, 5))  # test cavalier ne peut pas se déplacer en diagonale
        self.assertFalse(available_move(self.board, 4, 4, 6, 6))  # test cavalier ne peut pas se déplacer en diagonale de deux cases
    
    def test_knight_jump(self):
        """test de la capacité à sauter par-dessus des pièces"""
        # place des pièces sur le trajet du cavalier
        self.board[4][5] = [1, 2]  # joueur 1, case bleue
        self.board[5][4] = [1, 3]  # joueur 1, case jaune
        
        # le cavalier peut sauter par-dessus d'autres pièces
        self.assertTrue(available_move(self.board, 4, 4, 6, 5))  # test cavalier peut sauter par-dessus des pièces
        self.assertTrue(available_move(self.board, 4, 4, 6, 3))  # test cavalier peut sauter par-dessus des pièces
    
    def test_knight_edge_cases(self):
        """test des cas particuliers en bord de plateau"""
        # place un pion en bordure et retirer la case verte initiale (voir setUp)
        self.board[4][4] = [None, None]  # nettoie (voir setUp pour la modification initiale)
        self.board[0][0] = [0, 1]  # joueur 0, case verte en coin
        
        # le cavalier peut faire des mouvements en L valides depuis un coin
        self.assertTrue(available_move(self.board, 0, 0, 1, 2))  # test cavalier peut se déplacer de 1 vers le bas et 2 vers la droite
        self.assertTrue(available_move(self.board, 0, 0, 2, 1))  # test cavalier peut se déplacer de 2 vers le bas et 1 vers la droite

if __name__ == "__main__":
    unittest.main() 