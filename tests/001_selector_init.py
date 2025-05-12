from test_base import TestBase

from src.windows.selector.selector import Selector
from src.windows.selector.quadrant_handler import QuadrantHandler
from src.windows.selector.config_loader import ConfigLoader
from src.windows.selector.game_launcher import GameLauncher

class TestSelectorInit(TestBase):
    def setUp(self):
        super().setUp()
        self.original_main_loop = Selector.main_loop # sauvegarde la méthode main_loop originale
        Selector.main_loop = TestSelectorInit.mock_main_loop # remplace la méthode main_loop par une méthode qui ne fait rien
        
    @staticmethod
    def mock_main_loop(selector_instance):
        # permet de ne pas lancer la boucle principale de l'application
        # pour ne pas afficher les fenêtres pygame
        pass
        
    def tearDown(self):
        Selector.main_loop = self.original_main_loop
        super().tearDown()
    
    def test_selector_initialization(self):
        selector = Selector()
        
        self.assertIsNotNone(selector.quadrant_handler) # vérifie que le quadrant_handler est bien instancié
        self.assertIsInstance(selector.quadrant_handler, QuadrantHandler) # vérifie que le quadrant_handler est bien une instance de QuadrantHandler
        
        self.assertIsNotNone(selector.config_loader) # vérifie que le config_loader est bien instancié
        self.assertIsInstance(selector.config_loader, ConfigLoader) # vérifie que le config_loader est bien une instance de ConfigLoader
        
        self.assertIsNotNone(selector.game_launcher) # vérifie que le game_launcher est bien instancié
        self.assertIsInstance(selector.game_launcher, GameLauncher) # vérifie que le game_launcher est bien une instance de GameLauncher
        
        self.assertIsNotNone(selector.screen) # vérifie que la fenêtre pygame est bien instanciée
        self.assertIsNotNone(selector.clock) # vérifie que le clock est bien instancié
        
        self.assertFalse(selector.running) # vérifie que la boucle principale est bien arrêtée
        self.assertTrue(selector.outer_running) # vérifie que la boucle principale est bien en cours
        
        self.assertIsNotNone(selector.quadrants_config) # vérifie que les quadrants sont bien configurés
        self.assertIsNotNone(selector.quadrant_names) # vérifie que les noms des quadrants sont bien configurés
        self.assertEqual(len(selector.selected_quadrants), 4) # vérifie que les quadrants sélectionnés sont bien 4

if __name__ == "__main__":
    import unittest
    unittest.main() 