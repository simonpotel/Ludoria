from test_base import TestBase
import unittest
from src.moves import available_move

class TestYellowBishopMovement(TestBase):
    """Test du mouvement d'un pion situé sur une case jaune (mouvement de fou avec règle spéciale)"""
    
    def setUp(self):
        super().setUp()
        
        # voir src/board.py pour les couleurs des cases
        # les cases contiennent [joueur, couleur]
        # 0 = rouge, 1 = verte, 2 = bleue, 3 = jaune (marron)
        self.board = [
            [[None, None] for _ in range(8)] for _ in range(8)
        ]
        
        self.board[4][4] = [0, 3]  # joueur 0, case jaune
    
    def test_bishop_directions(self):
        """test des mouvements valides en diagonale"""
        # un fou se déplace en diagonale
        self.assertTrue(available_move(self.board, 4, 4, 3, 3))  # test fou peut se déplacer en diagonale haut-gauche
        self.assertTrue(available_move(self.board, 4, 4, 5, 5))  # test fou peut se déplacer en diagonale bas-droite
        self.assertTrue(available_move(self.board, 4, 4, 3, 5))  # test fou peut se déplacer en diagonale haut-droite
        self.assertTrue(available_move(self.board, 4, 4, 5, 3))  # test fou peut se déplacer en diagonale bas-gauche
        
        # un fou peut se déplacer de plusieurs cases en diagonale
        self.assertTrue(available_move(self.board, 4, 4, 2, 2))  # test fou peut se déplacer de deux cases en diagonale haut-gauche
        self.assertTrue(available_move(self.board, 4, 4, 6, 6))  # test fou peut se déplacer de deux cases en diagonale bas-droite
        self.assertTrue(available_move(self.board, 4, 4, 2, 6))  # test fou peut se déplacer de deux cases en diagonale haut-droite
        self.assertTrue(available_move(self.board, 4, 4, 6, 2))  # test fou peut se déplacer de deux cases en diagonale bas-gauche
    
    def test_bishop_invalid_moves(self):
        """test des mouvements non valides"""
        # un fou ne peut pas se déplacer autrement qu'en diagonale
        self.assertFalse(available_move(self.board, 4, 4, 4, 5))  # test fou ne peut pas se déplacer horizontalement
        self.assertFalse(available_move(self.board, 4, 4, 5, 4))  # test fou ne peut pas se déplacer verticalement
        self.assertFalse(available_move(self.board, 4, 4, 4, 6))  # test fou ne peut pas se déplacer horizontalement de deux cases
        self.assertFalse(available_move(self.board, 4, 4, 6, 4))  # test fou ne peut pas se déplacer verticalement de deux cases
        self.assertFalse(available_move(self.board, 4, 4, 3, 6))  # test fou ne peut pas se déplacer en L
    
    def test_bishop_obstacles(self):
        """test des obstacles sur le trajet diagonal"""
        # test de capture d'un pion adverse sur une case directement adjacente
        self.board[5][5] = [1, 2]  # joueur 1, case bleue directement à côté
        self.assertTrue(available_move(self.board, 4, 4, 5, 5))  # test fou peut capturer un pion adverse adjacent
        
        # test de capture d'un pion adverse sur une case plus éloignée
        self.board[5][5] = [None, None]  # annule les changements précédents
        self.board[6][6] = [1, 2]  # joueur 1, case bleue plus loin
        self.assertTrue(available_move(self.board, 4, 4, 6, 6))  # test fou peut capturer un pion adverse plus loin
        
        # un fou ne peut pas sauter par-dessus d'autres pièces 
        self.board[5][5] = [1, 2]  # joueur 1, case bleue (obstacle)
        self.assertTrue(available_move(self.board, 4, 4, 5, 5))  # test fou peut capturer un pion adverse
        self.assertFalse(available_move(self.board, 4, 4, 6, 6))  # test fou ne peut pas sauter par-dessus d'autres pièces
        
        # un fou ne peut pas se déplacer sur une case occupée par un pion du même joueur
        self.board[5][5] = [None, None]  # nettoie
        self.board[3][3] = [0, 2]  # joueur 0, case bleue (allié)
        self.assertFalse(available_move(self.board, 4, 4, 3, 3))  # test fou ne peut pas se déplacer sur une case occupée par un pion allié
        
        self.board[3][3] = [None, None]  # nettoie
        self.board[6][6] = [None, None]  # nettoie
    
    def test_bishop_yellow_constraint(self):
        """test de la contrainte spéciale: s'arrêter à la première case jaune rencontrée"""
        # un fou doit s'arrêter à la première case jaune rencontrée
        
        # cas 1: case jaune vide - peut s'y arrêter, mais pas aller au-delà
        self.board[6][6] = [None, 3]  # case jaune vide
        self.assertTrue(available_move(self.board, 4, 4, 6, 6))  # test fou peut s'arrêter sur la première case jaune rencontrée
        self.assertFalse(available_move(self.board, 4, 4, 7, 7))  # test fou doit s'arrêter au maximum sur la première case jaune rencontrée
        
        # cas 2: case jaune occupée par pion adverse - peut capturer, mais pas aller au-delà
        self.board[6][6] = [1, 3]  # case jaune avec pion adverse
        self.assertTrue(available_move(self.board, 4, 4, 6, 6))  # test fou peut capturer un pion adverse sur une case jaune
        self.assertFalse(available_move(self.board, 4, 4, 7, 7))  # test fou doit toujours s'arrêter à la case jaune
        
        # cas 3: case jaune occupée par pion allié - ne peut pas s'y arrêter ni aller au-delà
        self.board[6][6] = [0, 3]  # case jaune avec pion allié
        self.assertFalse(available_move(self.board, 4, 4, 6, 6))  # test fou ne peut pas se déplacer sur une case occupée par un pion allié
        self.assertFalse(available_move(self.board, 4, 4, 7, 7))  # test fou ne peut pas aller au-delà
        
        # cas 4: deux cases jaunes en ligne - s'arrête à la première
        self.board[6][6] = [None, 3]  # case jaune vide
        self.board[7][7] = [None, 3]  # case jaune vide plus loin
        self.assertTrue(available_move(self.board, 4, 4, 6, 6))  # test fou peut s'arrêter sur la première case jaune
        self.assertFalse(available_move(self.board, 4, 4, 7, 7))  # test fou ne peut pas atteindre la deuxième case jaune
        
        # nettoyage (voir modifications auparavant)
        self.board[6][6] = [None, None]
        self.board[7][7] = [None, None]
        
        # cas 5: case jaune dans une autre direction diagonale
        self.board[2][6] = [None, 3]  # case jaune vide diagonale haut-droite
        self.assertTrue(available_move(self.board, 4, 4, 2, 6))  # test fou peut s'arrêter sur la première case jaune rencontrée
        self.assertFalse(available_move(self.board, 4, 4, 1, 7))  # test fou doit s'arrêter au maximum sur la première case jaune rencontrée
        
        self.board[2][6] = [None, None]

if __name__ == "__main__":
    unittest.main() 