from test_base import TestBase
from unittest.mock import patch, MagicMock

from src.congress.game import Game as CongressGame
from src.windows.render.render import Render
from src.utils.logger import Logger
from src.saves import load_game
from src.windows.selector.config_loader import ConfigLoader
from src.moves import available_move


class TestCongressVictory(TestBase):
    """Test pour vérifier la condition de victoire dans Congress"""
    
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
    def test_congress_winning_move(self, mock_update, mock_flip):
        """Test si le coup gagnant dans dev_congress.json déclenche la victoire"""
        # crée une instance de jeu avec la configuration des quadrants
        game = CongressGame("dev_congress", self.selected_quadrants, "Solo")
        
        # crée un mock de Render pour simuler le comportement de l'interface : 
        # on peut suivre les appels aux méthodes de l'objet Render
        # le mock permet aussi de vérifier que les méthodes sont appelées avec les bons paramètres 
        # et de simuler le comportement de l'objet Render
        mock_render = MagicMock(spec=Render)
        mock_render.running = True 
        mock_render.needs_render = False  
        
        # mock pour simuler le comportement de l'objet Render
        def mock_show_end_popup(winner_text):
            mock_render.end_popup_active = True
            mock_render.end_popup_text = winner_text
            mock_render.end_popup_buttons = []
            mock_render.needs_render = True
            mock_render.running = False
            
        mock_render.show_end_popup.side_effect = mock_show_end_popup
        
        game.render = mock_render  # remplace le render réel par notre mock
        
        # charge le fichier de sauvegarde (initialise l'état du plateau)
        self.assertTrue(load_game(game), "Failed to load dev_congress.json save file")
        
        # vérifie que c'est le tour du joueur 1 (player 0 dans la représentation du code)
        self.assertEqual(game.round_turn, 0, "Test expects player 1's turn (round_turn=0)")
        
        # dans Congress, le joueur gagne en connectant toutes ses pièces
        # normalement dans dev_congress.json, il devrait y avoir un coup gagnant pour le joueur 1
        
        # d'abord, trouvons toutes les pièces du joueur 1
        player1_pieces = []
        for r in range(8):
            for c in range(8):
                if game.board.board[r][c][0] == 0:  # vérifie si c'est la pièce du joueur 1
                    player1_pieces.append((r, c))
        
        # il devrait y avoir au moins une pièce
        self.assertGreater(len(player1_pieces), 0, "Expected at least one piece for player 1")
        
        valid_move = None
        source_piece = None
        
        # vérifie toutes les cellules vides comme coups potentiels et toutes les pièces existantes comme source
        for r in range(8):
            for c in range(8):
                if game.board.board[r][c][0] is None:  # cellule vide (destination potentielle)
                    # cherche une pièce du joueur 1 qui peut se déplacer vers cette cellule
                    for piece_r, piece_c in player1_pieces:
                        if available_move(game.board.board, piece_r, piece_c, r, c):
                            # simule le mouvement pour vérifier s'il connecterait toutes les pièces
                            game.board.board[r][c][0] = 0  # place la pièce du joueur 1
                            game.board.board[piece_r][piece_c][0] = None  # retire la pièce de sa position d'origine
                            
                            # vérifie si cela crée une condition de victoire
                            if game.check_connected_pieces(0):
                                valid_move = (r, c)
                                source_piece = (piece_r, piece_c)
                                # restaure l'état du plateau
                                game.board.board[r][c][0] = None
                                game.board.board[piece_r][piece_c][0] = 0
                                break
                            
                            # restaure l'état du plateau
                            game.board.board[r][c][0] = None
                            game.board.board[piece_r][piece_c][0] = 0
                    
                    if valid_move:
                        break
            
            if valid_move:
                break
                
        # s'assure qu'on a trouvé un coup gagnant
        self.assertIsNotNone(valid_move, "Could not find a winning move for player 1")
        self.assertIsNotNone(source_piece, "Could not identify source piece for winning move")
        
        s_row, s_col = source_piece
        d_row, d_col = valid_move
        Logger.info("Test", f"Found winning move: piece at ({s_row}, {s_col}) to position ({d_row}, {d_col}) that connects all pieces")
        
        # sélectionne la pièce source
        self.assertTrue(game.on_click(s_row, s_col), "Selecting source piece should succeed")
        # déplace la pièce à la destination gagnante
        self.assertFalse(game.on_click(d_row, d_col), "Moving to winning position should end the game")
        
        # vérifie que la pièce a été déplacée à la position gagnante
        self.assertEqual(game.board.board[d_row][d_col][0], 0, "La pièce du joueur 1 devrait être à la position gagnante")
        
        # s'assure que la victoire a été détectée par le jeu lui-même
        self.assertTrue(hasattr(game.render, 'end_popup_active') and game.render.end_popup_active, "Popup should be active after victory")
        
        # vérifie que check_win retourne True pour le joueur 1 (index 0)
        self.assertTrue(game.check_connected_pieces(0), "check_connected_pieces devrait retourner True pour le joueur 1 après le coup gagnant")


if __name__ == "__main__":
    import unittest
    unittest.main() 