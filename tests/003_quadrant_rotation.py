import copy
from test_base import TestBase

from src.windows.selector.quadrant_handler import QuadrantHandler

class TestQuadrantRotation(TestBase):
    def setUp(self):
        super().setUp() # initialise les variables d'instance
        self.quadrant_handler = QuadrantHandler() # initialise le quadrant_handler
        
        self.test_quadrant = [
            [(None, 0), (None, 1), (None, 2), (None, 3)],
            [(None, 0), (None, 1), (None, 2), (None, 3)],
            [(None, 0), (None, 1), (None, 2), (None, 3)],
            [(None, 0), (None, 1), (None, 2), (None, 3)]
        ] # initialise le quadrant de test
        
        self.selected_quadrants = [copy.deepcopy(self.test_quadrant) for _ in range(4)] # initialise les quadrants sélectionnés
    
    def test_rotate_right(self):
        index = 0 # index du quadrant à tester
        original_quadrant_at_index = copy.deepcopy(self.selected_quadrants[index])

        # test de la rotation à droite
        rotated_quadrants = self.quadrant_handler.rotate_right(self.selected_quadrants, index) # tourne le quadrant à droite
        
        # résultat attendu après une rotation à droite
        expected_after_one_rotation = [
            [original_quadrant_at_index[3][0], original_quadrant_at_index[2][0], original_quadrant_at_index[1][0], original_quadrant_at_index[0][0]],
            [original_quadrant_at_index[3][1], original_quadrant_at_index[2][1], original_quadrant_at_index[1][1], original_quadrant_at_index[0][1]],
            [original_quadrant_at_index[3][2], original_quadrant_at_index[2][2], original_quadrant_at_index[1][2], original_quadrant_at_index[0][2]],
            [original_quadrant_at_index[3][3], original_quadrant_at_index[2][3], original_quadrant_at_index[1][3], original_quadrant_at_index[0][3]],
        ]
        self.assertEqual(rotated_quadrants[index], expected_after_one_rotation, "Quadrant not rotated right correctly after one rotation")

        # vérifie que les autres quadrants restent inchangés
        for i in range(len(self.selected_quadrants)):
            if i != index:
                self.assertEqual(rotated_quadrants[i], self.selected_quadrants[i], f"Quadrant at index {i} should not have changed")

        # test de la rotation à droite
        current_quadrants = copy.deepcopy(self.selected_quadrants)
        for _ in range(4):
            current_quadrants = self.quadrant_handler.rotate_right(current_quadrants, index)
        
        self.assertEqual(current_quadrants[index], original_quadrant_at_index, "Quadrant should return to original state after 4 right rotations")
    
    def test_rotate_left(self):
        index = 1 # index du quadrant à tester
        original_quadrant_at_index = copy.deepcopy(self.selected_quadrants[index])

        # test de la rotation à gauche
        rotated_quadrants = self.quadrant_handler.rotate_left(self.selected_quadrants, index) # tourne le quadrant à gauche

        # résultat attendu après une rotation à gauche
        expected_after_one_rotation = [
            [original_quadrant_at_index[0][3], original_quadrant_at_index[1][3], original_quadrant_at_index[2][3], original_quadrant_at_index[3][3]],
            [original_quadrant_at_index[0][2], original_quadrant_at_index[1][2], original_quadrant_at_index[2][2], original_quadrant_at_index[3][2]],
            [original_quadrant_at_index[0][1], original_quadrant_at_index[1][1], original_quadrant_at_index[2][1], original_quadrant_at_index[3][1]],
            [original_quadrant_at_index[0][0], original_quadrant_at_index[1][0], original_quadrant_at_index[2][0], original_quadrant_at_index[3][0]],
        ]
        self.assertEqual(rotated_quadrants[index], expected_after_one_rotation, "Quadrant not rotated left correctly after one rotation")

        # vérifie que les autres quadrants restent inchangés
        for i in range(len(self.selected_quadrants)):
            if i != index:
                self.assertEqual(rotated_quadrants[i], self.selected_quadrants[i], f"Quadrant at index {i} should not have changed")

        # test de la rotation à gauche
        current_quadrants = copy.deepcopy(self.selected_quadrants)
        for _ in range(4):
            current_quadrants = self.quadrant_handler.rotate_left(current_quadrants, index)
        
        self.assertEqual(current_quadrants[index], original_quadrant_at_index, "Quadrant should return to original state after 4 left rotations")
    
    def test_multiple_quadrant_rotations(self):
        for index in range(4):
            rotated = self.quadrant_handler.rotate_right(self.selected_quadrants, index) # tourne le quadrant à droite
            self.assertNotEqual(rotated[index], self.selected_quadrants[index]) # vérifie que le quadrant est bien tourné à droite
             
            for other_index in range(4):
                if other_index != index:
                    self.assertEqual(rotated[other_index], self.selected_quadrants[other_index])

if __name__ == "__main__":
    import unittest
    unittest.main() 