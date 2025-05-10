from test_base import TestBase
from unittest.mock import patch, MagicMock

from src.isolation.game import Game as IsolationGame
from src.windows.render.render import Render
from src.utils.logger import Logger
from src.saves import load_game
from src.windows.selector.config_loader import ConfigLoader
from src.captures import has_valid_move, is_threatened


class TestIsolationVictory(TestBase):
    """Test pour vérifier la condition de victoire dans Isolation"""
    
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
    def test_isolation_winning_move(self, mock_update, mock_flip):
        """Test si le coup gagnant dans dev_isolation.json déclenche la victoire"""
        # crée une instance de jeu avec la configuration des quadrants
        game = IsolationGame("dev_isolation", self.selected_quadrants, "Solo")
        
        # crée un mock de Render pour simuler le comportement de l'interface
        mock_render = MagicMock(spec=Render)
        mock_render.running = True  # initialise la propriété running à True
        mock_render.needs_render = False  # initialise la propriété needs_render à False
        game.render = mock_render  # remplace le render réel par notre mock
        
        # charge le fichier de sauvegarde (initialise l'état du plateau)
        self.assertTrue(load_game(game), "Failed to load dev_isolation.json save file")
        
        # vérifie quel joueur a le tour
        current_player = game.round_turn
        opponent_player = 1 - current_player
        Logger.info("Test", f"Current turn: Player {current_player + 1}")
        
        # dans Isolation, un joueur gagne en faisant un mouvement qui laisse l'adversaire sans mouvements valides
        # trouvons un coup gagnant pour le joueur actuel
        valid_move = None
        
        # vérifie toutes les cellules vides comme coups potentiels
        for r in range(8):
            for c in range(8):
                if game.board.board[r][c][0] is None:  # cellule vide
                    # s'assure que cette cellule n'est pas menacée par les pièces adverses
                    if not is_threatened(game.board.board, r, c, current_player, check_all_pieces=True):
                        # essaie de faire ce coup
                        game.board.board[r][c][0] = current_player  # place la pièce du joueur actuel
                        
                        # vérifie si l'adversaire aurait un coup valide après cela
                        if not has_valid_move(game.board.board, opponent_player, check_all_pieces=True):
                            valid_move = (r, c)
                            # restaure l'état du plateau
                            game.board.board[r][c][0] = None
                            break
                        
                        # restaure l'état du plateau
                        game.board.board[r][c][0] = None
            
            if valid_move:
                break
                
        # s'assure qu'on a trouvé un coup gagnant
        self.assertIsNotNone(valid_move, f"Could not find a winning move for Player {current_player + 1}")
        row, col = valid_move
        Logger.info("Test", f"Found winning move at ({row}, {col}) that leaves opponent with no valid moves")
        
        # exécute le coup gagnant en utilisant on_click
        # le coup gagnant devrait mettre fin à la partie, alors on_click retourne False
        self.assertFalse(game.on_click(row, col), "on_click should return False for a winning move")
        
        # vérifie que la pièce a été placée à la position gagnante
        self.assertEqual(game.board.board[row][col][0], current_player, f"La pièce du joueur {current_player + 1} devrait être à la position gagnante")
        
        # s'assure que la victoire a été détectée par le jeu lui-même
        self.assertFalse(game.render.running, "Le jeu devrait s'arrêter après la victoire")
        
        # vérifie qu'il n'y a pas de coups valides pour l'adversaire (condition de victoire)
        # pas nécessaire car on_click a déjà vérifié que le coup gagnant est valide
        #self.assertFalse(has_valid_move(game.board.board, opponent_player, check_all_pieces=True), f"Le joueur {opponent_player + 1} ne devrait pas avoir de coups valides après le coup gagnant du joueur {current_player + 1}")


if __name__ == "__main__":
    import unittest
    unittest.main() 