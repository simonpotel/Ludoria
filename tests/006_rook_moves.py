from test_base import TestBase
import unittest
from src.moves import available_move

class TestRedRookMovement(TestBase):
    """Test du mouvement d'un pion situé sur une case rouge (mouvement de tour avec règle spéciale)"""
    
    def setUp(self):
        super().setUp()
        
        # voir src/board.py pour les couleurs des cases
        # les cases contiennent [joueur, couleur]
        # 0 = rouge, 1 = verte, 2 = bleue, 3 = jaune (marron)
        self.board = [
            [[None, None] for _ in range(8)] for _ in range(8)
        ]
        
        self.board[3][3] = [0, 0]  # joueur 0, case rouge
    
    def test_rook_directions(self):
        """test des mouvements valides horizontalement et verticalement"""
        # une tour se déplace horizontalement ou verticalement
        self.assertTrue(available_move(self.board, 3, 3, 3, 0))  # test tour peut se déplacer horizontalement vers la gauche
        self.assertTrue(available_move(self.board, 3, 3, 3, 7))  # test tour peut se déplacer horizontalement vers la droite
        self.assertTrue(available_move(self.board, 3, 3, 0, 3))  # test tour peut se déplacer verticalement vers le haut
        self.assertTrue(available_move(self.board, 3, 3, 7, 3))  # test tour peut se déplacer verticalement vers le bas
        
        # une tour peut se déplacer de plusieurs cases
        self.assertTrue(available_move(self.board, 3, 3, 3, 1))  # test tour peut se déplacer de deux cases vers la gauche
        self.assertTrue(available_move(self.board, 3, 3, 3, 6))  # test tour peut se déplacer de plusieurs cases vers la droite
        self.assertTrue(available_move(self.board, 3, 3, 1, 3))  # test tour peut se déplacer de plusieurs cases vers le haut
        self.assertTrue(available_move(self.board, 3, 3, 6, 3))  # test tour peut se déplacer de plusieurs cases vers le bas
    
    def test_rook_invalid_moves(self):
        """test des mouvements non valides"""
        # une tour ne peut pas se déplacer en diagonale
        self.assertFalse(available_move(self.board, 3, 3, 4, 4))  # test tour ne peut pas se déplacer en diagonale bas-droite
        self.assertFalse(available_move(self.board, 3, 3, 2, 2))  # test tour ne peut pas se déplacer en diagonale haut-gauche
        self.assertFalse(available_move(self.board, 3, 3, 2, 4))  # test tour ne peut pas se déplacer en diagonale haut-droite
        self.assertFalse(available_move(self.board, 3, 3, 4, 2))  # test tour ne peut pas se déplacer en diagonale bas-gauche
        self.assertFalse(available_move(self.board, 3, 3, 2, 5))  # test tour ne peut pas se déplacer en L comme un cavalier
    
    def test_rook_obstacles(self):
        """test des obstacles sur le trajet"""
        # une tour ne peut pas sauter par-dessus d'autres pièces
        self.board[3][5] = [1, 1]  # joueur 1, case verte
        self.assertTrue(available_move(self.board, 3, 3, 3, 4))  # test tour peut se déplacer d'une case vers la droite
        self.assertTrue(available_move(self.board, 3, 3, 3, 5))  # test tour peut capturer un pion adverse
        self.assertFalse(available_move(self.board, 3, 3, 3, 6))  # test tour ne peut pas sauter par-dessus d'autres pièces
        
        # une tour ne peut pas se déplacer sur une case occupée par un pion du même joueur
        self.board[3][5] = [0, 1]  # joueur 0, case verte
        self.assertTrue(available_move(self.board, 3, 3, 3, 4))  # test tour peut se déplacer vers une case vide
        self.assertFalse(available_move(self.board, 3, 3, 3, 5))  # test tour ne peut pas se déplacer sur une case occupée par un pion allié
        
        self.board[3][5] = [None, None]  # nettoie 
    
    def test_rook_red_constraint(self):
        """test de la contrainte spéciale: s'arrêter à la première case rouge rencontrée"""
        # une tour doit s'arrêter à la première case rouge rencontrée
        
        # cas 1: case rouge vide - peut s'y arrêter, mais pas aller au-delà
        self.board[3][6] = [None, 0]  # case rouge vide
        self.assertTrue(available_move(self.board, 3, 3, 3, 6))  # test tour peut s'arrêter sur la première case rouge rencontrée
        self.assertFalse(available_move(self.board, 3, 3, 3, 7))  # test tour doit s'arrêter au maximum sur la première case rouge rencontrée
        
        # cas 2: case rouge occupée par pion adverse - peut capturer, mais pas aller au-delà
        self.board[3][6] = [1, 0]  # case rouge avec pion adverse
        self.assertTrue(available_move(self.board, 3, 3, 3, 6))  # test tour peut capturer un pion adverse sur une case rouge
        self.assertFalse(available_move(self.board, 3, 3, 3, 7))  # test tour doit toujours s'arrêter à la case rouge
        
        # cas 3: case rouge occupée par pion allié - ne peut pas s'y arrêter ni aller au-delà
        self.board[3][6] = [0, 0]  # case rouge avec pion allié
        self.assertFalse(available_move(self.board, 3, 3, 3, 6))  # test tour ne peut pas se déplacer sur une case occupée par un pion allié
        self.assertFalse(available_move(self.board, 3, 3, 3, 7))  # test tour ne peut pas aller au-delà
        
        # cas 4: deux cases rouges en ligne - s'arrête à la première
        self.board[3][6] = [None, 0]  # case rouge vide
        self.board[3][7] = [None, 0]  # case rouge vide plus loin
        self.assertTrue(available_move(self.board, 3, 3, 3, 6))  # test tour peut s'arrêter sur la première case rouge
        self.assertFalse(available_move(self.board, 3, 3, 3, 7))  # test tour ne peut pas atteindre la deuxième case rouge
        
        # nettoyage (voir modifications auparavant)
        self.board[3][6] = [None, None]
        self.board[3][7] = [None, None]
        
        # cas 5: case rouge dans une autre direction
        self.board[6][3] = [None, 0]  # case rouge vide verticale vers le bas
        self.assertTrue(available_move(self.board, 3, 3, 6, 3))  # test tour peut s'arrêter sur la première case rouge rencontrée
        self.assertFalse(available_move(self.board, 3, 3, 7, 3))  # test tour doit s'arrêter au maximum sur la première case rouge rencontrée
        
        # nettoyage (voir modifications auparavant)
        self.board[6][3] = [None, None]

if __name__ == "__main__":
    unittest.main() 