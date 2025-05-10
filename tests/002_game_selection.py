from test_base import TestBase

from src.windows.selector.selector import Selector
from src.windows.components import Dropdown

class TestGameSelection(TestBase):
    def setUp(self):
        super().setUp()
        self.original_main_loop = Selector.main_loop # sauvegarde la méthode main_loop originale
        Selector.main_loop = TestGameSelection.mock_main_loop # remplace la méthode main_loop par une méthode qui ne fait rien
        
        self.original_setup_ui = Selector.setup_ui # sauvegarde la méthode setup_ui originale
        Selector.setup_ui = TestGameSelection.mock_setup_ui # remplace la méthode setup_ui par une méthode qui ne fait rien
        
        self.selector = Selector() # initialise le selector
        self.selector.game_selection = Dropdown(0, 0, 200, 30, self.selector.GAMES, 0) # initialise le dropdown avec les jeux disponibles
        
    @staticmethod
    def mock_main_loop(selector_instance):
        # permet de ne pas lancer la boucle principale de l'application
        # pour ne pas afficher les fenêtres pygame
        pass
    
    @staticmethod
    def mock_setup_ui(self, selector):
        # permet de ne pas afficher les fenêtres pygame
        # pour ne pas afficher les fenêtres pygame
        pass
    
    def tearDown(self):
        Selector.main_loop = self.original_main_loop # restaure la méthode main_loop originale
        Selector.setup_ui = self.original_setup_ui # restaure la méthode setup_ui originale
        super().tearDown() # restaure les variables d'instance
    
    def test_game_selection_dropdown(self):
        dropdown = self.selector.game_selection # récupère le dropdown
        
        self.assertEqual(dropdown.options, ["katerenga", "isolation", "congress"]) # vérifie que les options du dropdown sont bien les jeux disponibles
        self.assertEqual(dropdown.selected_index, 0) # vérifie que le dropdown est bien sélectionné sur le premier jeu
        self.assertEqual(dropdown.get(), "katerenga") # vérifie que le dropdown est bien sélectionné sur le premier jeu
        
        dropdown.selected_index = 1 # sélectionne le deuxième jeu
        self.assertEqual(dropdown.get(), "isolation") # vérifie que le dropdown est bien sélectionné sur le deuxième jeu
        
        dropdown.selected_index = 2 # sélectionne le troisième jeu
        self.assertEqual(dropdown.get(), "congress") # vérifie que le dropdown est bien sélectionné sur le troisième jeu
        
        dropdown.selected_index = 0 # sélectionne le premier jeu
        self.assertEqual(dropdown.get(), "katerenga") # vérifie que le dropdown est bien sélectionné sur le premier jeu
    
    def test_game_selection_change(self):
        dropdown = self.selector.game_selection # récupère le dropdown
        
        for i, game in enumerate(self.selector.GAMES):
            dropdown.selected_index = i # sélectionne le jeu i
            self.assertEqual(dropdown.get(), game) # vérifie que le dropdown est bien sélectionné sur le jeu i
            self.assertEqual(dropdown.selected_index, i) # vérifie que le dropdown est bien sélectionné sur le jeu i

if __name__ == "__main__":
    import unittest
    unittest.main() 