from test_base import TestBase
from unittest.mock import patch, MagicMock

from src.katerenga.game import Game as KaterengaGame
from src.windows.render.render import Render
from src.utils.logger import Logger
from src.saves import load_game
from src.windows.selector.config_loader import ConfigLoader
from src.moves import available_move


class TestKaterengaVictory(TestBase):
    """Test pour vérifier la condition de victoire dans Katerenga"""
    
    def setUp(self):
        """Setup test en initialisant la configuration des quadrants"""
        super().setUp()  # appelle le setUp de la classe parente
        self.config_loader = ConfigLoader()  # initialise le chargeur de configuration
        config_result = self.config_loader.load_quadrants()  # charge les quadrants
        if not config_result:
            # échec si la configuration n'est pas chargée
            self.fail("Failed to load quadrants configuration")

        # décompose la configuration
        self.quadrants_config, self.quadrant_names, _ = config_result
        # prend le premier quadrant pour tous les emplacements par simplicité
        first_quadrant_name = self.quadrant_names[0]
        self.selected_quadrants = [self.quadrants_config[first_quadrant_name] for _ in range(4)]

    @patch('pygame.display.flip')  # mock pour éviter les erreurs d'affichage pygame
    @patch('pygame.display.update')  # mock pour éviter les erreurs d'affichage pygame
    def test_katerenga_winning_move(self, mock_update, mock_flip):
        """Test si le coup gagnant dans dev_katerenga.json déclenche la victoire"""
        # crée une instance de jeu avec la configuration des quadrants
        game = KaterengaGame("dev_katerenga", self.selected_quadrants, "Solo")

        # crée un mock de Render pour simuler le comportement de l'interface : 
        # on peut suivre les appels aux méthodes de l'objet Render
        # le mock permet aussi de vérifier que les méthodes sont appelées avec les bons paramètres 
        # et de simuler le comportement de l'objet Render
        mock_render = MagicMock(spec=Render)
        mock_render.running = True 
        mock_render.needs_render = False  
        game.render = mock_render  # remplace le render réel par notre mock

        # charge le fichier de sauvegarde (initialise l'état du plateau)
        self.assertTrue(load_game(game), "Failed to load dev_katerenga.json save file")
        
        # vérifie que c'est le tour du joueur 1 (player 0 dans la représentation du code)
        self.assertEqual(game.round_turn, 0, "Test expects player 1's turn (round_turn=0)")
        
        # vérifie les positions des camps dans ce type de jeu
        self.assertEqual(game.camps, [(0, 0), (0, 9), (9, 0), (9, 9)], "Expected camps at corners")
        
        # vérifie que le joueur 1 (index 0) a déjà une pièce à la position (9,0)
        self.assertEqual(game.board.board[9][0][0], 0, "Expected player 1's piece at position (9,0)")

        # cherche une pièce du joueur 1 (index 0) qui peut se déplacer à (9,9)
        valid_source_pos = None
        for r in range(10):  # parcourt toutes les lignes du plateau
            for c in range(10):  # parcourt toutes les colonnes du plateau
                if game.board.board[r][c][0] == 0:  # vérifie si c'est la pièce du joueur 1
                    if available_move(game.board.board, r, c, 9, 9):  # vérifie si cette pièce peut se déplacer à (9,9)
                        valid_source_pos = (r, c)
                        break
            if valid_source_pos:
                break

        # vérifie que nous avons trouvé une pièce valide qui peut se déplacer à (9,9)
        self.assertIsNotNone(valid_source_pos, "Could not find any player 1 piece that can move to camp (9,9)")
        
        source_r, source_c = valid_source_pos
        Logger.info("Test", f"Found valid piece at ({source_r}, {source_c}) that can move to (9,9)")

        # fait le coup qui déclenche la victoire
        game.on_click(source_r, source_c)  # sélectionne la pièce
        game.on_click(9, 9)  # puis déplace la pièce à (9,9)

        # vérifie que la pièce a été déplacée à la position gagnante
        self.assertEqual(game.board.board[9][9][0], 0, "La pièce du joueur 1 devrait maintenant être à (9,9)")

        # vérifie que la victoire a été détectée
        self.assertFalse(game.render.running, "Le jeu devrait s'arrêter après la victoire")
        
        # vérifie que check_win retourne True pour le joueur 1 (index 0)
        self.assertTrue(game.check_win(0), "check_win devrait retourner True pour le joueur 1 après le coup gagnant")


if __name__ == "__main__":
    import unittest
    unittest.main()
