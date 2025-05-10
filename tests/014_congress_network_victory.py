from test_base import TestBase
from unittest.mock import patch, MagicMock

from src.congress.game import Game as CongressGame
from src.windows.render.render import Render
from src.network.client.client import NetworkClient
from src.windows.selector.config_loader import ConfigLoader


class TestCongressNetworkVictory(TestBase):
    """test pour vérifier l'envoi de paquets réseau lors d'une victoire dans congress"""
    
    def setUp(self):
        """initialise l'environnement de test avec les mocks nécessaires"""
        super().setUp()
        
        # configuration des quadrants
        self.config_loader = ConfigLoader()
        config_result = self.config_loader.load_quadrants()
        if not config_result:
            self.fail("Failed to load quadrants")
        
        self.quadrants_config, self.quadrant_names, _ = config_result
        first_quadrant_name = self.quadrant_names[0]
        self.selected_quadrants = [self.quadrants_config[first_quadrant_name] for _ in range(4)]
        
        # création des mocks pour isoler le test
        self.client_mock = MagicMock(spec=NetworkClient)
        self.render_mock = MagicMock(spec=Render)
        self.render_mock.running = True
        self.render_mock.needs_render = False
        
        # mock pour simuler le comportement de l'objet Render
        def mock_show_end_popup(winner_text):
            self.render_mock.end_popup_active = True
            self.render_mock.end_popup_text = winner_text
            self.render_mock.end_popup_buttons = []
            self.render_mock.needs_render = True
            # simule le comportement normal du jeu lorsque la popup est affichée
            self.render_mock.running = False
            
        self.render_mock.show_end_popup.side_effect = mock_show_end_popup
        
        # patch pour éviter la connexion réelle au serveur
        self.network_client_patch = patch('src.network.client.client.NetworkClient', return_value=self.client_mock)
        self.network_client_mock = self.network_client_patch.start()
        
        # patch pour éviter l'initialisation réelle du rendu
        self.render_patch = patch('src.congress.game.Render', return_value=self.render_mock)
        self.render_mock_class = self.render_patch.start()
        
        # patch pour éviter d'interagir avec pygame
        self.pygame_event_patch = patch('pygame.event.get', return_value=[])
        self.pygame_event_mock = self.pygame_event_patch.start()
        
        # patch pour les fonctions pygame d'affichage
        self.pygame_display_flip_patch = patch('pygame.display.flip')
        self.pygame_display_flip_mock = self.pygame_display_flip_patch.start()
        
        self.pygame_display_update_patch = patch('pygame.display.update')
        self.pygame_display_update_mock = self.pygame_display_update_patch.start()
        
        # patch pour éviter l'erreur de chargement de font
        self.font_mock = MagicMock()
        self.pygame_font_patch = patch('pygame.font.Font', return_value=self.font_mock)
        self.pygame_font_mock = self.pygame_font_patch.start()
        
        # patch de pygame.Surface pour éviter les erreurs de rendu
        self.surface_mock = MagicMock()
        self.surface_mock.blit = MagicMock()
        self.pygame_surface_patch = patch('pygame.Surface', return_value=self.surface_mock)
        self.pygame_surface_mock = self.pygame_surface_patch.start()
        
    def tearDown(self):
        """nettoie les ressources utilisées par le test"""
        self.network_client_patch.stop()
        self.render_patch.stop()
        self.pygame_event_patch.stop()
        self.pygame_display_flip_patch.stop()
        self.pygame_display_update_patch.stop()
        self.pygame_font_patch.stop()
        self.pygame_surface_patch.stop()
        super().tearDown()
    
    @patch('src.saves.save_game')
    def test_congress_network_victory_packet(self, mock_save_game):
        """vérifie qu'un paquet réseau est envoyé lors d'une victoire par connexion des pièces"""
        # désactive la méthode de rendu du mock pour éviter les erreurs
        self.render_mock.render_board = MagicMock()
        
        # crée le jeu en mode réseau avec l'initialisation du plateau moquée
        with patch('src.congress.game.Board'):
            game = CongressGame("dev_congress", self.selected_quadrants, "Network")
            
            # s'assure que la classe Render a bien été moquée
            self.assertIs(game.render, self.render_mock)
            
            # configure le jeu pour le réseau
            game.is_network_game = True
            game.network_client = self.client_mock
            game.player_number = 1
            game.is_my_turn = True
            game.game_started = True
            game.local_player_name = "TestPlayer"
            
            # réinitialise le mock pour garantir un état propre pour les assertions
            self.client_mock.reset_mock()
            
            # force le client à un état de connexion correct pour l'envoi
            self.client_mock.is_connected = True
            self.client_mock.connected_to_game = True
            
            # initialise le plateau manuellement
            game.board = MagicMock()
            game.board.board = [[None for _ in range(8)] for _ in range(8)]
            for r in range(8):
                for c in range(8):
                    game.board.board[r][c] = [None, 0]  # [joueur, type_case]
            
            # configure la situation de test
            self.setup_test_board(game)
            
            # les coordonnées source et destination pour le mouvement gagnant
            source_row, source_col = 5, 4  # position de la pièce séparée
            dest_row, dest_col = 4, 4      # position qui connecterait toutes les pièces
            
            # mock pour rendre available_move toujours vrai
            with patch('src.moves.available_move', return_value=True):
                # patch check_connected_pieces pour simuler une victoire
                with patch.object(CongressGame, 'check_connected_pieces', return_value=True):
                    # définie la sélection de pièce manuellement
                    game.selected_piece = (source_row, source_col)
                    
                    # reset le mock pour vérifier l'appel spécifique après le mouvement
                    self.client_mock.reset_mock()
                    
                    # simule un clic sur la destination pour effectuer le mouvement
                    game.on_click(dest_row, dest_col)
                    
                    # vérifie que le client a tenté d'envoyer un paquet réseau
                    self.client_mock.send_game_action.assert_called_once()
                    
                    # vérifie le contenu du paquet envoyé
                    call_args = self.client_mock.send_game_action.call_args[0][0]
                    self.assertEqual(call_args["from_row"], source_row)
                    self.assertEqual(call_args["from_col"], source_col)
                    self.assertEqual(call_args["to_row"], dest_row)
                    self.assertEqual(call_args["to_col"], dest_col)
                    
                    # vérifie que le jeu s'est arrêté après la victoire
                    self.assertTrue(hasattr(game.render, 'end_popup_active') and game.render.end_popup_active, "Popup should be active after victory")
    
    def setup_test_board(self, game):
        """configure un plateau de test avec des pièces presque connectées"""
        # place des pièces du joueur 1 (index 0) qui sont presque connectées
        game.board.board[2][2][0] = 0  # pièce en (2,2)
        game.board.board[2][3][0] = 0  # pièce en (2,3)
        game.board.board[2][4][0] = 0  # pièce en (2,4)
        game.board.board[3][4][0] = 0  # pièce en (3,4)
        game.board.board[5][4][0] = 0  # pièce en (5,4) - séparée


if __name__ == "__main__":
    import unittest
    unittest.main() 